#ifndef LIBRARY_FRESNEL

vec3 fresnelReflectance(vec3 baseColor, float metallic, vec3 halfAngle, vec3 lightDirection)
{
    vec3 F0 = mix(vec3(0.04), baseColor, metallic);
    float cosTheta = max(0.0, dot(halfAngle, lightDirection));
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

float computeFresnel(float F0, vec3 halfAngle, vec3 lightDirection)
{
    float cosTheta = max(0.0, dot(halfAngle, lightDirection));
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

#define LIBRARY_FRESNEL
#endif
