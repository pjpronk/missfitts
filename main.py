from classes.PandaWorld3D import PandaWorld3D
from classes.HapticDevice import HapticDevice

MOUSE_SENSITIVITY = 0.15
HAPTIC_SCALE = 300  # degrees per meter

haptic = HapticDevice()
world = PandaWorld3D()

aim_yaw = 0.0
aim_pitch = 0.0

while True:
    world.taskMgr.step()

    if haptic.connected:
        x, y = haptic.get_position()
        aim_yaw = x * HAPTIC_SCALE
        aim_pitch = y * HAPTIC_SCALE
    else:
        dx, dy = world.get_mouse_delta()
        aim_yaw -= dx * MOUSE_SENSITIVITY
        aim_pitch -= dy * MOUSE_SENSITIVITY
        aim_pitch = max(-80.0, min(80.0, aim_pitch))

    world.set_aim(aim_yaw, aim_pitch)
