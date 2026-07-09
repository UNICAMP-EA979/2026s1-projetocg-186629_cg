#version 330 core
// Recebe os dados: 
// position no location = 0
// vertexUV na location = 1 
// normal na location = 3
//
// e as uniforms mat4 modelTransformation, viewTransformation e projectionMatrix
// 
// Converte a position para o clip space usando as transformações e armazena em gl_Position.
//
// Também escreve os dados de saída:
// worldPosition: posição no world space
// worldNormal: normal no world space
// uv: uv do vértice 
//
// SEU CÓDIGO AQUI //////////////////////////////////////////////////////////////////////////

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 vertexUV;
layout(location = 3) in vec3 normal;

out vec3 worldPosition;
out vec3 worldNormal;
out vec2 uv;

uniform mat4 modelTransformation;
uniform mat4 viewTransformation;
uniform mat4 projectionMatrix;

void main()
{
    worldPosition = (modelTransformation * vec4(position, 1.0)).xyz;

    worldNormal = normalize((modelTransformation * vec4(normal, 0.0)).xyz);

    uv = vertexUV;

    gl_Position = projectionMatrix * viewTransformation * modelTransformation * vec4(position, 1.0);
}

/////////////////////////////////////////////////////////////////////////////////////////////