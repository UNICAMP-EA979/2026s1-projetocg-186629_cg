from collections import deque
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
import urenderer
from OpenGL import GL
from urenderer.node import Node
from urenderer.renderer.opengl import Material, Texture


def update_rotation(node: Node, deltaTime: float, time_since_start: float) -> None:

    time_since_start /= 10
    t = time_since_start - int(time_since_start)

    node.rotation[0] = 0
    node.rotation[1] = 360*t
    node.rotation[2] = 0


def update_scale(node: Node, deltaTime: float, time_since_start: float) -> None:
    scale = np.sin(5*time_since_start)/10
    scale += 0.8

    node.scale = scale * np.ones(3)


def update_cube(node: Node, deltaTime: float, time_since_start: float) -> None:

    # Posição = dv/dt -> posição_t = posição_{t-1}+DeltaT*v
    center: np.array = node.center
    position = node.translation

    r = position-center

    r_2d = np.array([r[0], r[2]])
    v_dir = np.array([-r_2d[1], r_2d[0]])

    v = v_dir*node.angular_velocity
    v = np.array([v[0], 0.0, v[1]])

    node.translation += deltaTime*v

    # Rotação = f(tempo)
    time_since_start /= 10
    t = time_since_start - int(time_since_start)
    node.rotation[0] = 0
    node.rotation[1] = -360*node.angular_velocity*t
    node.rotation[2] = 0


# Podemos dar um nome a cena
NOME_DA_CENA = "minha_cena"

if __name__ == "__main__":
    urenderer.utils.clear_workdir(NOME_DA_CENA)
    renderer = urenderer.renderer.OpenGLRenderer(1920, 1080)
    renderer.background_color = np.array([0, 0, 0, 1], np.float32)
    runtime = urenderer.application.Runtime(
        renderer, name=NOME_DA_CENA)

    # Configuramos a luz ambiente da cena
    renderer.ambient_color = np.array([0.1, 0.1, 0.1], dtype=np.float32)

    # Carregamos o shader e texturas
    shader = urenderer.renderer.Shader(
        "assets/vertex.vs", "assets/05-fragment.fs")

    whiteTextureR = Texture(255*np.ones((1, 1), np.uint8), GL.GL_RED, GL.GL_R8)
    blackTextureR = Texture(np.zeros((1, 1), np.uint8), GL.GL_RED, GL.GL_R8)

    whiteTexture = Texture(255*np.ones((1, 1, 3), np.uint8),
                           GL.GL_RGB, GL.GL_RGB)
    blackTexture = Texture(np.zeros((1, 1, 3), np.uint8),
                           GL.GL_RGB, GL.GL_RGB)

    starrySkyTexture = Texture.load_file("assets/Blue-universe-956981.jpg",
                                         srgb=True, drop_alpha=True)

    rockBasecolor = Texture.load_file("assets/Rock035_1K-JPG/Rock035_1K-JPG_Color.jpg",
                                      srgb=True, drop_alpha=True)
    rockRoughness = Texture.load_file("assets/Rock035_1K-JPG/Rock035_1K-JPG_Roughness.jpg",
                                      drop_alpha=True)

    materialBasic = Material(shader)
    materialBasic.set_texture(0, "baseColorTexture", whiteTexture)
    materialBasic.set_texture(1, "metallicTexture", blackTextureR)
    materialBasic.set_texture(2, "roughnessTexture", whiteTextureR)

    materialBackground = Material(shader)
    materialBackground.set_texture(0, "baseColorTexture", starrySkyTexture)
    materialBackground.set_texture(1, "metallicTexture", blackTextureR)
    materialBackground.set_texture(2, "roughnessTexture", whiteTextureR)
    materialBackground.set_uniform("tiling", 10.0)

    materialCube = Material(shader)
    materialCube.set_texture(0, "baseColorTexture", rockBasecolor)
    materialCube.set_texture(1, "metallicTexture", blackTextureR)
    materialCube.set_texture(2, "roughnessTexture", rockRoughness)

    # Carregamos a cena (ou poderia ser criada com primitivas)
    glb_root = urenderer.geometry.mesh.load_glb("assets/CenaExemplo.glb")

    center = np.zeros(3, dtype=np.float32)
    nodes = deque([glb_root])
    while len(nodes) != 0:
        node = nodes.pop()
        nodes += node.children

        if node.name == "Icosphere":
            center = node.translation

    # Definimos materiais para os elementos da cena
    nodes = deque([glb_root])
    last_cube = None
    while len(nodes) != 0:
        node = nodes.pop()
        nodes += node.children

        node.render_data["material"] = materialBasic

        # Podemos definir o material pelo nome do nó, ou um padrão no nome
        if node.name == "Plane":
            node.render_data["material"] = materialBackground
        if "Cube" in node.name:
            node.render_data["material"] = materialCube

        # Podemos animar os objetos da cena:
        if node.name == "Icosphere":
            node.callbacks = [update_rotation, update_scale]
        if "Cube" in node.name:
            node.center = center
            node.angular_velocity = 0.5
            node.callbacks = [update_cube]
            last_cube = node

    # Movimentamos a cena para a posição desejada
    glb_root.translation = np.array([0, 0, -7])
    glb_root.rotation = np.array([30, 0, 0], np.float32)
    runtime.scene.add_child(glb_root)

    # Podemos alterar propriedades da câmera
    runtime.camera.vertical_fov = 90.0

    # Adicionamos luzes a cena

    light = urenderer.node.Light(urenderer.node.LightType.DIRECTIONAL)
    light.rotation = np.array([45, 45, 45], np.float64)
    light.light_intensity = 3.0
    runtime.scene.add_child(light)

    light2 = urenderer.node.Light(urenderer.node.LightType.POINT)
    light2.translation = np.array([-1, -1, -6], np.float64)
    light2.light_color = np.array([0.0, 0.0, 1.0], np.float32)
    light2.light_intensity = 5.0
    runtime.scene.add_child(light2)

    light3 = urenderer.node.Light(urenderer.node.LightType.POINT)
    # light3.translation = np.array([1, -1, -6], np.float64)
    light3.light_color = np.array([1.0, 0.0, 1.0], np.float32)
    light3.light_intensity = 5.0
    if last_cube is not None:
        last_cube.add_child(light3)
    else:
        runtime.scene.add_child(light3)

    # Renderizamos a cena

    video = False
    if video:
        # Renderização salvando video
        # Podemos ajustar os parâmetros para alterar o tamanho ou frequência de sampling
        runtime.loop(n=4000, capture=np.arange(0, 4000, 40, dtype=np.int32))
        urenderer.utils.image_to_video(NOME_DA_CENA, fps=30)
        urenderer.utils.clear_workdir(NOME_DA_CENA, image_only=True)
    else:
        # Renderização salvando frames
        runtime.loop(capture=[1])
