#ifndef LIBRARY_LIGHT

const int LIGHT_UNSET = 0;
const int LIGHT_DIRECTIONAL = 1;
const int LIGHT_POINT = 2;
const float R_MIN = 0.05;

struct Light
{
    int type;
    vec3 color;
    float intensity;
    vec3 direction; //Only directional
    vec3 position; //Only point
    float reference_distance; //Only point
};

// Calcula a atenuação da luz
float computeLightAttenuation(Light light, vec3 position)
{
    if(light.type == LIGHT_DIRECTIONAL)
    {
        return 1.0;
    }
    
    if(light.type == LIGHT_POINT)
    {
        float distance = length(light.position - position);
        distance = max(distance, R_MIN);
        float attenuation = (light.reference_distance / distance);
        return attenuation * attenuation;
    }
    
    return 0.0;
}

//Calcula a direção da luz
vec3 computeLightDirection(Light light, vec3 position)
{
    if(light.type == LIGHT_DIRECTIONAL)
    {
        return normalize(light.direction);
    }
    
    if(light.type == LIGHT_POINT)
    {
        return normalize(light.position - position);
    }
    
    return vec3(0.0);
}

#define LIBRARY_LIGHT
#endif