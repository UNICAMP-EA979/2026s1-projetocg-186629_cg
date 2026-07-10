import time
from collections import deque

import numpy as np
from numpy.typing import NDArray
from urenderer.node import Camera, Node
from urenderer.renderer import Renderer


class Runtime:
    '''
    Application Runtime, manages the scene graph and application loop
    '''

    def __init__(self, renderer: Renderer, name: str = "MyApplication") -> None:
        '''
        Runtime initilizer.

        Args:
            renderer (Renderer): renderer to render the scene.
            name (str, optional): name of the application. Defaults to "MyApplication".
        '''
        self._renderer = renderer
        self._name = name

        self.scene = Node("scene_root")
        self.camera = Camera()
        self.scene.add_child(self.camera)

    @property
    def _view_matrix(self) -> np.ndarray:
        '''
        View matrix of the scene main camera.

        Returns:
            np.ndarray: 4x4 view matrix
        '''
        view_matrix = np.eye(4)
        node = self.camera
        while node.parent is not None:
            view_matrix = node.model_transform @ view_matrix
            node = node.parent
        view_matrix = np.linalg.inv(view_matrix)

        return view_matrix

    def _update(self, delta_time: float, time_since_start: float) -> None:
        '''
        Execute the application update code

        Args:
            delta_time (float): time since last update
            time_since_start (float): time since application start
        '''
        nodes = deque([self.scene])
        while len(nodes) != 0:
            node = nodes.pop()
            nodes += node.children

            node.update(delta_time, time_since_start)

    def _render(self, capture: bool = False) -> None:
        '''
        Render the scene

        Args:
            capture (bool, optional): if should capture and save the scene frame. Defaults to False.
        '''
        self._renderer.start(self.camera, self._view_matrix, self._name)

        # Traverse the scene tree.
        nodes = deque([(self.scene, self.scene.model_transform)])
        while len(nodes) != 0:
            node, transformation = nodes.pop()

            # Traverse the node children
            for child in node.children:
                """
                Raciocínio:
                    A transformação acumulada do filho é a transformação corrente do
                    pai concatenada com a transformação local do filho:
                        child_transformation = transformation @ child.model_transform
                    Isso aplica primeiro a transformação local do filho, e em seguida
                    a transformação dos antecessores (parent -> world).
                """
                # Create child transformation by concatenating parent and local
                child_transformation = transformation @ child.model_transform

                # Add child to the processing queue
                nodes.append((child, child_transformation))

            self._renderer.render(node, transformation)

        self._renderer.end(capture)

    def iter(self, delta_time: float = 1.0, time_since_start: float = 0.0, capture: bool = False) -> None:
        '''
        Execute one iteration of the application (update+render)

        Args:
            delta_time (float, optional): time since last iteration. Defaults to 1.0.
            time_since_start (float, optional): time since application start. Defaults to 0.0.
            capture (bool, optional): if should save the iteration frame. Defaults to False.
        '''
        self._update(delta_time, time_since_start)
        self._render(capture)

    def loop(self, n: int | None = None, constant_time: bool = False, capture: bool | list[int] | NDArray[np.int32] = False) -> None:
        '''
        Execute the application in a loop.

        Args:
            n (int | None, optional): number of iterations. If None, run non-stop. Defaults to None.
            constant_time (bool, optional): if should use constant times for the application update. Defaults to False.
            capture (bool | list[int], optional): if should capture the rendered frames. If a list, capture the frames with number in the list. Defaults to False.
        '''

        start_time = time.time()
        last_time = time.time()
        current_time = time.time()
        i = 0
        while (n is None or i < n) and not self._renderer.should_stop():

            if constant_time:
                delta_time = 1.0
            else:
                delta_time = last_time-current_time

            capture_frame = False
            if isinstance(capture, list) or isinstance(capture, np.ndarray):
                capture_frame = i in capture
            else:
                capture_frame = capture

            self.iter(delta_time, current_time-start_time, capture_frame)

            i += 1

            last_time = current_time
            current_time = time.time()
            if last_time != current_time:
                print(f"\r {1/(current_time-last_time)} fps",
                      end="", flush=True)
