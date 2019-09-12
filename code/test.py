from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, MoveTank, SpeedPercent
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2.sound import Sound
import time
sound = Sound()

sound.speak("I am ready in 3")
time.sleep(1)
sound.speak("2")
time.sleep(1)
sound.speak("1")
time.sleep(1)
sound.speak("Lift off")

tank = MoveTank(OUTPUT_A, OUTPUT_D)

for speed_pro in range(20, 100, 20):
    speed_pro = -1*speed_pro

    tank.on(SpeedPercent(speed_pro), SpeedPercent(speed_pro))
    time.sleep(0.2)

sound.speak("Top speed")
time.sleep(3)
tank.on(0,0)

sound.speak("mission completed")
