import os
import RPi.GPIO as GPIO
import time
import sys
import select

# Autostart detection
AUTOSTART = os.getenv("AUTOSTART", "0") == "1"

# GPIO setup
LID_SWITCH_PIN = 17
WEIGHT_SENSOR_PIN = 25
BUZZER_PIN = 2
LOCK_SERVO_PIN = 18     #use hardare PWM

GPIO.setmode(GPIO.BCM)
GPIO.setup(LID_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(WEIGHT_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LOCK_SERVO_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(LOCK_SERVO_PIN, 50)  # 50Hz for servo control
servo_pwm.start(2.5)
time.sleep(1)
servo_pwm.ChangeDutyCycle(0)

# State variables
Lid_Switch = False
Weight_Sensor = False
Buzzer_Status = False
Lock_Status = False
Arming_System = False

# UTILITY FUNCTION
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def set_buzzer(status: bool):
    global Buzzer_Status
    Buzzer_Status = status
    GPIO.output(BUZZER_PIN, status)

def set_lock_status(status: bool):
    global Lock_Status
    Lock_Status = status
    if status:
        print("set servo to locked pos")
        servo_pwm.ChangeDutyCycle(7.5)  # Locked position = 38% / 100 * 20 = 7.6ms
        time.sleep(1)
        servo_pwm.ChangeDutyCycle(0)
#    elif not status:
#        servo_pwm.ChangeDutyCycle(12.5)  # Unlocked position = 12.5% / 100 * 20 = 2.5ms
#        print("set servo to unlocked pos")

def display_gui(state: int):
 # ASCII Art representation based on state
    if state == 1:
        clear_screen()
        print("\n".join([
            "           ___________________",
            "          |                   |",
            "          |                   |",
            "          |     LID OPEN      |",
            "          |                   |",
            "          ____________________",
            "         /     UNLOCKED      /|",
            "        /      UNARMED      / |",
            "       /___________________/  |",
            "       |                   |  |",
            "       |                   |  |",
            "       |       EMPTY       |  /",
            "       |                   | /",
            "       |___________________|/"
        ]))
    elif state == 2:
        clear_screen()
        print("\n".join([
            "           ___________________",
            "          |                   |",
            "          |                   |",
            "          |     LID OPEN      |",
            "          |                   |",
            "          ____________________",
            "         /     UNLOCKED      /|",
            "        /      UNARMED      / |",
            "       /___________________/  |",
            "       |            _____  |  |",
            "       | Package   |\   /| |  |",
            "       | Detected! |  X  | |  /",
            "       |           |/___\| | /",
            "       |___________________|/"
        ]))
        print("\nClose the box lid if you wish to Arm the System")
    elif state == 3:
        clear_screen()
        print("\n".join([
            "                               ",
            "                               ",
            "                               ",
            "               LID CLOSED      ",
            "                               ",
            "          ____________________ ",
            "         /     UNLOCKED      /|",
            "        /      UNARMED      / |",
            "       /___________________/  |",
            "       |            _____  |  |",
            "       | Package   |\   /| |  |",
            "       | Detected! |  X  | |  /",
            "       |           |/___\| | /",
            "       |___________________|/"
        ]))
    elif state == 4:
        clear_screen()
        print("\n".join([
            "                               ",
            "                               ",
            "                               ",
            "                LID CLOSED     ",
            "                               ",
            "          ____________________ ",
            "         / ..Lid is Locked.. /|",
            "        /  ..SYSTEM ARMED.. / |",
            "       /___________________/  |",
            "       |            _____  |  |",
            "       | Package   |\   /| |  |",
            "       | Detected! |  X  | |  /",
            "       |           |/___\| | /",
            "       |___________________|/"
        ]))
    elif state == 5:
        clear_screen()
        print("\n".join([
            "                               ",
            "                               ",
            "                               ",
            "               LID CLOSED      ",
            "                               ",
            "          ____________________ ",
            "         /     UNLOCKED      /|",
            "        /      UNARMED      / |",
            "       /___________________/  |",
            "       |                   |  |",
            "       |       Empty       |  |",
            "       |                   |  /",
            "       |                   | /",
            "       |___________________|/"
        ]))
    elif state == 6:
        clear_screen()
        print("\n".join([
            "           ___________________",
            "          |                   |",
            "          |..Lid was Opened.. |",
            "          |                   |",
            "          | Alarm is Sounding |",
            "          ____________________",
            "         / ..Lid is Locked.. /|",
            "        /  ..SYSTEM ARMED.. / |",
            "       /___________________/  |",
            "       |            _____  |  |",
            "       | Package   |\   /| |  |",
            "       | Detected! |  X  | |  /",
            "       |           |/___\| | /",
            "       |___________________|/"
        ]))
    elif state == 7:
        clear_screen()
        print("\n".join([
            "           ___________________",
            "          |                   |",
            "          |..Lid was Opened.. |",
            "          |                   |",
            "          | Alarm is Sounding |",
            "          ____________________",
            "         / ..Lid is Locked.. /|",
            "        /  ..SYSTEM ARMED.. / |",
            "       /___________________/  |",
            "       |                   |  |",
            "       | !!! Package  !!!  |  |",
            "       | !!! Stolen   !!!  |  /",
            "       |                   | /",
            "       |___________________|/"
        ]))
    
    # ... Add GUI outputs for all states

    # Print state values
"""
    print("\n")
    print(f"Lid_Switch: {Lid_Switch}")
    print(f"Weight_Sensor: {Weight_Sensor}")
    print(f"Buzzer_Status: {Buzzer_Status}")
    print(f"Lock_Status: {Lock_Status}")
    print(f"Arming_System: {Arming_System}")
"""

def read_input():
    global Lid_Switch, Weight_Sensor
    Lid_Switch = GPIO.input(LID_SWITCH_PIN)
    Weight_Sensor = GPIO.input(WEIGHT_SENSOR_PIN)

def main():
    global Arming_System
    try:
        while True:
            read_input()

            # State transition logic
            #State 1:  Open Lid, Unarmed System, Empty Box, Buzzer is Off, Lid is Unlocked
            if Lid_Switch and Weight_Sensor and not Arming_System:
                set_buzzer(False)
                set_lock_status(False)
                display_gui(1)

            #State 2:  Open Lid, Unarmed System, Box is Full, Buzzer is Off, Lid is Unlocked
            elif Lid_Switch and not Weight_Sensor and not Arming_System:
                set_buzzer(False)
                set_lock_status(False)
                display_gui(2)

            #State 3:  Closed Lid, Unarmed System, Box is Full, Buzzer is Off, Lid is Unlocked
            elif not Lid_Switch and not Weight_Sensor and not Arming_System:
                set_buzzer(False)
                display_gui(3)
                
                if AUTOSTART:
                    # In autostart mode, skip user input and auto-arm
                    choice = "a"
                else:
                    # Manual mode - show controls and wait for input
                    print("\nControls:")
                    print("  [A] Arm system")
                    print("  [U] Unarm system")
                    print("  [Q] Quit")
                    # Wait for input with 10-second timeout
                    ready = select.select([sys.stdin], [], [], 10)
                    if ready[0]:
                        choice = input("\nSelect option: ").lower()
                    else:
                        choice = "a"  # Default to arming if no input
                    print("\nNo input detected. Auto-arming system...")
                
                if choice == "a":
                    Arming_System = True
                    set_lock_status(True)
                    display_gui(4)
                elif choice == "u":
                    Arming_System = False
                    set_lock_status(False)
                    display_gui(3)
                elif choice == "q":
                    clear_screen()
                    print("Exiting security system...")
                    break

            #State 4:  Closed Lid, Armed System, Box is Full, Buzzer is Off, Lid is Locked
            elif not Lid_Switch and not Weight_Sensor and Arming_System:
                set_buzzer(False)
                #set_lock_status(True)
                display_gui(4)

            #State 5:  Closed Lid, Unarmed System, Box is Empty, Buzzer is Off, Lid is Unlocked
            elif not Lid_Switch and Weight_Sensor and not Arming_System:
                set_buzzer(False)
                set_lock_status(False)
                display_gui(5)

            #State 6:  Open Lid, Armed System, Box Is Full, Buzzer is On, Lid is Locked
            elif Lid_Switch and not Weight_Sensor and Arming_System:
                set_buzzer(True)
                #set_lock_status(True)
                display_gui(6)

            #State 7:  Open Lid, Armed System, Box Is Empty, Buzzer is On, Lid is Locked
            elif Lid_Switch and Weight_Sensor and Arming_System:
                set_buzzer(True)
                #set_lock_status(True)
                display_gui(7)
            time.sleep(.5)  # Refresh rate of 1Hz

    finally:
        print("\nProgram Stopped by User")
        servo_pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
