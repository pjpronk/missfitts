from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    WindowProperties,
    CardMaker,
    ClockObject,
)
import math
import random

<<<<<<< HEAD
=======

>>>>>>> 6b93118 (Adding graphics, merging target respawn spots)
class PandaWorld3D(ShowBase):
    def __init__(self):
        super().__init__()

        self.disableMouse()
        self.setBackgroundColor(0.45, 0.65, 0.9, 1)

        props = WindowProperties()
        props.setTitle("Missfitts shooter")
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        self.accept("escape", self.userExit)

        # Camera position
        self.camera.setPos(0, -10, 2)

<<<<<<< HEAD
        self.setup_lights()
        self.create_floor()
        self.create_wall_box()
=======
        # predetermined configs (size, pos, color)
        self.spot_configs = [
            ((1.0, 1.0, 1.0), (-6, 15, 4.4), (0.6, 0.2, 0.2, 1)),  # Left Mid-ground
            ((0.8, 0.8, 1.5), (5, 12, 0.75), (0.2, 0.5, 0.2, 1)),  # Right Near-ground
            ((1.2, 1.2, 1.2), (0, 25, 3.0), (0.2, 0.2, 0.6, 1)),   # Center Far-ground 
            ((1.7, 1.7, 1.7), (-8, 17, 0.35), (0.5, 0.5, 0.1, 1)), # Far Left
            ((1.5, 1.5, 0.8), (4, 5, 0.4), (0.5, 0.1, 0.5, 1)),    # Right Mid 
            ((0.9, 0.9, 2.0), (-3, 10, 1.0), (0.1, 0.5, 0.5, 1)),  # Left Near 
            ((1.1, 1.1, 1.1), (4, 8, 5.0), (0.8, 0.4, 0.0, 1)),    # Far Right 
            ((0.9, 0.6, 1.2), (0.2, 0.15, 0.65), (0.3, 0.3, 0.3, 1)) # Mid Center
        ]

        # Extract target pos with height adjustment
        self.target_positions = []
        for size, pos, color in self.spot_configs:
            x, y, z = pos
            box_height = size[2]  # The 3rd value in the 'size' tuple is the height
            
            # Keep X and Y the same, but add the box's height to Z
            self.target_positions.append((x, y, z + box_height))

        # Environment & Player Setup
        self.setup_lights()
        self.create_floor()
        self.create_wall_box()
        self.create_respawn_spots()
        self.create_stairs()

>>>>>>> 6b93118 (Adding graphics, merging target respawn spots)
        self.create_gun_3d()
        self.create_crosshair()

        self.mouse_dx = 0.0
        self.mouse_dy = 0.0

        self.center_mouse()

        self.taskMgr.add(self._read_mouse, "_read_mouse")
        self.taskMgr.add(self.animate_gun, "animate_gun")

        # target system
        self.target_node = None
        self.current_target_index = -1

        self.dummy_node = None
        self.current_dummy_index = -1
        self.last_target_pos = None
<<<<<<< HEAD
        
        # 10 predetermined positions (x, y, z) 
        self.target_positions = [
            (0, 10, 1), (-3, 12, 1.5), (3, 12, 1.5), 
            (-5, 15, 2), (5, 15, 2), (0, 18, 0.5), 
            (-4, 8, 2.5), (4, 8, 2.5), (-2, 20, 1.5), (2, 20, 1.5)
        ]
        

    def setup_lights(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.4, 0.4, 0.4, 1))
=======


    def setup_lights(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.7, 0.7, 0.7, 1))
