from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    WindowProperties,
    CardMaker,
    ClockObject,
    CollisionTraverser, 
    CollisionNode, 
    CollisionRay, 
    CollisionHandlerQueue,
    BitMask32,
    Point2,
    LineSegs
)
import math
import random

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

        # predetermined configs (size, pos, color)
        self.spot_configs = [
            ((1.0, 1.0, 1.0), (-6, 15, 4.4), (0.6, 0.2, 0.2, 1)),  # Left Mid-ground
            ((0.8, 0.8, 1.5), (5, 12, 0.75), (0.2, 0.5, 0.2, 1)),  # Right Near-ground
            ((1.2, 1.2, 1.2), (0, 25, 3.0), (0.2, 0.2, 0.6, 1)),   # Center Far-ground 
            ((1.7, 1.7, 1.7), (-8, 17, 0.35), (0.5, 0.5, 0.1, 1)), # Far Left
            ((1.5, 1.5, 0.8), (4, 5, 0.4), (0.5, 0.1, 0.5, 1)),    # Right Mid 
            ((0.9, 0.9, 2.0), (-3, 10, 1.0), (0.1, 0.5, 0.5, 1)),  # Left Near 
            ((1.1, 1.1, 1.1), (4.5, 13, 5), (0.8, 0.4, 0.0, 1)),    # Far Right 
            ((0.9, 0.6, 1.2), (0.2, 0.15, 0.65), (0.3, 0.3, 0.3, 1)) # Mid Center
        ]

        # Extract target pos with height adjustment
        self.target_positions = []
        for size, pos, color in self.spot_configs:
            x, y, z = pos
            z_offset = size[2] + 0.4
            y_offset = size[1]
            x_offset = size[0] / 2
            
            # Keep X and Y the same, but add the box's height to Z
            self.target_positions.append((x + x_offset, y + y_offset, z + z_offset))

        # Environment & Player Setup
        self.setup_lights()
        self.create_floor()
        self.create_wall_box()
        self.create_respawn_spots()
        self.create_stairs()

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
        
        
        ## Setting up hit detection system
        self.cTrav = CollisionTraverser()
        self.rayQueue = CollisionHandlerQueue()
        
        # Create the ray attached to the camera
        pickerNode = CollisionNode('mouseRay')
        pickerNP = self.camera.attachNewNode(pickerNode)
        self.pickerRay = CollisionRay(0, 0, 0, 0, 1, 0)
        pickerNode.addSolid(self.pickerRay)
        
        # Register with traverser
        self.cTrav.addCollider(pickerNP, self.rayQueue)
        
        # Use a BitMask so we only hit targets, not walls/floors
        self.target_mask = BitMask32.bit(1)
        pickerNode.setFromCollideMask(self.target_mask)


    def setup_lights(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.7, 0.7, 0.7, 1))
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

    def create_box(self, parent, size=(1, 1, 1), pos=(0, 0, 0), color=(1, 1, 1, 1), texture_file=None, mask=None):
        box = self.loader.loadModel("models/box")
        box.reparentTo(parent)
        if texture_file:
            box.setTexture(self.loader.loadTexture(texture_file), 1)
        else:
            box.clearTexture()
            box.setColor(*color)        
        box.setScale(size[0], size[1], size[2])
        box.setPos(*pos)
        if mask:
            box.setCollideMask(mask)
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
            texture_file = "textures/cs.jpg"
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
            texture_file="textures/concrete.jpg"
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
        end_pos = (3.5, 9, 4.0)     

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
                color=(0.1, 0.1, 0.1, 1), 
                texture_file="textures/rusty_metal.jpg"
            )
        
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
            mask=self.target_mask,
        )
        self.target_node = self.loader.loadModel("smiley")
        self.target_node.reparentTo(self.render)
        self.target_node.setScale(target_size / 1.5) 
        self.target_node.setPos(new_target_pos)
        self.target_node.setColorScale(0.9, 0.1, 0.1, 1)

        # 5. make the green block (Dummy)
        self.dummy_node = self.loader.loadModel("smiley")
        self.dummy_node.reparentTo(self.render)
        self.dummy_node.setScale(target_size / 1.5) 
        self.dummy_node.setPos(new_dummy_pos)
        self.dummy_node.setColorScale(0.1, 0.9, 0.1, 1)

        return id_score
    
    def get_targeted_node(self):
        print("checking for hit")
        self.cTrav.traverse(self.render)
        if self.rayQueue.getNumEntries() > 0:
            self.rayQueue.sortEntries()
            return self.rayQueue.getEntry(0).getIntoNodePath()
        return None
    def get_target_angular_error(self) -> tuple[float, float] | None:
        """Returns (yaw_error, pitch_error) in degrees from crosshair to target.
        Positive yaw = target is to the right; positive pitch = target is above."""
        if self.target_node is None:
            return None
        local_pos = self.camera.getRelativePoint(self.render, self.target_node.getPos(self.render))
        if local_pos.y <= 0:
            return None  # target is behind the camera
        yaw_error   = math.degrees(math.atan2(local_pos.x, local_pos.y))
        pitch_error = math.degrees(math.atan2(local_pos.z, local_pos.y))
        return yaw_error, pitch_error

    def get_target_angular_radius(self, target_size: float) -> float | None:
        """Returns the angular radius of the target in degrees based on its
        physical size and distance from the camera."""
        if self.target_node is None:
            return None
        local_pos = self.camera.getRelativePoint(self.render, self.target_node.getPos(self.render))
        distance = local_pos.length()
        if distance < 1e-6:
            return None
        return math.degrees(math.atan2(target_size / 2.0, distance))

    def get_target_position_error(self) -> tuple[float, float] | None:
        """Returns (yaw_error, pitch_error) in degrees from crosshair to target.
        Positive yaw = target is to the right; positive pitch = target is above."""
        if self.target_node is None:
            return None
        local_pos = self.camera.getRelativePoint(self.render, self.target_node.getPos(self.render))
        if local_pos.y <= 0:
            return None  # target is behind the camera
        yaw_error   = math.degrees(math.atan2(local_pos.x, local_pos.y))
        pitch_error = math.degrees(math.atan2(local_pos.z, local_pos.y))
        return yaw_error, pitch_error

    def draw_force_vector(self, fx: float, fy: float, scale: float = 0.001):
        if hasattr(self, '_force_line_np') and self._force_line_np:
            self._force_line_np.removeNode()
        ls = LineSegs()
        ls.setThickness(2)
        ls.setColor(1, 0.5, 0, 1)  # orange
        # Origin at screen center (0, 0) in aspect2d space
        ls.moveTo(0, 0, 0)
        # fx is horizontal (maps to X in aspect2d), fy is vertical (maps to Z in aspect2d)
        ls.drawTo(fx * scale, 0, -fy * scale)
        self._force_line_np = self.aspect2d.attachNewNode(ls.create())
