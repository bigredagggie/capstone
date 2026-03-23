#!/usr/bin/env python3
import bluetooth
import struct
import time
import curses
import sys

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

        self._initialize_board()

    def _initialize_board(self):
        # Start sending data reports
        # 0x12 = set report mode
        self._send(self.control_socket, b'\x12\x04')

        # Request calibration data
        self._get_calibration()

    def _send(self, sock, data):
        sock.send(bytes(data))

    def _read(self):
        return self.data_socket.recv(1024)

    def _get_calibration(self):
        # Ask for calibration
        self._send(self.control_socket, b'\x15\x00')
        data = self._read()

        # Parse calibration data (known WBB format)
        # Packet is 23 bytes long containing:
        #   3 calibration points: 0kg, 17kg, 34kg
        #   Each point gives 4 ADC values
        cal = struct.unpack(">BBBBHHHHHHHH", data[2:2+20])

        self.calibration.kg0 = cal[4:8]
        self.calibration.kg17 = cal[8:12]
        self.calibration.kg34 = cal[12:16]

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

    def _kg_from_raw(self, (tl, tr, bl, br)):
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

    while True:
        weight = board.read_weight()

        stdscr.clear()
        stdscr.addstr(1, 2, "Wii Balance Board Scale")
        stdscr.addstr(3, 2, f"Current Weight: {weight:6.2f} lbs")

        # Alert for >1 lb change
        if abs(weight - prev_weight) > 1.0:
            stdscr.addstr(5, 2, "*** ALERT: Weight changed > 1 lb! ***")

        prev_weight = weight
        stdscr.refresh()
        time.sleep(1)

if __name__ == "__main__":
    curses.wrapper(main)
