import cv2
import numpy as np

from ppadb.client import Client as AdbClient

class Adb():
    def __init__(self):
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()
        if len(devices) == 0:
            raise Exception('There is no ADB devices')

        self.device = devices[0]

    def get_screen(self, color: bool = True):
        buffer = np.frombuffer(self.device.screencap(), dtype='uint8')

        if color:
            img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        else:
            img = cv2.imdecode(buffer, cv2.IMREAD_GRAYSCALE)
        
        return img

    def touch(self, x, y):
        self.device.input_tap(x, y)
        
    def swipe(self, start_x, start_y, end_x, end_y, duration):
        self.device.input_swipe(start_x, start_y, end_x, end_y, duration)

    def run_app(self):
        self.device.shell('monkey -p com.firsttouchgames.smp -c android.intent.category.LAUNCHER 1')
        