>>>>>>> 6b93118 (Adding graphics, merging target respawn spots)
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)

        sun = DirectionalLight("sun")
        sun.setColor((0.9, 0.9, 0.85, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(-45, -35, 0)
        self.render.setLight(sun_np)

    def create_floor(self):
        cm = CardMaker("floor")
        cm.setFrame(-30, 30, -30, 30)
        floor = self.render.attachNewNode(cm.generate())
        floor.setP(-90)
        floor.setPos(0, 10, 0)
        floor.setColor(0.25, 0.28, 0.25, 1)

<<<<<<< HEAD
    def create_box(self, parent, size=(1, 1, 1), pos=(0, 0, 0), color=(1, 1, 1, 1)):
        box = self.loader.loadModel("models/box")
        box.clearTexture()
        box.reparentTo(parent)
        box.setScale(size[0], size[1], size[2])
        box.setPos(*pos)
        box.setColor(*color)
        return box

    def create_wall_box(self):
        self.create_box(
            self.render,
            size=(2.5, 0.4, 2.5),
            pos=(0, 8, 1.25),
            color=(0.72, 0.72, 0.78, 1),
        )

        self.create_box(
            self.render,
            size=(1.2, 1.2, 1.2),
            pos=(3, 11, 0.6),
            color=(0.55, 0.35, 0.25, 1),
        )

        self.create_box(
            self.render,
            size=(1.5, 1.5, 3),
            pos=(-4, 14, 1.5),
            color=(0.4, 0.4, 0.5, 1),
=======
    def create_box(self, parent, size=(1, 1, 1), pos=(0, 0, 0), color=(1, 1, 1, 1), texture_file=None):
        box = self.loader.loadModel("models/box")
        if texture_file:
            box.setTexture(self.loader.loadTexture(texture_file))
        else:
            box.clearTexture()
            box.setColor(*color)
        box.reparentTo(parent)
        box.setScale(size[0], size[1], size[2])
        box.setPos(*pos)
        return box

    def create_wall_box(self):
        width = 20
        depth = 30
        height = 10
        # right wall
        self.create_box(
            self.render,
            size=(1, depth+10, height),
            pos=(width/2, -10, 0),
            color=(0.5, 0.2, 0.2, 1),
        )

        # left wall
        self.create_box(
            self.render,
            size=(1, 40, height),
            pos=(-width/2, -10, 0),
            color=(0.5, 0.2, 0.2, 1),
        )

        # back wall
        self.create_box(
            self.render,
            size=(width, 1, height),
            pos=(-width/2, depth, 0),
            color=(0.5, 0.2, 0.2, 1),
        )

        # ceiling
        self.create_box(
            self.render,
            size=(width, depth+10, 1),
            pos=(-width/2, -10, height),
            color=(0.8, 0.8, 0.8, 1),
        )

        # second floor
        self.create_box(
            self.render,
            size=(width/2-5, depth, 1),
            pos=(5, 0, height/2-1),
            color=(0.5, 0.5, 0.5, 1),
>>>>>>> 6b93118 (Adding graphics, merging target respawn spots)
        )

    def create_gun_3d(self):
        self.gun_root = self.camera.attachNewNode("gun_root")
        self.gun_root.setPos(0.6, 1.4, -0.55)
        self.gun_root.setHpr(0, -8, 0)

        self.create_box(
            self.gun_root,
            size=(0.22, 0.55, 0.14),
            pos=(0, 0, 0),
            color=(0.12, 0.12, 0.12, 1),
        )

        self.create_box(
            self.gun_root,
            size=(0.08, 0.7, 0.08),
            pos=(0, 0.55, 0.02),
            color=(0.2, 0.2, 0.2, 1),
        )

        grip = self.create_box(
            self.gun_root,
            size=(0.1, 0.18, 0.22),
            pos=(0, -0.12, -0.16),
            color=(0.08, 0.08, 0.08, 1),
        )
        grip.setP(-18)

    def create_crosshair(self):
        cm_h = CardMaker("crosshair_h")
        cm_h.setFrame(-0.02, 0.02, -0.002, 0.002)
        h = self.aspect2d.attachNewNode(cm_h.generate())
        h.setColor(1, 1, 1, 1)

        cm_v = CardMaker("crosshair_v")
        cm_v.setFrame(-0.002, 0.002, -0.02, 0.02)
        v = self.aspect2d.attachNewNode(cm_v.generate())
        v.setColor(1, 1, 1, 1)

    def center_mouse(self):
        if self.win is not None and self.win.movePointer(
            0,
            self.win.getXSize() // 2,
            self.win.getYSize() // 2
        ):
            pass

    def _read_mouse(self, task):
        """Stores raw mouse delta each frame; consumed by main loop."""
        if not self.mouseWatcherNode.hasMouse():
            self.mouse_dx = 0.0
            self.mouse_dy = 0.0
            return task.cont

        cx = self.win.getXSize() // 2
        cy = self.win.getYSize() // 2
        self.mouse_dx = float(self.win.getPointer(0).getX() - cx)
        self.mouse_dy = float(self.win.getPointer(0).getY() - cy)
        self.center_mouse()
        return task.cont

    def get_mouse_delta(self) -> tuple[float, float]:
        """Returns (dx, dy) pixel delta since last frame center."""
        return self.mouse_dx, self.mouse_dy

    def set_aim(self, yaw: float, pitch: float):
        """Positions the camera to the given yaw/pitch angles."""
        self.camera.setHpr(yaw, pitch, 0)

    def animate_gun(self, task):
        t = task.time
        self.gun_root.setZ(-0.55 + math.sin(t * 1.8) * 0.015)
        self.gun_root.setP(-8 + math.sin(t * 1.5) * 1.2)
        self.gun_root.setR(math.sin(t * 1.2) * 1.0)
        return task.cont

<<<<<<< HEAD
=======
    def create_targets(self):
        self.target_cube = self.create_box(
        self.render,
        size=(0.8, 0.8, 0.8),
        pos=(5, 15, 4),
        color=(0, 1, 1, 1) # Cyan
    )
        
    def create_respawn_spots(self):
        """
        Creates 8 distinct boxes at various distances and heights 
        using the existing create_box function.
        """
        self.respawn_nodes = []
        for size, pos, color in self.spot_configs:
            node = self.create_box(self.render, size=size, pos=pos, color=color, texture_file="textures/woodplank.jpg")
            self.respawn_nodes.append(node)

    def create_stairs(self):
        """
        Creates a staircase leading up to the second floor platform.
        """
        num_steps = 12              # Increased slightly for a smoother climb
        step_size = (1.5, 30, 0.4) # Width, Depth, Thickness of each step

        # Start on the ground (z=0), slightly to the left and forward in the room
        start_pos = (-3.0, 5.0, 0.0)   
        
        # End exactly at the edge of your second floor (x=5) and its height (z=4)
        end_pos = (4.0, 9, 4.0)     

        for i in range(num_steps):
            # Calculate percentage along the staircase (0.0 to 1.0)
            t = i / (num_steps - 1)
            
            # Find the exact X, Y, Z for this step
            step_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            step_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            step_z = start_pos[2] + (end_pos[2] - start_pos[2]) * t
            
            self.create_box(
                self.render,
                size=step_size,
                pos=(step_x, step_y, step_z),
                color=(1, 1, 0, 1), # Bright green, just like the drawing!
            )
        
>>>>>>> 6b93118 (Adding graphics, merging target respawn spots)
    def spawn_random_target(self, target_size=0.6):
        # Remove old blocks
        if self.target_node is not None:
            self.target_node.removeNode()
        if self.dummy_node is not None:
            self.dummy_node.removeNode()

        # Save old positon of target for Fitts' Law berekening
        if self.current_target_index != -1:
            self.last_target_pos = self.target_positions[self.current_target_index]
        else:
            self.last_target_pos = (0, 0, 0) # Default for first target spawn, won't be used in ID calculation

        # List with all 9 new possible locations
        all_indices = list(range(len(self.target_positions)))

        # chooses new location for target
        target_opties = [i for i in all_indices if i != self.current_target_index]
        self.current_target_index = random.choice(target_opties)
        
        # chooses new location for dummy
        dummy_options = [i for i in all_indices if i != self.current_target_index and i != self.current_dummy_index]
        self.current_dummy_index = random.choice(dummy_options)

        new_target_pos = self.target_positions[self.current_target_index]
        new_dummy_pos = self.target_positions[self.current_dummy_index]

        # --- FITTS' LAW BEREKENING ---
        id_score = 0.0
        # Calculates the distance between the last target position and the new target position, and then calculates the ID score using Fitts' Law
        if self.last_target_pos is not None:
            p1 = self.last_target_pos
            p2 = new_target_pos
            # Euclidean distance formule
            distance = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)
            # Shannon form van Fitts' Law: ID = log2(D/W + 1)
            id_score = math.log2((distance / target_size) + 1)


        # 4. make the red block (Target)
        self.target_node = self.create_box(
            self.render,
            size=(target_size, target_size, target_size),
            pos=new_target_pos,
            color=(0.9, 0.1, 0.1, 1),  # Red
        )

        # 5. make the green block (Dummy)
        self.dummy_node = self.create_box(
            self.render,
            size=(target_size, target_size, target_size),
            pos=new_dummy_pos,
            color=(0.1, 0.9, 0.1, 1),  # Green
        )
        
<<<<<<< HEAD
        return id_score
=======
        return id_score
    
>>>>>>> 6b93118 (Adding graphics, merging target respawn spots)
