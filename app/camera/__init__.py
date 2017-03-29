import sys

if 'darwin' in sys.platform:
    from app.camera.simulator import Camera
else:
    from app.camera.fli import Camera