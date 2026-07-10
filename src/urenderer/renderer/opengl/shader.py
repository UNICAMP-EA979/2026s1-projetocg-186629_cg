import os
import re
from collections import defaultdict
from typing import Any, cast

import numpy as np
from OpenGL import GL

from . import shader_library

SHADER_LIBRARY_PATH = os.path.dirname(shader_library.__file__)


def check_program_linking(shader_program: int) -> None:
    '''
    Checks for program compilation error

    Args:
        shader_program (int): program to check

    Raises:
        RuntimeError: if there is a linking error
    '''
    success = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
    if not success:
        info_log = GL.glGetProgramInfoLog(shader_program)
        raise RuntimeError("Program Linking Failed\n\n" +
                           info_log.decode("utf-8"))


class Shader:
    '''
    Stores an OpenGL shader program
    '''

    _program_cache: dict[str, Any] = {}

    def __init__(self, vertex_path: str, fragment_path: str) -> None:
        '''
        Shader constructor

        Args:
            vertex_path (str): path of the vertex shader file.
            fragment_path (str): path of the fragment shader file
        '''

        self._shader_ranges: dict[Any, list[str]] = {}

        # Lê os arquivos
        with open(vertex_path, "r") as file:
            vertex_shader_source = file.read()

            n_line = len(vertex_shader_source.split("\n"))
            self._shader_ranges[GL.GL_VERTEX_SHADER] = n_line * \
                [os.path.basename(vertex_path)]

            vertex_shader_source = self._preprocess(vertex_shader_source,
                                                    GL.GL_VERTEX_SHADER)
        with open(fragment_path, "r") as file:
            fragment_shader_source = file.read()

            n_line = len(fragment_shader_source.split("\n"))
            self._shader_ranges[GL.GL_FRAGMENT_SHADER] = n_line * \
                [os.path.basename(fragment_path)]

            fragment_shader_source = self._preprocess(fragment_shader_source,
                                                      GL.GL_FRAGMENT_SHADER)

        for shader_type in [GL.GL_VERTEX_SHADER, GL.GL_FRAGMENT_SHADER]:
            file_position = defaultdict(lambda: 1)
            for i in range(len(self._shader_ranges[shader_type])):
                file_name = self._shader_ranges[shader_type][i]
                position = file_position[file_name]
                self._shader_ranges[shader_type][i] += f":{position}"
                file_position[file_name] += 1

        # Checa se o programa já foi compilado e linkado
        full_source = vertex_shader_source+fragment_shader_source
        if full_source not in Shader._program_cache:
            # Compila o programa ainda não cacheado

             ## SEU CÓDIGO AQUI ######################################################
            # Cria e compila o vertex shader
            # Raciocínio: Criamos um shader vazio do tipo VERTEX, fornecemos o código fonte
            # e compilamos. O resultado é um identificador do shader compilado.
            vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
            GL.glShaderSource(vertex_shader, vertex_shader_source)
            GL.glCompileShader(vertex_shader)
            #########################################################################

            vertex_shader = cast(int, vertex_shader)
            self._check_shader_compilation(vertex_shader,
                                           GL.GL_VERTEX_SHADER,
                                           "VERTEX")

            ## SEU CÓDIGO AQUI ######################################################
            # Cria e compila o fragment shader
            # Raciocínio: Processo idêntico ao vertex shader, mas para FRAGMENT shader.
            # Este shader define a cor final de cada pixel (fragmento).
            fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
            GL.glShaderSource(fragment_shader, fragment_shader_source)
            GL.glCompileShader(fragment_shader)
            #########################################################################

            fragment_shader = cast(int, fragment_shader)
            self._check_shader_compilation(fragment_shader,
                                           GL.GL_FRAGMENT_SHADER,
                                           "FRAGMENT")

            ## SEU CÓDIGO AQUI ######################################################
            # Cria e linka o programa
            # Raciocínio: O programa é um contêiner que combina múltiplos shaders.
            # Attachamos os shaders compilados e linkamos. O resultado é um programa
            # que pode ser usado para renderizar.
            shader_program = GL.glCreateProgram()
            GL.glAttachShader(shader_program, vertex_shader)
            GL.glAttachShader(shader_program, fragment_shader)
            GL.glLinkProgram(shader_program)
            #########################################################################

            shader_program = cast(int, shader_program)
            check_program_linking(shader_program)

            GL.glDeleteShader(vertex_shader)
            GL.glDeleteShader(fragment_shader)

            Shader._program_cache[full_source] = shader_program

        self.shader_program = Shader._program_cache[full_source]
        self.uniform_location: dict[str, int] = {}

        del self._shader_ranges

    def use(self) -> None:
        '''
        Use the shader, activating it in the current rendering state
        '''
        ## SEU CÓDIGO AQUI ######################################################
        # Usa o programa compilado e linkado anteriormente no contexto atual
        # Raciocínio: glUseProgram ativa o programa para todos os próximos comandos
        # de renderização, até que outro programa seja ativado.
        GL.glUseProgram(self.shader_program)
        #########################################################################

    def _get_uniform_location(self, name: str) -> int:
        '''
        Get to location of a uniform

        Args:
            name (str): name of the uniform

        Returns:
            int: uniform location
        '''

        # Cacheia o local da uniform para melhor performance
        if name not in self.uniform_location:
            self.uniform_location[name] = GL.glGetUniformLocation(
                self.shader_program, name)

        return self.uniform_location[name]

    def set_uniform(self, name: str, value: bool | int | float | np.ndarray) -> None:
        '''
        Set the value of a uniform

        Args:
            name (str): name of the uniform
            value (bool | int | float | np.ndarray): value to set

        Raises:
            ValueError: if the value type is not supported
        '''
        location = self._get_uniform_location(name)

        if isinstance(value, bool):
            GL.glUniform1i(location, int(value))
        elif isinstance(value, int):
            GL.glUniform1i(location, value)
        elif isinstance(value, float):
            GL.glUniform1f(location, value)
        elif isinstance(value, np.ndarray):
            if value.dtype == np.float32 and value.shape == (4, 4):
                GL.glUniformMatrix4fv(location,
                                      1,  # quantas matrizes
                                      GL.GL_FALSE,
                                      value.flatten(order="F"))
            elif value.dtype == np.float32 and value.shape == (3,):
                GL.glUniform3fv(location,
                                1,  # quantas matrizes
                                value.flatten(order="F"))

            else:
                raise ValueError(
                    f"Value type {type(value)} with dtype {value.dtype} and shape {value.shape} not supported")
        else:
            raise ValueError(f"Value type {type(value)} not supported")

    def _preprocess(self, shader_code: str,
                    shader_type: Any) -> str:
        while "#include" in shader_code:
            code_lines = shader_code.split("\n")

            offset = 0

            for i, line in enumerate(code_lines):
                if "#include" in line:
                    line = line.split(" ")
                    file_name = line[1]
                    file_name = file_name.replace("\"", "")
                    file_path = os.path.join(SHADER_LIBRARY_PATH, file_name)

                    with open(file_path, "r") as file:
                        library_code = file.read()

                    code_lines[i] = library_code

                    n_line = len(library_code.split("\n"))
                    index = i+offset
                    self._shader_ranges[shader_type][index:index] = n_line*[file_name]
                    offset += n_line

            shader_code = "\n".join(code_lines)

        return shader_code

    def _replace_error_location(self,
                                location: str,
                                shader_type) -> str:
        if "(" in location:
            line = location.split("(")[1].split(")")[0]
            line = int(line)
        else:
            location = location.removeprefix("ERROR: ")
            location = location.removesuffix(":")
            line = location.split(":")[-1]
            line = int(line)

        return self._shader_ranges[shader_type][line]

    def _check_shader_compilation(self, shader: int,
                                  shader_type: Any,
                                  name: str = "") -> None:
        '''
        Checks for shader compilation errors

        Args:
            shader (int): shader to check
            name (str, optional): Name of the shader for exception. Defaults to "".

        Raises:
            RuntimeError: if there is a compilation error
        '''
        success = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        if not success:
            info_log: str = GL.glGetShaderInfoLog(shader).decode("utf-8")

            info_log = re.sub(
                r'0\([0-9]+\)',
                lambda m: self._replace_error_location(
                    m.group(0), shader_type),
                info_log
            )

            info_log = re.sub(
                r'ERROR: 0:[0-9]+:',
                lambda m: self._replace_error_location(
                    m.group(0), shader_type),
                info_log
            )

            raise RuntimeError(f"Shader Compilation Failed - {name}\n\n" +
                               info_log)
