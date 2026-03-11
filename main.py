from classes.PandaWorld3D import PandaWorld3D
from classes.HapticDevice import HapticDevice

MOUSE_SENSITIVITY = 0.15
HAPTIC_SCALE = 1.0  # aim degrees per motor degree

haptic = HapticDevice()
if haptic.connected:
    haptic.calibrate()
world = PandaWorld3D()

aim_yaw = 0.0
aim_pitch = 0.0

while True:
    world.taskMgr.step()

    if haptic.connected:
        a1, a2 = haptic.get_angles()
        haptic.set_force(0, 0)
        aim_pitch   = (a1 - a2) * HAPTIC_SCALE
        aim_yaw = (-a1 - a2) * HAPTIC_SCALE
    else:
        dx, dy = world.get_mouse_delta()
        aim_yaw -= dx * MOUSE_SENSITIVITY
        aim_pitch -= dy * MOUSE_SENSITIVITY
        aim_pitch = max(-80.0, min(80.0, aim_pitch))

    world.set_aim(aim_yaw, aim_pitch)

    # game logic (TARGET HIT PLACEHOLDER)
    # TODO: Add cdoe that checks if the target is hit
    target_hit = False 

    # For now, we simulate that the key 'T' immitates the target being hit
    if world.mouseWatcherNode.hasMouse():
        if world.mouseWatcherNode.isButtonDown(world.win.getKeyboardMap().getMappedButton("t")):
            target_hit = True

    if target_hit:
        print("Target hit")
        world.spawn_random_target()
        
        # Voorkom dat hij 60x per seconde spawnt als je de knop ingedrukt houdt
        while world.mouseWatcherNode.isButtonDown(world.win.getKeyboardMap().getMappedButton("t")):
            world.taskMgr.step()
