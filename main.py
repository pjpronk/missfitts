from classes.PandaWorld3D import PandaWorld3D
from classes.HapticDevice import HapticDevice
from classes.HapticForceGenerator import HapticForceGenerator
import time

MOUSE_SENSITIVITY = 0.15
HAPTIC_SCALE = 1.0  # degrees per motor degree

haptic = HapticDevice()
force_gen = HapticForceGenerator(kp=0.2, kd=0.00)

if haptic.connected:
    haptic.calibrate()
world = PandaWorld3D()

aim_yaw = 0.0
aim_pitch = 0.0

# Trial state
target_size = 0.6
total_trials = 20
current_trial = 0
trial_started = False
cumulative_id = 0.0
trial_start_time = 0.0
shot_start_time = 0.0
trigger_held = False

csv_file = open('CSVfile.csv', 'w')

world.spawn_random_target(target_size=target_size)
print(f"Shoot the first target to start the trial of {total_trials}!")


def update_aim(yaw, pitch):
    if haptic.connected:
        a1, a2 = haptic.get_angles()
        return (-a1 - a2) * HAPTIC_SCALE, (a1 - a2) * HAPTIC_SCALE
    dx, dy = world.get_mouse_delta()
    return yaw - dx * MOUSE_SENSITIVITY, max(-80.0, min(80.0, pitch - dy * MOUSE_SENSITIVITY))


def update_force():
    if not haptic.connected:
        return
    angular_error = world.get_target_angular_error()
    fx, fy = force_gen.calculate_force(*angular_error) if angular_error is not None else (0.0, 0.0)
    world.draw_force_vector(fx, fy, scale=0.001)
    haptic.set_force(fx, fy)


def handle_shot(target_hit):
    global trial_started, current_trial, cumulative_id, trial_start_time, shot_start_time

    if not trial_started:
        print("\n--- TRIAL STARTED ---")
        trial_started = True
        trial_start_time = time.time()
        shot_start_time = trial_start_time
        world.spawn_random_target(target_size=target_size)
        return False

    current_trial += 1
    difficulty = world.spawn_random_target(target_size=target_size)
    cumulative_id += difficulty

    now = time.time()
    shot_time = now - shot_start_time
    shot_start_time = now

    print(f"Hit {current_trial}/{total_trials} | ID this jump: {difficulty:.2f} | time taken: {shot_time:.2f}s")
    csv_file.write(f"{current_trial}, {difficulty}, {shot_time}, {int(target_hit)}\n")

    if current_trial >= total_trials:
        total_time = time.time() - trial_start_time
        throughput = cumulative_id / total_time if total_time > 0 else 0.0

        print("\n=== TRIAL COMPLETE ===")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Total ID: {cumulative_id:.2f} bits")
        print(f"Average throughput: {throughput:.2f} bits/second")
        print("======================")

        csv_file.close()
        return True

    return False


def is_trigger_pressed():
    if not world.mouseWatcherNode.hasMouse():
        return False
    return world.mouseWatcherNode.isButtonDown(
        world.win.getKeyboardMap().getMappedButton("t")
    )


while True:
    world.taskMgr.step()

    aim_yaw, aim_pitch = update_aim(aim_yaw, aim_pitch)
    update_force()
    world.set_aim(aim_yaw, aim_pitch)

    trigger_down = is_trigger_pressed()

    if trigger_down and not trigger_held:
        trigger_held = True
        target_hit = world.get_targeted_node() is not None
        if handle_shot(target_hit):
            break

    if not trigger_down:
        trigger_held = False
