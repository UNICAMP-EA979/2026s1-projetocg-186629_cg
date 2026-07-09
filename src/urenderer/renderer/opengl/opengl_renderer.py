import ctypes
from concurrent.futures import ProcessPoolExecutor
from typing import TYPE_CHECKING, Any, TypeAlias, cast

import cv2 as cv
import glfw
import numpy as np
from OpenGL import GL

from urenderer.geometry.mesh import Mesh
from urenderer.node import Camera, Light, LightType, Node
from urenderer.renderer.renderer import Renderer
from urenderer.utils import get_filename_unique

from .material import Material

if TYPE_CHECKING:
    GLFWWindow = Any
else:
    GLFWWindow = ctypes.POINTER(glfw._GLFWwindow)


def save_frame(path: str, frame: np.ndarray) -> None:
    '''
    Save a frame

    Args:
        path (str): path to save
        frame (np.ndarray): frame
    '''
    cv.imwrite(path, frame)


class OpenGLRenderer(Renderer):
    '''
    Renderer using OpenGL
    '''

    def __init__(self, screen_width: int, screen_height: int) -> None:
        '''
        OpenGLRenderer initializer.

        Args:
            screen_width (int): screen width
            screen_height (int): screen height
            show (bool, optional): if should show the rendered frame. Defaults to True.
        '''
        super().__init__(screen_width, screen_height)
        self._executor = ProcessPoolExecutor(max_workers=1)

        ## SEU CÓDIGO AQUI ######################################################
        # Inicializa o GLFW, core profile e OpenGL 3.3
        # Raciocínio: GLFW é a biblioteca para criar janelas e contextos OpenGL.
        # Configuramos para usar OpenGL 3.3 Core Profile, que é mais moderno e seguro.
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        # Configurar janela invisível para ambientes CI/headless
        import os
        if os.environ.get('CI') or os.environ.get('DISPLAY') is None:
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        #########################################################################

        ## SEU CÓDIGO AQUI ######################################################
        # Cria a janela, associando ela ao contexto
        # e configurando o tamanho dela no OpenGl
        # Raciocínio: glfw.create_window cria a janela com as dimensões especificadas.
        # glfw.make_context_current torna o contexto OpenGL da janela ativo para essa thread.
        # glfw.swap_interval(1) ativa vsync para evitar tearing.
        # GL.glViewport configura a área de desenho.
        window = glfw.create_window(screen_width, screen_height, "MyApp", None, None)
        glfw.make_context_current(window)
        glfw.swap_interval(1)
        GL.glViewport(0, 0, screen_width, screen_height)
        import sys
        w, h = glfw.get_window_size(window)
        fw, fh = glfw.get_framebuffer_size(window)
        sys.stderr.write(f"DEBUG_WINDOW_SIZE: {w}x{h} FB: {fw}x{fh}\n")
        sys.stderr.flush()
        #########################################################################

        ## SEU CÓDIGO AQUI ######################################################
        # Habilite o uso de GL_FRAMEBUFFER_SRGB para convertor cores para sRGB
        # 
        # Explicação: Quando ativo, o framebuffer converte automaticamente
        # valores RGB lineares para sRGB (gamma correction) antes de exibir.
        # Sem isso, as cores aparecerão muito claras no monitor.
        # 
        # Processo:
        # 1. Calculamos cor em RGB linear (nossos shaders)
        # 2. GL_FRAMEBUFFER_SRGB converte automaticamente: RGB → sRGB
        # 3. Monitor exibe a cor corrigida
        GL.glEnable(GL.GL_FRAMEBUFFER_SRGB)
        #########################################################################

        glfw.set_framebuffer_size_callback(
            window, self._framebuffer_size_callback)

        GL.glEnable(GL.GL_DEPTH_TEST)

        self._window = cast(GLFWWindow, window)
        
        # Create FBO for offscreen rendering to ensure exact resolution
        self._fbo = GL.glGenFramebuffers(1)
        self._color_tex = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._color_tex)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_SRGB8_ALPHA8, screen_width, screen_height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        
        self._depth_rbo = GL.glGenRenderbuffers(1)
        GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self._depth_rbo)
        GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_DEPTH24_STENCIL8, screen_width, screen_height)
        
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self._color_tex, 0)
        GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_STENCIL_ATTACHMENT, GL.GL_RENDERBUFFER, self._depth_rbo)
        
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        if status != GL.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Framebuffer not complete: {status}")
            
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        self.background_color = np.array([1.0, 0.0, 1.0, 1.0])

        self.ambient_color = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        GL.glDisable(GL.GL_DITHER)

    def _framebuffer_size_callback(self, window: GLFWWindow,
                                   width: int, height: int):
        '''
        Callback for a change in the framebuffer size

        Args:
            window (GLFWWindow): window with size change
            width (int): new width
            height (int): new heigth
        '''
        GL.glViewport(0, 0, width, height)

    def start(self, camera: Camera, view_matrix: np.ndarray, name: str) -> None:
        '''
        Start the frame rendering

        Args:
            camera (Camera): current camera.
            view_matrix (np.ndarray): camera view matrix.
            name (str): name of the application
        '''
        super().start(camera, view_matrix, name)
        self._view_matrix = view_matrix
        self._projection_matrix = camera.projection_matrix
        self._name = name
        self._lights: list[dict[str, Light | np.ndarray]] = []

        glfw.set_window_title(self._window, name)

       ## SEU CÓDIGO AQUI ######################################################
        # Limpe os buffers de cor e profundidade (COLOR_BUFFER e DEPTH_BUFFER)
        # Para o de cor, utilize a cor self.background_color
        # Raciocínio: glClearColor define a cor usada para limpar.
        # glClear limpa os buffers especificados com essa cor.
        # Limpar profundidade é essencial para depth testing correto.
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._fbo)
        GL.glViewport(0, 0, self.screen_width, self.screen_height)
        GL.glClearColor(self.background_color[0], self.background_color[1], 
                       self.background_color[2], self.background_color[3])
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        #########################################################################

    def validate(self, node: Node, model_transformation: np.ndarray) -> bool:
        '''
        Validate a node for rendering.

        Check if the node is compatible to be rendered with this renderer.

        Args:
            node (Node): node to validate.

        Returns:
            bool: True if the node is valid
        '''
        if isinstance(node, Light):
            dummy = np.zeros(4)
            dummy[-1] = 1
            position = model_transformation@dummy
            position = position[:3].astype(np.float32)

            self._lights.append(
                {"node": node, "position": position})
        return ("material" in node.render_data and
                "mesh" in node.render_data)

    def render_valid_node(self, node: Node, model_transformation: np.ndarray):
        '''
        Renders a validated node

        Args:
            node (Node): node to render
            model_transformation (np.ndarray): node model transformation in the scene
        '''
        material: Material = node.render_data["material"]
        mesh: Mesh = node.render_data["mesh"]

        material.use()

        ## SEU CÓDIGO AQUI ######################################################
        # Defina as uniforms 'modelTransformation', 'viewTransformation' e
        # 'projectionMatrix' do material.shader, as matrizes de transformação de
        # coordenadas 4x4.
        #
        # Utilize o método set_uniform do shader, pois não queremos alterar a
        # uniform para todo uso do material.
        #
        # Atente-se que os valores precisam ser convertidos para np.float32
        # Raciocínio: As matrizes de transformação são essenciais para converter
        # coordenadas do espaço local do objeto para o espaço de projeção da câmera.
        # model -> world -> view -> projection space.
        material.shader.set_uniform("modelTransformation", model_transformation.astype(np.float32))
        material.shader.set_uniform("viewTransformation", self._view_matrix.astype(np.float32))
        material.shader.set_uniform("projectionMatrix", self._projection_matrix.astype(np.float32))
        #########################################################################

        ## SEU CÓDIGO AQUI ######################################################
        # Defina a uniform lights para os valores correspondetes de cada luz.
        #
        # As luzes precisam ser enviadas sequencialmente ([luz0, luz1, UNDEFINED, UNDEFINED, ...])
        # Você pode alterar o valor da uniforme 'type' da light 0 usando: 'light[0].type'.
        #
        # Utilize o método set_uniform do shader

        # Iterar sobre todas as luzes que foram processadas pelo validate()
        for i, light_info in enumerate(self._lights):
            light = cast(Light, light_info["node"])
            light_position = cast(np.ndarray, light_info["position"])
             
            # ================================================================
            # ENVIAR TIPO DE LUZ
            # ================================================================
            # O tipo de luz (LIGHT_DIRECTIONAL=1 ou LIGHT_POINT=2) é necessário
            # para o shader saber qual fórmula usar (atenuação, direção, etc)
            # light.light_type é um enum, então usamos .value para obter o int
            material.shader.set_uniform(f"lights[{i}].type", int(light.light_type.value))
             
            # ================================================================
            # ENVIAR COR × INTENSIDADE
            # ================================================================
            # Multiplicamos a cor base pela intensidade da luz
            # Exemplo: cor=[1,0,0] (vermelho) × intensidade=2.0 = [2,0,0]
            # Um valor > 1.0 significa luz super brilhante (HDR)
            # 
            # Nota: Combinamos em um único envio para eficiência
            light_color_with_intensity = light.light_color * light.light_intensity
            material.shader.set_uniform(f"lights[{i}].color", 
                                       light_color_with_intensity.astype(np.float32))
             
            # ================================================================
            # ENVIAR DADOS ESPECÍFICOS DO TIPO DE LUZ
            # ================================================================
             
            if light.light_type == LightType.DIRECTIONAL:
                # ============================================================
                # LUZ DIRECIONAL: Enviar direção normalizada
                # ============================================================
                # A direção foi calculada a partir da rotação do nó
                # light.light_direction já retorna um vetor normalizado
                # Este vetor aponta na direção que a luz "emite"
                material.shader.set_uniform(f"lights[{i}].direction", 
                                           light.light_direction.astype(np.float32))
                 
            elif light.light_type == LightType.POINT:
                # ============================================================
                # LUZ PONTUAL: Enviar posição e distância de referência
                # ============================================================
                # light_position: Já foi transformada para world space em validate()
                # Esta é a posição da lâmpada no mundo
                material.shader.set_uniform(f"lights[{i}].position", 
                                           light_position.astype(np.float32))
                 
                # reference_distance: Distância onde a atenuação = 1.0
                # Valores típicos: 1.0 (padrão) até 10.0 (luz muito intensa)
                material.shader.set_uniform(f"lights[{i}].reference_distance", 
                                           float(light.light_reference_distance))
         
        # ====================================================================
        # MARCAR FIM DO ARRAY DE LUZES
        # ====================================================================
        # O shader itera sobre o array lights[] até encontrar type==LIGHT_UNSET
        # Por isso, precisamos marcar o primeiro slot vazio como inválido
        if len(self._lights) < 10:  # MAX_LIGHT = 10
            # Enviar LIGHT_UNSET no primeiro slot vazio
            # Constante: LIGHT_UNSET = 0
            material.shader.set_uniform(f"lights[{len(self._lights)}].type", 0)
         
        #########################################################################

        ## SEU CÓDIGO AQUI ######################################################
        # Defina a uniform ambientColor para self.ambient_color
        #
        # Utilize o método set_uniform do shader
        material.shader.set_uniform("ambientColor", self.ambient_color)
        #########################################################################

        mesh.draw()

    def end(self, capture: bool = False):
        '''
        Ends the frame rendering

        Args:
            capture (bool, optional): if should save the current frame. Defaults to False.
        '''
        super().end(capture)

        if capture:
            GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)

            frame_data = GL.glReadPixels(0,  # first pixel x
                                         0,  # first pixel y
                                         self.screen_width,  # dimensão do retângulo sendo lido
                                         self.screen_height,  # dimensão do retângulo sendo lido
                                         GL.GL_BGRA,
                                         GL.GL_UNSIGNED_BYTE)
            frame_data = cast(bytes, frame_data)

            frame = np.frombuffer(frame_data, np.uint8)
            frame = frame.reshape([self.screen_height, self.screen_width, 4])
            frame = np.flipud(frame)

            filename = get_filename_unique(self._name)

            self._executor.submit(save_frame, filename, frame)

        ## SEU CÓDIGO AQUI ######################################################
        # Troque o buffer frontal e traseiro, mostrando o novo buffer renderizado
        # Raciocínio: Double buffering evita flickering. Enquanto renderizamos
        # no back buffer, o front buffer é exibido. Depois trocamos.
        # Blit the offscreen FBO to the window's default framebuffer (0)
        w, h = glfw.get_framebuffer_size(self._window)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self._fbo)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)
        GL.glBlitFramebuffer(0, 0, self.screen_width, self.screen_height,
                             0, 0, w, h,
                             GL.GL_COLOR_BUFFER_BIT, GL.GL_NEAREST)
        
        # Bind default framebuffer back
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

        glfw.swap_buffers(self._window)
        #########################################################################

        glfw.poll_events()

    def should_stop(self) -> bool:
        return glfw.window_should_close(self._window)

    def __del__(self):
        self._executor.shutdown()
        glfw.terminate()
