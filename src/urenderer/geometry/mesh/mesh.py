from ctypes import c_void_p
from typing import Optional

import numpy as np
from numpy.typing import NDArray
from OpenGL import GL


def check_dtype(name: str,
                value: np.ndarray | None,
                dtype: type) -> None:
    '''
    Checks the dtype of the array. Raises an exception if wrong.

    Ignores None arrays

    Args:
        name (str): name of the array (for exception message)
        value (np.ndarray | None): array to check
        dtype (type): expected dtype

    Raises:
        ValueError: if value.dtype != dtype
    '''
    if value is not None and value.dtype != dtype:
        raise ValueError(
            f"{name} dtype must be {np.dtype(dtype).name}, dtype is {value.dtype}")


class Mesh:
    '''
    Stores a Mesh for OpenGL rendering.
    '''

    def __init__(self,
                 vertex: NDArray[np.float32],
                 index: NDArray[np.uint32],
                 uv: NDArray[np.float32],
                 color: Optional[NDArray[np.float32]] = None,
                 normal: Optional[NDArray[np.float32]] = None) -> None:
        '''
        Mesh constructor.

        Arrays may be on (n, m) shape or (n*m) shape, where n is the number of vertices

        Args:
            vertex (NDArray[np.float32]): vertex array, (n, 3).
            index (NDArray[np.uint32]): index array, (e, 3), e is the number of elements.
            uv (NDArray[np.float32]): uv array, (n, 2).
            color (Optional[NDArray[np.float32]], optional): vertex color, (n, 3). Defaults to None.
            normal (Optional[NDArray[np.float32]], optional): vertex normal, (n, 3). Defaults to None.

        Raises:
            ValueError: if any parameter dtype is wrong.
        '''

        check_type_dict = {"vertex": vertex,
                           "uv": uv,
                           "color": color,
                           "normal": normal}
        for name, value in check_type_dict.items():
            if value is not None and value.dtype != np.float32:
                raise ValueError(
                    f"{name} dtype must be float32, dtype is {value.dtype}")

        self._vao = GL.glGenVertexArrays(1)
        self._vbo = GL.glGenBuffers(1)
        self._ebo = GL.glGenBuffers(1)

        self.index = index

        self._vertex = vertex
        self._index = index
        self._uv = uv
        self._color = color
        self._normal = normal
        self._update_vbo()

    def _update_ebo(self):
        '''
        Updates the mesh's element array buffer (EBO).

        The EBO contains the indices of each triangle.
        See https://wikis.khronos.org/opengl/Vertex_Specification#Index_buffers
        '''
        ## SEU CÓDIGO AQUI ######################################################
        # Faça bind do VAO e EBO e envie os dados do EBO

        GL.glBindVertexArray(self._vao)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER,
                        self._index.nbytes, self._index.flatten(), GL.GL_STATIC_DRAW)
        #########################################################################

    def _update_vbo(self):
        '''
        Updates the mesh's vertex buffer object (VBO).

        The VBO is stored in a in a standardized format for all meshes:
        [x, y, z, u, v, r, g, b , nx, ny, nz]

        Where x, y, z is the vertex position (location=0),
              u, v is the UV positions (location=1),
              r, g, b is the vertex color (location=2),
              nx, ny, nz is the vertex normal (location=3).

        The vertex color and vertex normal are optional.

        See https://wikis.khronos.org/opengl/Vertex_Specification#Vertex_Buffer_Object.

        Raises:
            ValueError: _description_
        '''
        # 0=vertex (3), 1=uv (2), 2=color (3), 3=normal (3)

        ## SEU CÓDIGO AQUI ######################################################
        # Bind the VAO and VBO
        GL.glBindVertexArray(self._vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._vbo)

        #########################################################################

        check_type_dict = {"vertex": self._vertex,
                           "uv": self._uv,
                           "color": self._color,
                           "normal": self._normal}
        for name, value in check_type_dict.items():
            if value is not None and value.dtype != np.float32:
                raise ValueError(
                    f"{name} dtype must be float32, dtype is {value.dtype}")

        # Formata os dados do buffer
        components = [self._vertex.reshape(-1, 3), self._uv.reshape(-1, 2)]
        n_item = 3+2  # vertex+uv

        if self._color is not None:
            components.append(self._color.reshape(-1, 3))
            n_item += 3
        if self._normal is not None:
            components.append(self._normal.reshape(-1, 3))
            n_item += 3

        data = np.hstack(components, dtype=np.float32)

        ## SEU CÓDIGO AQUI ######################################################
        # Envia os dados para o buffer
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        data.nbytes, data, GL.GL_STATIC_DRAW)

        # Configura os atributos do buffer
        float_size = np.dtype(np.float32).itemsize
        stride = n_item * float_size
        # Vertex
        GL.glVertexAttribPointer(0, 3,
                                 GL.GL_FLOAT, GL.GL_FALSE,
                                 stride,
                                 c_void_p(0))
        GL.glEnableVertexAttribArray(0)

        # UV
        GL.glVertexAttribPointer(1, 2,
                                 GL.GL_FLOAT, GL.GL_FALSE,
                                 stride,
                                 c_void_p(3*float_size))
        GL.glEnableVertexAttribArray(1)

        start = 3+2  # uv start + uv size
        if self._color is not None:
            GL.glVertexAttribPointer(2, 3,
                                     GL.GL_FLOAT, GL.GL_FALSE,
                                     stride,
                                     c_void_p(start*float_size))
            GL.glEnableVertexAttribArray(2)

            start += 3

        if self._normal is not None:
            GL.glVertexAttribPointer(3, 3,
                                     GL.GL_FLOAT, GL.GL_FALSE,
                                     stride,
                                     c_void_p(start*float_size))
            GL.glEnableVertexAttribArray(3)

        #########################################################################

        # Unbind the VAO
        GL.glBindVertexArray(0)

    def draw(self) -> None:
        '''
        Draws the stored mesh
        '''
        ## SEU CÓDIGO AQUI ######################################################
        # Realiza o bind do VAO ao contexto e desenha a geometria contida nele

        GL.glBindVertexArray(self._vao)
        GL.glDrawElements(GL.GL_TRIANGLES, self._n_element,
                          GL.GL_UNSIGNED_INT, None)

        #########################################################################

    @property
    def index(self) -> NDArray[np.uint32]:
        return self._index

    @index.setter
    def index(self, value: NDArray[np.uint32]) -> None:
        if value.dtype != np.uint32:
            raise ValueError(
                f"index dtype must be uint32, dtype is {value.dtype}")

        self._index = value
        self._n_element = value.size

        self._update_ebo()

    @property
    def vertex(self):
        return self._vertex

    @vertex.setter
    def vertex(self, value: NDArray[np.float32]):
        check_dtype("vertex", value, np.float32)
        self._vertex = value
        self._update_vbo()

    @property
    def uv(self):
        return self._uv

    @uv.setter
    def uv(self, value: NDArray[np.float32]):
        check_dtype("uv", value, np.float32)
        self._uv = value
        self._update_vbo()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value: NDArray[np.float32]):
        check_dtype("color", value, np.float32)
        self._color = value
        self._update_vbo()

    @property
    def normal(self):
        return self._normal

    @normal.setter
    def normal(self, value: NDArray[np.float32]):
        check_dtype("normal", value, np.float32)
        self._normal = value
        self._update_vbo()
