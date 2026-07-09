import numpy as np


def get_ifs_pyramid() -> dict:
    '''
    Get Indexed Face Set of a pyramid

    Returns:
        dict: node render data for a pyramid.
    '''

    ## SEU CÓDIGO AQUI #####################################################
    # Escreva os vértices e índices para formar uma pirâmide de base triangular
    # Ela não precisa ser regular

    geometry_vertex = np.array([
        [-0.5, -0.5, 0],
        [0.5, -0.5, 0],
        [0, 1, 0],
        [0, 0, 1]
    ], dtype=np.float64)

    geometry_index = [
        [0, 1, 2],
        [0, 1, 3],
        [1, 2, 3],
        [2, 0, 3]
    ]

    #########################################################################

    return {"geometry_vertex": geometry_vertex, "geometry_index": geometry_index}
