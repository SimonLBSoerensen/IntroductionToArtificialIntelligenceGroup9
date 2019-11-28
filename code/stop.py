from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_D, SpeedPercent, MoveTank
tank_drive = MoveTank(OUTPUT_B, OUTPUT_D)
tank_drive.stop()