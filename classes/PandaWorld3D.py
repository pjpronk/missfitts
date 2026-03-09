from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    WindowProperties,
    CardMaker,
    ClockObject,
)
import math


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

        self.setup_lights()
        self.create_floor()
        self.create_wall_box()
        self.create_gun_3d()
        self.create_crosshair()

        self.mouse_dx = 0.0
        self.mouse_dy = 0.0

        self.center_mouse()

        self.taskMgr.add(self._read_mouse, "_read_mouse")
        self.taskMgr.add(self.animate_gun, "animate_gun")

    def setup_lights(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.4, 0.4, 0.4, 1))
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

