from classes.PandaWorld3D import PandaWorld3D
from classes.HapticDevice import HapticDevice
import time
from io import StringIO

MOUSE_SENSITIVITY = 0.15
HAPTIC_SCALE = 1.0  # aim degrees per motor degree

haptic = HapticDevice()
if haptic.connected:
    haptic.calibrate()
world = PandaWorld3D()

aim_yaw = 0.0
aim_pitch = 0.0

# Trial variables
target_size = 0.6
total_trials = 20
current_trial = 0
trial_started = False
total_id = 0.0
start_time = 0.0
old_time = 0.0
new_time =0.0

# Data file
CSV = open('CSVfile.csv', 'w')

world.spawn_random_target(target_size=target_size)
print(f"Shoot the first target to start the trial of {total_trials}!")

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

    # --- GAME LOGICA (TARGET HIT) ---
    target_hit = False 

    # For now, we simulate that the key 'T' immitates the target being hit
    if world.mouseWatcherNode.hasMouse():
        if world.mouseWatcherNode.isButtonDown(world.win.getKeyboardMap().getMappedButton("t")):
            target_hit = True

    if target_hit:
        if not trial_started:
            # This is the first hit that starts the trial
            print("\n--- TRIAL GESTART ---")
            trial_started = True
            start_time = time.time()
            old_time = start_time
            # Spawn the first target and get its difficulty (ID score), even though it won't be used in the ID calculation since there's no previous target
            world.spawn_random_target(target_size=target_size)
        else:
            # This is a hit during an ongoing trial, so we calculate the ID score for the jump to the new target and accumulate it
            current_trial += 1
            
            # Spawn a new target and get the ID score for the jump to this new target, which is based on the distance from the last target to the new target and the target size
            difficulty = world.spawn_random_target(target_size=target_size)
            total_id += difficulty
            
            # Calculating time per shot
            new_time = time.time()
            shot_time = new_time - old_time
            
            print(f"Hit {current_trial}/{total_trials} | ID deze sprong: {difficulty:.2f} | time taken: {shot_time:.2f} seconds")
            
            # Writing shot data
            CSV.write(f"{current_trial}, {difficulty}, {shot_time}\n")
            
            old_time = new_time

            # Check if the trial is complete
            if current_trial >= total_trials:
                end_time = time.time()
                total_time = end_time - start_time
                throughput = total_id / total_time if total_time > 0 else 0
                
                print("\n=== TRIAL COMPLETE ===")
                print(f"Total timne: {total_time:.2f} seconds")
                print(f"Total ID: {total_id:.2f} bits")
                print(f"Average Throughput: {throughput:.2f} bits/seconde")
                print("======================")
                
                # Sluit het programma (of je kunt een pauze/restart scherm maken)
                CSV.close()
                break 
        
        # Voorkom 'machinegeweer' klikken
        while world.mouseWatcherNode.isButtonDown(world.win.getKeyboardMap().getMappedButton("t")):
            world.taskMgr.step()