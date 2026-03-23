import RPi.GPIO as GPIO
import time

#----------GPIO Setup for Sync Button Relay Control---------
GPIO.setmode(GPIO.BCM)
Sync_PIN = 4
Switch_PIN = 17
Siren_PIN = 2
Servo_PIN = 3
LoadSW_PIN = 25
GPIO.setup(Sync_PIN, GPIO.OUT)
GPIO.setup(Switch_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LoadSW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Siren_PIN, GPIO.OUT)
GPIO.setup(Servo_PIN, GPIO.OUT)

"""
print ("Pressing Sync Button")
GPIO.output(GPIO_PIN, GPIO.HIGH)
time.sleep(1.0)
print ("Releasing Sync Button")
GPIO.output(GPIO_PIN, GPIO.LOW)
time.sleep(1.0)
"""


p = GPIO.PWM(Servo_PIN, 50)
print ("Door is Unlocked")
p.start(2.5)
time.sleep(3)
print ("Door is Locked")
p.ChangeDutyCycle(38)  #This is a percentage. ie x/100*20ms = x ms
time.sleep(3)

GPIO.cleanup()

"""
print ("Monitoring Micro Switches..........")
try:
	while True:
		#read pin state
		if GPIO.input(Switch_PIN) == GPIO.HIGH:
			print("Door is Open, Sounding Alarm!!!")
			print(GPIO.input(Switch_PIN))
			#GPIO.output(Siren_PIN, GPIO.HIGH)
		if GPIO.input(Switch_PIN) == GPIO.LOW:
			print("Door is Closed")
			print(GPIO.input(Switch_PIN))
			GPIO.output(Siren_PIN, GPIO.LOW)
		if GPIO.input(LoadSW_PIN) == GPIO.HIGH:
			print("Box is Empty, No Packages")
		if GPIO.input(LoadSW_PIN) == GPIO.LOW:
			print("Package Detected!!!  Do you want to Arm the Security System___?  (Y/N)")
		time.sleep(1)
except KeyboardInterrupt:
	print ("Progrm stopped by keyboard")
finally: 
	GPIO.cleanup()
"""
