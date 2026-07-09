# Gerado com Google Gemini 3.1 Pro - 22/06/2026

import numpy as np
from pygltflib import GLTF2
from scipy.spatial.transform import Rotation

from urenderer.node import Node

from .mesh import Mesh

# Mapeamento dos tipos do GLTF para dtypes do Numpy
COMPONENT_TYPE_MAP = {
    5120: np.int8,
    5121: np.uint8,
    5122: np.int16,
    5123: np.uint16,
    5125: np.uint32,
    5126: np.float32
}

# Mapeamento do formato (VEC3, SCALAR, etc) para quantidade de componentes
TYPE_MAP = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": 4,
    "MAT3": 9,
    "MAT4": 16
}


def _get_accessor_data(gltf: GLTF2, accessor_idx: int) -> np.ndarray:
    """
    Lê os dados binários puros a partir de um índice de accessor no GLTF.
    """
    accessor = gltf.accessors[accessor_idx]
    buffer_view = gltf.bufferViews[accessor.bufferView]

    # Pega o buffer binário inteiro
    blob = gltf.binary_blob()

    # Calcula os offsets
    byte_offset = buffer_view.byteOffset + (accessor.byteOffset or 0)

    # Determina o tipo do dado e a quantidade de elementos
    dtype = COMPONENT_TYPE_MAP[accessor.componentType]
    num_components = TYPE_MAP[accessor.type]
    count = accessor.count

    # Quantidade total de bytes que vamos ler
    byte_length = count * num_components * np.dtype(dtype).itemsize

    # Extrai e formata o array
    raw_data = blob[byte_offset: byte_offset + byte_length]
    data = np.frombuffer(raw_data, dtype=dtype).reshape(
        (count, num_components))

    return data


def _parse_mesh(gltf: GLTF2, mesh_idx: int) -> list[Mesh]:
    """
    Converte um Mesh do GLTF em uma ou mais instâncias da classe Mesh.
    Retorna uma lista, pois um Mesh no GLTF pode conter múltiplas primitivas.
    """
    gltf_mesh = gltf.meshes[mesh_idx]
    meshes = []

    for primitive in gltf_mesh.primitives:
        # Vértices (Obrigatório)
        pos_accessor_idx = primitive.attributes.POSITION
        vertex = _get_accessor_data(gltf, pos_accessor_idx).astype(np.float32)

        # Índices (Obrigatório para o seu Mesh)
        if primitive.indices is not None:
            index = _get_accessor_data(
                gltf, primitive.indices).flatten().astype(np.uint32)
        else:
            # Caso não tenha EBO (raro, mas possível em GLTF), gera de forma sequencial
            index = np.arange(vertex.shape[0], dtype=np.uint32)

        # UVs (Sua classe pede UV obrigatório, então geramos default se faltar)
        if hasattr(primitive.attributes, 'TEXCOORD_0') and primitive.attributes.TEXCOORD_0 is not None:
            uv = _get_accessor_data(
                gltf, primitive.attributes.TEXCOORD_0).astype(np.float32)
        else:
            uv = np.zeros((vertex.shape[0], 2), dtype=np.float32)

        # Normais (Opcional)
        normal = None
        if hasattr(primitive.attributes, 'NORMAL') and primitive.attributes.NORMAL is not None:
            normal = _get_accessor_data(
                gltf, primitive.attributes.NORMAL).astype(np.float32)

        mesh = Mesh(vertex=vertex, index=index, uv=uv, normal=normal)
        meshes.append(mesh)

    return meshes


def _parse_node(gltf: GLTF2, node_idx: int) -> Node:
    """
    Constrói um Node, define seus transforms e atrela recursivamente seus filhos e geometrias.
    """
    gltf_node = gltf.nodes[node_idx]
    node = Node(name=gltf_node.name or f"Node_{node_idx}")

    # 1. Parsing de Transformações (TRS)
    if gltf_node.translation is not None:
        node.translation = np.array(gltf_node.translation, dtype=np.float32)

    if gltf_node.rotation is not None:
        # GLTF usa Quaternions [x, y, z, w]. O seu Node espera Euler em graus.
        quat = gltf_node.rotation
        r = Rotation.from_quat(quat)
        node.rotation = r.as_euler('xyz', degrees=True).astype(np.float32)

    if gltf_node.scale is not None:
        node.scale = np.array(gltf_node.scale, dtype=np.float32)

    # Nota: Se o GLTF vier com uma propriedade 'matrix' ao invés de TRS (pouco comum em exportações recentes,
    # mas listado na especificação do GLTF), essa implementação assume que a matriz precisaria
    # ser decomposta. Mantemos o parser focado em TRS pois 99% das exportações modernas (.glb) utilizam TRS.

    # 2. Lidando com Geometria
    if gltf_node.mesh is not None:
        meshes = _parse_mesh(gltf, gltf_node.mesh)
        if len(meshes) == 1:
            # Se for só uma primitiva, atrela direto a este Node
            node.render_data["mesh"] = meshes[0]
        else:
            # Se a malha tiver múltiplas primitivas (múltiplos materiais por exemplo),
            # criamos nós filhos virtuais para acomodar cada uma, dado que a arquitetura do motor liga 1 Node -> 1 Mesh
            for i, primitive_mesh in enumerate(meshes):
                child_mesh_node = Node(name=f"{node.name}_prim_{i}")
                child_mesh_node.render_data["mesh"] = primitive_mesh
                node.add_child(child_mesh_node)

    # 3. Construindo a Hierarquia (Filhos)
    if gltf_node.children is not None:
        for child_idx in gltf_node.children:
            child_node = _parse_node(gltf, child_idx)
            node.add_child(child_node)

    return node


def load_glb(filepath: str) -> Node:
    """
    Carrega um arquivo .glb e retorna o nó raiz (Node) contendo o Grafo de Cena.
    """
    gltf = GLTF2().load(filepath)

    # O GLTF pode ter múltiplas "cenas", mas quase sempre usamos a cena padrão
    scene_idx = gltf.scene if gltf.scene is not None else 0
    scene = gltf.scenes[scene_idx]

    # Cria um nó root (cenário vazio)
    root_node = Node(name=f"SceneRoot_{filepath}")

    for root_node_idx in scene.nodes:
        child_node = _parse_node(gltf, root_node_idx)
        root_node.add_child(child_node)

    return root_node
