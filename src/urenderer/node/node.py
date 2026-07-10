import copy
from collections.abc import Iterable
from typing import Callable

import numpy as np
from scipy.spatial.transform import Rotation


#teste de 
class Node:
    """
    Scene node.

    Represents any element that exists in the application scene.
    """

    def __init__(self, name: str = "") -> None:
        """
        Node initializer

        Args:
            name (str, optional): node name. Defaults to "".
        """
        self.name = name

        self.translation: np.ndarray = np.zeros(3)  # Translação
        self.rotation: np.ndarray = np.zeros(3)  # Ângulos da rotação em graus
        self.scale: np.ndarray = np.ones(3)  # Escala

        self.render_data = {}
        self.callbacks: list[Callable[["Node", float, float], None]] = []

        self._children: set[Node] = set()
        self._parent: Node | None = None

    @property
    def model_transform(self) -> np.ndarray:
        """
        The model transformation from object space to world space

        Returns:
            np.ndarray: 4x4 model transformation

        Raciocínio:
            Crio as matrizes de Escala (S), Rotação (R) e Translação (T) e
            concateno na ordem M = T @ R @ S. A rotação é obtida a partir de
            ângulos Euler (`Rotation.from_euler('xyz', ..., degrees=True)`).
            Essa ordem (S depois R depois T) aplica escala no espaço local,
            então rotaciona, e por fim posiciona o objeto no mundo.
        """

        # Scale matrix (homogênea)
        S = np.eye(4)
        S[0, 0] = self.scale[0]
        S[1, 1] = self.scale[1]
        S[2, 2] = self.scale[2]

        # Rotation matrix (from Euler angles in degrees)
        R = np.eye(4)
        R[:3, :3] = Rotation.from_euler('xyz', self.rotation, degrees=True).as_matrix()

        # Translation matrix
        T = np.eye(4)
        T[:3, 3] = self.translation

        # Final transformation: translate * rotate * scale
        final_transformation = T @ R @ S

        return final_transformation

    @property
    def parent(self) -> "Node | None":
        """
        Parent node
        """
        return self._parent

    @property
    def children(self) -> Iterable["Node"]:
        """
        Set of children
        """
        return frozenset(self._children)

    def clone(self) -> "Node":
        """
        Creates a new node with same properties (except for children)

        Returns:
            Node: node clone.
        """
        clone = copy.deepcopy(self)
        clone._children = set()

        if self.parent is not None:
            self.parent.add_child(clone)

        return clone

    def add_child(self, child: "Node") -> None:
        """
        Add a child node to this node

        Args:
            child (Node): child to add
        """
        if child in self._children:
            return

        self._children.add(child)

        if child._parent is not None:
            child._parent._children.remove(child)
        child._parent = self

    def update(self, delta_time: float, time_since_start: float) -> None:
        """
        Execute the application update code for this node

        Args:
            delta_time (float): time since last update
            time_since_start (float): time since application start
        """
        for callback in self.callbacks:
            callback(self, delta_time, time_since_start)
