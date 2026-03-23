#!/sr/bin/env python3
import bluetooth
import struct
import time
import curses
import sys
import RPi.GPIO as GPIO

#----------GPIO Setup for Sync Button Relay Control---------
GPIO.setmode(GPIO.BCM)
GPIO_PIN = 4
GPIO.setup(GPIO_PIN, GPIO.OUT)

GPIO.output(GPIO_PIN, GPIO.HIGH)
time.sleep(1.0)
GPIO.outut(GPIO_PIN, GPIO.LOW)

# Wii Balance Board Constants
BT_NAME = "Nintendo RVL-WBC-01"
INPUT_REPORT_ID = 0x32

# Button bit mask (not really needed for scale usage)
BUTTON_DOWN_MASK = 0x08

# Calibration container
class Calibration:
    def __init__(self):
        self.kg0 = [0, 0, 0, 0]
        self.kg17 = [0, 0, 0, 0]
        self.kg34 = [0, 0, 0, 0]

# Main class for reading from the board
class WiiBoard:
    def _set_led(self, on=True):
        # 0x11 = set LED command
        self._send(
            self.control_socket,
            b'\x11' + (b'\x10' if on else b'\x00')
        )

    def __init__(self):
        self.calibration = Calibration()
        self.control_socket = None
        self.data_socket = None
        self.weight = 0.0

    def find_board(self):
        print("Searching for Wii Balance Board...")
        nearby = bluetooth.discover_devices(duration=6, lookup_names=True)
        for addr, name in nearby:
            if name == BT_NAME:
                print(f"Found board at {addr}")
                return addr
        raise RuntimeError("Balance board not found.")

    def connect(self, addr):
        print("Connecting...")

        # Control channel (11)
        self.control_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.control_socket.connect((addr, 0x11))

        # Data channel (13)
        self.data_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.data_socket.connect((addr, 0x13))
        self.data_socket.settimeout(5.0)
        self._initialize_board()

    def _initialize_board(self):
    # Turn on LED (this "wakes" the board)
        self._set_led(True)
        time.sleep(0.2)

    # Enable continuous reporting
        # 0x12 = set report mode
        # 0x00 = continuous
        # 0x32 = balance board data
        self._send(self.control_socket, b'\x12\x00\x32')
        time.sleep(0.2)

        # NOW calibration will work
        self._get_calibration()

    def _send(self, sock, data):
        sock.send(bytes(data))

    def _read(self):
        return self.data_socket.recv(1024)

    def _get_calibration(self):
        # Request calibration data from Wii Balance Board memory
        # Address: 0x04A40024, Length: 24 bytes
        self._send(
            self.control_socket,
            b'\x17\x04\xa4\x00\x24\x00\x18'
        )

        data = b''
        while len(data) < 24:
            packet = self._read()

            # Calibration data packets start with 0x21
            if packet[0] == 0x21:
                    data += packet[7:7 + packet[6]]

        # Now we *guarantee* we have enough bytes
        cal = struct.unpack(">HHHHHHHHHHHH", data[:24])

        self.calibration.kg0  = cal[0:4]
        self.calibration.kg17 = cal[4:8]
        self.calibration.kg34 = cal[8:12]

        print("Calibration loaded")

    def read_weight(self):
        data = self._read()

        if data[0] != INPUT_REPORT_ID:
            return self.weight

        # Four corner sensor raw values:
        # bytes 7-14 (2 bytes each)
        raw = struct.unpack(">HHHH", data[7:15])
        tl, tr, bl, br = raw

        w = self._kg_from_raw(raw)
        self.weight = w
        return w

    def _interp(self, val, c0, c17, c34):
        """Converts raw ADC to kg using 3-point calibration."""
        if val < c17:
            return 17.0 * (val - c0) / (c17 - c0)
        else:
            return 17.0 + 17.0 * (val - c17) / (c34 - c17)


    def _kg_from_raw(self, raw):
        tl, tr, bl, br = raw
        c = self.calibration
        w_tl = self._interp(tl, c.kg0[0], c.kg17[0], c.kg34[0])
        w_tr = self._interp(tr, c.kg0[1], c.kg17[1], c.kg34[1])
        w_bl = self._interp(bl, c.kg0[2], c.kg17[2], c.kg34[2])
        w_br = self._interp(br, c.kg0[3], c.kg17[3], c.kg34[3])
        return (w_tl + w_tr + w_bl + w_br) * 2.20462 / 100.0  # convert kg → lb

# ---------------- GUI + Main Loop ---------------- #

def main(stdscr):
    curses.curs_set(0)

    board = WiiBoard()
    addr = board.find_board()

    board.connect(addr)

    prev_weight = 0.0

    try:
        while True:
            weight = board.read_weight()

            stdscr.clear()
            stdscr.addstr(1, 2, "Wii Balance Board Scale")
            stdscr.addstr(3, 2, f"Current Weight: {weight:6.2f} lbs")

            if abs(weight - prev_weight) > 1.0:
                stdscr.addstr(5, 2, "*** ALERT: Weight changed > 1 lb! ***")

            prev_weight = weight
            stdscr.refresh()
            time.sleep(1)

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    curses.wrapper(main)

