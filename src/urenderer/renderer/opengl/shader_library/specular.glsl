#ifndef LIBRARY_SPECULAR

#define PI 3.14159265359

vec3 specular(vec3 halfAngle, vec3 normal, vec3 lightDirection,
              vec3 viewDirection, float roughness, vec3 fresnel)
{
    // Calcula o expoente de Blinn-Phong baseado em roughness
    // smoothness = 1 - roughness
    // alpha = 8192^smoothness (8192 = 2^13)
    float smoothness = 1.0 - roughness;
    float m = pow(8192.0, smoothness);

    float ndotH = max(0.0, dot(normal, halfAngle));
    float ndotL = max(0.0, dot(normal, lightDirection));
    float ndotV = max(0.001, dot(normal, viewDirection));

    float normalizationFactor = (m + 2.0) / (8.0 * PI);
    float specularTerm = pow(ndotH, m) / max(ndotL * ndotV, 0.000001);

    return fresnel * normalizationFactor * specularTerm;
}

float computeSpecular(float fresnel, vec3 normal, vec3 halfAngle,
                      vec3 viewDirection, vec3 lightDirection, float roughness)
{
    return specular(halfAngle, normal, lightDirection,
                    viewDirection, roughness, vec3(fresnel)).r;
}

#define LIBRARY_SPECULAR
#endif
