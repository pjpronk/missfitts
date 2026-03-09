import time
import numpy as np
import serial
import serial.tools.list_ports

from classes.HaplyHAPI import Board, Device, Pantograph, Mechanisms


class HapticDevice:
    def __init__(self, hardware_version=3, reverse_motor_order=False):
        CW = 0
        CCW = 1

        port = self._find_port()

        if port:
            print(f"[HapticDevice]: Board found on port {port}")
            self._board = Board("app", port, 0)
            self._device = Device(5, self._board)
            self._pantograph = Pantograph(hardware_version)
            self._device.set_mechanism(self._pantograph)

            if hardware_version == 3:
                if reverse_motor_order:
                    self._device.add_actuator(2, CCW, 2)
                    self._device.add_actuator(1, CCW, 1)
                    self._device.add_encoder(2, CCW, 82.7, 4880, 2)
                    self._device.add_encoder(1, CCW, 97.3, 4880, 1)
                else:
                    self._device.add_actuator(1, CCW, 2)
                    self._device.add_actuator(2, CCW, 1)
                    self._device.add_encoder(1, CCW, 168, 4880, 2)
                    self._device.add_encoder(2, CCW, 12, 4880, 1)
            else:
                self._device.add_actuator(1, CCW, 2)
                self._device.add_actuator(2, CW, 1)
                self._device.add_encoder(1, CCW, 241, 10752, 2)
                self._device.add_encoder(2, CW, -61, 10752, 1)

            self._device.device_set_parameters()

            start = time.time()
            while True:
                if not self._board.data_available():
                    self._device.set_device_torques(np.zeros(2))
                    self._device.device_write_torques()
                    time.sleep(0.001)
                    if time.time() - start > 5.0:
                        raise RuntimeError("[HapticDevice]: Board present but not providing data.")
                else:
                    print("[HapticDevice]: Ready.")
                    break

            self.connected = True
        else:
            print("[HapticDevice]: No device found, running without haptics.")
            self.connected = False

    def get_position(self) -> tuple[float, float]:
        """Returns endpoint position (x, y) in meters."""
        self._device.device_read_data()
        angles = self._device.get_device_angles()
        pos = self._device.get_device_position(angles)
        return float(pos[0]), float(pos[1])

    def set_force(self, fx: float, fy: float):
        """Sends Cartesian force (fx, fy) in Newtons to the device."""
        self._device.set_device_torques([fx, -fy])
        self._device.device_write_torques()
        time.sleep(0.001)

    def close(self):
        if self.connected:
            self._device.set_device_torques([0.0, 0.0])
            self._device.device_write_torques()
            time.sleep(0.001)

    def _find_port(self):
        for p in serial.tools.list_ports.comports():
            try:
                s = serial.Serial(p.device)
                s.close()
                if p.description[:12] == "Arduino Zero":
                    print(p.description[:12])
                    return p.device
            except (OSError, serial.SerialException):
                pass
        return None
