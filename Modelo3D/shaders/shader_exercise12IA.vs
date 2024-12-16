#version 330 core
layout (location = 0) in vec3 aPos;       // Posiciones
layout (location = 1) in vec3 aColor;    // Colores
layout (location = 2) in vec2 aTexCoord; // Coordenadas de textura

out vec3 ourColor;       // Pasar color al fragment shader
out vec2 TexCoord;       // Pasar coordenadas de textura al fragment shader
out vec3 FragPos;        // Pasar posición del fragmento al fragment shader

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    ourColor = aColor;       // Asignar el color del vértice
    TexCoord = aTexCoord;    // Asignar las coordenadas de textura
    FragPos = vec3(model * vec4(aPos, 1.0)); // Posición en espacio del mundo
}
