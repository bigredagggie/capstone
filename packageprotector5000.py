#!/usr/bin/env python3
import os
import time
import RPi.GPIO as GPIO

#------GPIO Setup-------
GPIO.setmode(GPIO.BCM)
Sync_PIN = 4
Switch_PIN = 17
Siren_PIN = 2
Servo_PIN = 3
GPIO.setup(Sync_PIN, GPIO.OUT)
GPIO.setup(Switch_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Siren_PIN, GPIO.OUT)
GPIO.setup(Servo_PIN, GPIO.OUT)

"""
#Wii Fit Board Sync Button Relay Control - not used
print ("Pressing Sync Button")
GPIO.output(GPIO_PIN, GPIO.HIGH)
time.sleep(1.0)
print ("Releasing Sync Button")
GPIO.output(GPIO_PIN, GPIO.LOW)
time.sleep(1.0)
"""

"""
#Servo Motor Control to Lock/Unloock Box Lid
p = GPIO.PWM(Servo_PIN, 50)
print ("Door is Unlocked")
p.start(2.5)
time.sleep(3)
print ("Door is Locked")
p.ChangeDutyCycle(38)  #This is a percentage. ie x/100*20ms = x ms
time.sleep(3)
"""

"""
#Monitoring Door Switch
try:
        while True:
                #read pin state
                if GPIO.input(Switch_PIN) == GPIO.HIGH:
                        print("Door is Open, Sounding Alarm!!!")
                       #GPIO.output(Siren_PIN, GPIO.HIGH)
                if GPIO.input(Switch_PIN) == GPIO.LOW:
                        print("Door is Closed")
                       #GPIO.output(Siren_PIN, GPIO.LOW)
                time.sleep(0.5)
except KeyboardInterrupt:
        print ("Progrm stopped by keyboard")
finally:
        GPIO.cleanup()
"""

# ===============================
# STATE VARIABLES (Booleans)
# ===============================
empty = 0
full = 0
armed = 0
unarmed = 0


# ===============================
# UTILITY FUNCTIONS
# ===============================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ===============================
# GUI RENDERING FUNCTIONS
# ===============================
def draw_unarmed_empty_box():
    clear_screen()
    print(r"""
          ________________
         /               /|
        /     OPEN      / |
       /_______________/  |
       |               |  |
       |    UNARMED    |  |
       |               |  /
       |     EMPTY     | /
       |_______________|/
    """)


def draw_armed_full_box():
    clear_screen()
    print(r"""
          ________________
         /               /|
        /    CLOSED     / |
       /_______________/  |
       |               |  |
       |     ARMED     |  |
       |               |  /
       |     FULL      | /
       |_______________|/
    """)

# ===============================
# STATE MACHINE
# ===============================
def update_gui():
    if armed == 1:
        draw_armed_full_box() 
    elif unarmed == 1:
        draw_unarmed_empty_box()
    else:
        clear_screen()
        print("\nSystem Idle — No State Active\n")


# ===============================
# MAIN LOOP
# ===============================
def main():
    global empty, full, armed, unarmed

    while True:
        update_gui()

        print("\nControls:")
        print("  [A] Arm system")
        print("  [U] Unarm system")
        print("  [Q] Quit")

        choice = input("\nSelect option: ").lower()

        if choice == "a":
            armed = 1
            unarmed = 0
            full = 1
            empty = 0

        elif choice == "u":
            armed = 0
            unarmed = 1
            full = 0
            empty = 1

        elif choice == "q":
            clear_screen()
            print("Exiting security system...")
            GPIO.cleanup()
            time.sleep(1)
            break


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    main()
