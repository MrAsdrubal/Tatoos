
from Preprocesamiento import Preprocesamiento
from Modelo import ModeloPrediccionPiel
from DataSet import BaseDeDatos
from Imagen import Imagen
import json
import base64

class Controlador:
    """
    Clase Controlador que orquesta la interacción entre el modelo de predicción,
    la base de datos de tatuajes y el preprocesamiento de imágenes.
    """

    def __init__(self, ruta_modelo, ruta_csv, ruta_carpeta_imagenes):
        """
        Inicializa el controlador con los componentes necesarios.

        Args:
            ruta_modelo (str): Ruta al archivo del modelo de predicción.
            ruta_csv (str): Ruta al archivo CSV con datos de los tatuajes.
            ruta_carpeta_imagenes (str): Ruta a la carpeta donde se encuentran las imágenes de tatuajes.
        """
        self.modelo = ModeloPrediccionPiel(ruta_modelo)
        self.base_datos = BaseDeDatos(ruta_csv, ruta_carpeta_imagenes)

    def procesar_imagen_y_recomendar(self, imagen):
        """
        Procesa una imagen de entrada, predice la tonalidad de piel y recomienda tatuajes.

        Args:
            imagen (Imagen): Instancia de la clase Imagen con la imagen cargada.

        Returns:
            list: Lista de objetos Imagen correspondientes a los tatuajes recomendados.
        """
        # 1. Preprocesar la imagen
        imagen_procesada = Preprocesamiento.procesar(imagen)

        # 2. Predecir la tonalidad de piel
        tonalidad_predicha = self.modelo.predecir(imagen_procesada)

        # 3. Obtener tatuajes recomendados
        tatuaje_recomendado = self.base_datos.obtener_tatuaje_aleatorio(tonalidad_predicha)

        return tatuaje_recomendado, tonalidad_predicha

# class Controlador:
#     def __init__(self, ruta_modelo, ruta_csv, ruta_carpeta_imagenes):
#         self.modelo = ModeloPrediccionPiel(ruta_modelo)
#         self.base_datos = BaseDeDatos(ruta_csv, ruta_carpeta_imagenes)
#         self.output_json = {}

#     def procesar_imagen_y_recomendar(self, imagen):
#         """
#         Procesa una imagen de entrada, predice la tonalidad de piel y recomienda un tatuaje.

#         Args:
#             imagen (Imagen): Instancia de la clase Imagen con la imagen cargada.

#         Returns:
#             dict: JSON con la tonalidad predicha y el tatuaje recomendado en forma de bits.
#         """
#         # 1. Preprocesar la imagen
#         imagen_procesada = Preprocesamiento.procesar(imagen)

#         # 2. Predecir la tonalidad de piel
#         tonalidad_predicha = self.modelo.predecir(imagen_procesada)

#         # 3. Obtener un tatuaje recomendado
#         tatuaje_recomendado = self.base_datos.obtener_tatuaje_aleatorio(tonalidad_predicha)

#         # 4. Convertir la imagen a bits directamente
#         imagen_bytes = tatuaje_recomendado.datos_Imagen.tobytes()
#         imagen_en_bits = base64.b64encode(imagen_bytes).decode('utf-8')

#         # 5. Crear el JSON de output
#         self.output_json = {
#             "tonalidad_predicha": tonalidad_predicha,
#             "tatuaje_recomendado": imagen_en_bits
#         }

#         return self.output_json


if __name__ == "__main__":
    # Rutas de ejemplo (modificar según el entorno real)
    ruta_modelo = "C:/EPN/2024-B/IA/TattooVision/Modelos_Entrenados/model7_resnet18.pth"
    ruta_csv = "C:/EPN/2024-B/IA/TattooVision/LogicaNegocio/resultado_analisis.csv"
    ruta_carpeta_imagenes = "C:/EPN/2024-B/IA/TattooVision/Tatuajes"
    ruta_imagen_usuario = "C:/EPN/2024-B/IA/TattooVision/Prediccion/piel18.jpg"

    try:
        # Crear instancia del controlador
        controlador = Controlador(ruta_modelo, ruta_csv, ruta_carpeta_imagenes)

        # Cargar imagen del usuario
        imagen_usuario = Imagen(ruta_imagen_usuario)
        imagen_usuario.cargarImagen()

        # Obtener recomendaciones de tatuajes
        recomendacion, tonalidadPredicha = controlador.procesar_imagen_y_recomendar(imagen_usuario)

        print("Tonalidad de piel predicha:", tonalidadPredicha)
        # Mostrar las recomendaciones
        print("Tatuajes recomendados:")
        
        recomendacion.datos_Imagen.show()  # Mostrar cada tatuaje recomendado

    except Exception as e:
        print(f"Error: {e}")
