from ev3dev2.sensor import lego
class gyro:
    def __init__(self, gyrosensor_pin, mode='GYRO-G&A'):
        self.gyro_sensor = lego.GyroSensor(gyrosensor_pin)
        self.gyro_sensor.mode = mode
        self.offset = 0

    def reset(self):
        self.gyro_sensor.reset()
        self.offset = self.gyro_sensor.angle

    def get_angel(self):
        return self.gyro_sensor.angle - self.offset

    def add_offset(self, offset_to_add):
        self.offset += offset_to_add

    def get_angel_and_rate(self):
        gyro_angel, gyro_rate = self.gyro_sensor.angle_and_rate
        gyro_angel -= self.offset
        return [gyro_angel, gyro_rate]