import copy

import numpy as np
from OpenGL import GL

from .shader import Shader
from .texture import Texture


class Material:
    '''
    Stores a material for OpenGL rendering

    A Material is a shader along with the data it uses (uniforms and textures).
    '''

    def __init__(self, shader: Shader) -> None:
        '''
        Material constructor

        Args:
            shader (Shader): material shader
        '''
        self.shader = shader

        self.textures: dict[int, Texture] = {}

        self.uniforms: dict[str, bool | int | float | np.ndarray] = {}

    def set_texture(self, unit: int, name: str, texture: Texture) -> None:
        '''
        Set a texture of the material

        Args:
            unit (int): texture unit to set.
            name (str): name of the texture variable.
            texture (Texture): texture to use.
        '''
        self.textures[unit] = texture
        self.set_uniform(name, unit)

    def set_uniform(self, name: str, value: bool | int | float | np.ndarray) -> None:
        '''
        Set a uniform of the material

        Args:
            name (str): name of the uniform variable.
            value (bool | int | float | np.ndarray): value to use.
        '''
        self.uniforms[name] = value

    def use(self) -> None:
        '''
        Use the material, activating it in the current rendering state
        '''
        self.shader.use()

        # Set the textures
        for texture_unit, texture in self.textures.items():
            GL.glActiveTexture(int(GL.GL_TEXTURE0)+texture_unit)
            texture.bind_at_unit(texture_unit)

        # Set the uniforms
        for name, value in self.uniforms.items():
            self.shader.set_uniform(name, value)

    def clone(self) -> "Material":
        clone = copy.deepcopy(self)
        return clone
