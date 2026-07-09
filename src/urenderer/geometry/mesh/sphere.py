import numpy as np
from icosphere import icosphere

from .mesh import Mesh


def get_mesh_sphere() -> Mesh:
    '''
    Creates a icosphere in Mesh representation

    Returns:
        Mesh: icosphere mesh
    '''
    vertices, faces = icosphere(7)

    vertices = vertices.astype(np.float32)
    faces = faces.astype(np.uint32)

    uv = np.empty([vertices.shape[0], 2], dtype=np.float32)
    normals = np.empty_like(vertices)

    for i in range(vertices.shape[0]):
        x = vertices[i, 0]
        y = vertices[i, 1]
        z = vertices[i, 2]

        u = 0.5 + np.atan2(z, x) / (2*np.pi)
        v = 0.5 - np.asin(y) / np.pi

        uv[i, 0] = u
        uv[i, 1] = v

        length = np.sqrt(x*x + y*y + z*z)

        normals[i, 0] = x / length
        normals[i, 1] = y / length
        normals[i, 2] = z / length

    return Mesh(vertices, faces, uv, normal=normals)
