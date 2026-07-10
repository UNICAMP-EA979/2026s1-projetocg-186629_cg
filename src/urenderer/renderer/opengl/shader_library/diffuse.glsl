#ifndef LIBRARY_DIFUSE

#define PI 3.14159265359

vec3 diffuse(vec3 baseColor, float metallic, vec3 fresnel)
{
    return (1.0 - fresnel) * (1.0 - metallic) * baseColor / PI;
}

vec3 computeDiffuse(vec3 baseColor, float fresnel)
{
    return diffuse(baseColor, 0.0, vec3(fresnel));
}

#define LIBRARY_DIFUSE
#endif
