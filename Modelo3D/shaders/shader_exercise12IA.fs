#version 330 core
out vec4 FragColor;

in vec3 ourColor;
in vec2 TexCoord;

uniform sampler2D texture1;  // Textura del tatuaje
uniform sampler2D texture2;  // Nueva textura a aplicar
uniform vec2 textureOffset; 
uniform vec2 textureSize;    // Tamaño dinámico del tatuaje
uniform float rotationAngle; // Ángulo de rotación en radianes

void main()
{
    // Calcular el centro de la textura
    vec2 center = textureOffset + textureSize * 0.5;

    // Desplazar las coordenadas de la textura para que el centro sea el origen de la rotación
    vec2 texCoordOffset = TexCoord - center;

    // Matriz de rotación
    mat2 rotationMatrix = mat2(cos(rotationAngle), -sin(rotationAngle),
                               sin(rotationAngle), cos(rotationAngle));

    // Aplicar la rotación
    vec2 rotatedTexCoord = rotationMatrix * texCoordOffset + center;

    // Definir el área de la textura
    vec2 textureAreaMin = textureOffset;
    vec2 textureAreaMax = textureOffset + textureSize;

    // Si las coordenadas rotadas están dentro del área del tatuaje
    if (rotatedTexCoord.x >= textureAreaMin.x && rotatedTexCoord.x <= textureAreaMax.x &&
        rotatedTexCoord.y >= textureAreaMin.y && rotatedTexCoord.y <= textureAreaMax.y)
    {
        // Escalar las coordenadas de la textura
        vec2 scaledTexCoord = (rotatedTexCoord - textureAreaMin) / textureSize;
        
        // Muestrear el color de texture1
        vec4 sampledColor = texture(texture1, scaledTexCoord);

        // Si el color es blanco, reemplazar con texture2
        if (sampledColor.rgb == vec3(1.0, 1.0, 1.0)) {
            FragColor = texture(texture2, TexCoord);
        } else {
            FragColor = sampledColor; // Aplicar la textura del tatuaje
        }
    }
    else
    {
        FragColor = texture(texture2, TexCoord); // Aplicar la segunda textura
    }
}

