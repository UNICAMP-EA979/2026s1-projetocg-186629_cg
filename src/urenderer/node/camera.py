import numpy as np

from .node import Node


class Camera(Node):
    """
    Camera node, a perspective camera
    """

    def __init__(self, name: str = "camera") -> None:
        """
        Camera initilizer

        Args:
            name (str, optional): node name. Defaults to "camera".
        """
        super().__init__(name)

        self.near_plane = 1.0
        self.far_plane = 10.0
        self.screen_width = 1920.0
        self.screen_height = 1080.0
        self.vertical_fov = 60.0

    @property
    def projection_matrix(self) -> np.ndarray:
        """
        Camera projection matrix

        Returns:
            np.ndarray: 4x4 projection matrix
        """

        ## SEU CÓDIGO AQUI #####################################################
        # Crie a matriz de projeção utilizando a fórmula

        Raciocínio = """
        Calculo a matriz de projeção perspectiva usando a convenção:
        a = screen_width / screen_height (aspect)
        c = 1 / tan(vertical_fov/2)

        A matriz possui a forma:
            [ c/a,   0,          0,                 0 ]
            [  0,    c,          0,                 0 ]
            [  0,    0,  -(f+n)/(f-n),  -2*f*n/(f-n) ]
            [  0,    0,         -1,                 0 ]
        """

        a = self.screen_width / self.screen_height
        c = 1.0 / np.tan(np.deg2rad(self.vertical_fov) / 2.0)
        n = self.near_plane
        f = self.far_plane

        matrix = np.zeros((4, 4))
        matrix[0, 0] = c / a
        matrix[1, 1] = c
        matrix[2, 2] = -(f + n) / (f - n)
        matrix[2, 3] = -2.0 * f * n / (f - n)
        matrix[3, 2] = -1.0

        #########################################################################

        return matrix
