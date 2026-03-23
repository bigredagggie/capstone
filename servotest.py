import RPi.GPIO as GPIO 
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

pwm = GPIO.PWM(18, 50)
pwm.start(7.5)

time.sleep(1)
pwm.ChangeDutyCycle(2.5)  # one direction
time.sleep(1)
pwm.ChangeDutyCycle(15)  # other direction
time.sleep(1)

pwm.ChangeDutyCycle(0)
pwm.stop()
GPIO.cleanup()
