import enum
from typing import Optional

import numpy as np
from scipy.spatial.transform import Rotation

from .node import Node


class LightType(enum.Enum):
    DIRECTIONAL = 1
    POINT = 2


class Light(Node):
    def __init__(self, light_type: LightType, name: Optional[str] = None) -> None:
        '''
        Light initilizer

        Args:
            name (str, optional): node name.
        '''
        if name is None:
            name = "light_"+light_type.name.lower()

        super().__init__(name)

        self.light_type = light_type
        self.light_color = np.array([1, 1, 1], np.float32)
        self.light_reference_distance = 1.0
        self.light_intensity = 1.0

    @property
    def light_direction(self) -> np.ndarray:
        R = np.eye(4)
        R[:3, :3] = Rotation.from_euler(
            "xyz", self.rotation, degrees=True).as_matrix()

        direction = R@np.array([0, 1, 0, 0], np.float32)
        return direction[:3].astype(np.float32)
