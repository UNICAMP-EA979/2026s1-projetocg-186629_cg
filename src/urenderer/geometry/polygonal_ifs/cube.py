import numpy as np


def get_ifs_cube() -> dict:
    '''
    Get Indexed Face Set of a cube

    Returns:
        dict: node render data for a cube.
    '''
    geometry_vertex = np.array([
        [0, 0, 0],  # A0
        [1, 0, 0],  # B1
        [1, 1, 0],  # C2
        [0, 1, 0],  # D3
        [0, 0, 1],  # E4
        [1, 0, 1],  # F5
        [1, 1, 1],  # G6
        [0, 1, 1],  # H7
    ], dtype=np.float64)

    geometry_vertex -= np.array([0.5, 0.5, 0.5])

    geometry_index = [
        # Back
        [0, 1, 2],
        [0, 2, 3],
        # Front
        [4, 5, 6],
        [4, 6, 7],
        # Floor
        [0, 1, 5],
        [0, 5, 4],
        # Right
        [1, 2, 6],
        [1, 6, 5],
        # Ceil
        [2, 3, 7],
        [2, 7, 6],
        # Left
        [3, 0, 4],
        [3, 4, 7]
    ]

    return {"geometry_vertex": geometry_vertex, "geometry_index": geometry_index}
