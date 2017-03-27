
import sys
sys.path.append("..")

import app
from app.camera.fli import Camera

cam = Camera()
print(cam.CCD_temp)
print(cam.CCD_set_point)
print(cam.base_temp)

cam._cam.take_photo()

