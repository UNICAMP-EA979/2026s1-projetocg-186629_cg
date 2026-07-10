import numpy as np

from urenderer.geometry.polygonal_ifs import get_ifs_cube

from .mesh import Mesh


def get_mesh_cube() -> Mesh:
    '''
    Creates a cube in mesh representation

    Returns:
        Mesh: cube mesh
    '''

    # Dados incorretos
    data = get_ifs_cube()
    vertex: np.ndarray = data["geometry_vertex"].astype(np.float32)
    index = np.array(data["geometry_index"], dtype=np.uint32)

    uv = np.array([
        [0, 0],  # A
        [1, 0],  # B
        [0, 0],  # C
        [1, 1],  # D
        [0, 1],  # E
        [1, 1],  # F
        [1, 0],  # G
        [0, 0],  # H
    ], dtype=np.float32)

    # Dados corretos
    # Observe como são utilizados 24 vértices, cada face é representada com 4
    # vértices independentes das outras faces, pois é impossível mapear
    # a UV corretamente utilizando apenas 8 vértices para o cubo inteiro.

    vertex = np.array([-0.5, -0.5, -0.5,  # 0
                       0.5, -0.5, -0.5,  # 1
                       0.5,  0.5, -0.5,  # 2
                       -0.5,  0.5, -0.5,  # 3

                       -0.5, -0.5,  0.5,  # 4
                       0.5, -0.5,  0.5,  # 5
                       0.5,  0.5,  0.5,  # 6
                       -0.5,  0.5,  0.5,  # 7

                       -0.5,  0.5,  0.5,  # 8
                       -0.5,  0.5, -0.5,  # 9
                       -0.5, -0.5, -0.5,  # 10
                       -0.5, -0.5,  0.5,  # 11

                       0.5,  0.5,  0.5,  # 12
                       0.5,  0.5, -0.5,  # 13
                       0.5, -0.5, -0.5,  # 14
                       0.5, -0.5,  0.5,  # 15

                       -0.5, -0.5, -0.5,  # 16
                       0.5, -0.5, -0.5,  # 17
                       0.5, -0.5,  0.5,  # 18
                       -0.5, -0.5,  0.5,  # 19

                       -0.5,  0.5, -0.5,  # 20
                       0.5,  0.5, -0.5,  # 21
                       0.5,  0.5,  0.5,  # 22
                       -0.5,  0.5,  0.5,  # 23
                       ], dtype=np.float32)

    index = np.array([0, 1, 2,
                      2, 3, 0,

                      4, 5, 6,
                      6, 7, 4,

                      8, 9, 10,
                      10, 11, 8,

                      12, 13, 14,
                      14, 15, 12,

                      16, 17, 18,
                      18, 19, 16,

                      20, 21, 22,
                      22, 23, 20
                      ],
                     dtype=np.uint32)

    uv = np.array([0.0, 0.0,
                   1.0, 0.0,
                   1.0, 1.0,
                   0.0, 1.0,],
                  dtype=np.float32)
    uv = np.tile(uv, 6)

    normal = np.array([
        0.0,  0.0, -1.0,
        0.0,  0.0, -1.0,
        0.0,  0.0, -1.0,
        0.0,  0.0, -1.0,

        0.0,  0.0,  1.0,
        0.0,  0.0,  1.0,
        0.0,  0.0,  1.0,
        0.0,  0.0,  1.0,

        -1.0,  0.0,  0.0,
        -1.0,  0.0,  0.0,
        -1.0,  0.0,  0.0,
        -1.0,  0.0,  0.0,

        1.0,  0.0,  0.0,
        1.0,  0.0,  0.0,
        1.0,  0.0,  0.0,
        1.0,  0.0,  0.0,

        0.0, -1.0,  0.0,
        0.0, -1.0,  0.0,
        0.0, -1.0,  0.0,
        0.0, -1.0,  0.0,

        0.0,  1.0,  0.0,
        0.0,  1.0,  0.0,
        0.0,  1.0,  0.0,
        0.0,  1.0,  0.0,
    ], dtype=np.float32)

    return Mesh(vertex, index, uv, normal=normal)
