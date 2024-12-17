
from ModeloIA.LogicaNegocio.Preprocesamiento import Preprocesamiento
from ModeloIA.LogicaNegocio.Modelo import ModeloPrediccionPiel
from ModeloIA.LogicaNegocio.DataSet import BaseDeDatos
from ModeloIA.LogicaNegocio.Imagen import Imagen
from pathlib import Path

class Controlador:
    """
    Clase Controlador que orquesta la interacción entre el modelo de predicción,
    la base de datos de tatuajes y el preprocesamiento de imágenes.
    """

    def __init__(self, ruta_imagen):
        """
        Inicializa el controlador con los componentes necesarios.

        Args:
            ruta_imagen (str): Ruta de la imagen a procesar.
        """
        self.imagen_usuario = Imagen(ruta_imagen)

        # Definir nombres de archivos y carpetas
        modelo_prediccion_nombre = "model7_resnet18.pth"
        tattoos_csv_nombre = "resultado_analisis.csv"
        directorio_tatuajes_nombre = "Tatuajes"

        # Obtener la ruta base del proyecto
        directorioBase= Path(__file__).resolve().parent.parent

        # Construir rutas completas utilizando Path
        self.modelo_prediccion = str(directorioBase / "Modelos_Entrenados" / modelo_prediccion_nombre)
        self.tattoos_csv = str(directorioBase / "LogicaNegocio" / tattoos_csv_nombre)
        self.directorio_tatuajes = str(directorioBase / directorio_tatuajes_nombre)

        # Inicializar los componentes principales
        self.modelo = ModeloPrediccionPiel(self.modelo_prediccion)
        self.base_datos = BaseDeDatos(self.tattoos_csv, self.directorio_tatuajes)

    def procesar_imagen_y_recomendar(self):
        """
        Procesa una imagen de entrada, predice la tonalidad de piel y recomienda tatuajes.

        Returns:
            tuple: Imagen procesada, tonalidad predicha y tatuaje recomendado.
        """
        # 1. Preprocesar la imagen
        imagen_procesada = Preprocesamiento.procesar(self.imagen_usuario)

        # 2. Predecir la tonalidad de piel
        tonalidad_predicha = self.modelo.predecir(imagen_procesada)

        # 3. Obtener un tatuaje recomendado, en este caso retorna una variable con longitud variable
        tatuajes_recomendado = self.base_datos.obtener_tatuaje_aleatorio(tonalidad_predicha)

        return tatuajes_recomendado, tonalidad_predicha

    def obtener_actualizacion_tatuajes(self, tonalidad_predicha):
        print("llegamos aqui")
        tatuajes_recomendado = self.base_datos.obtener_tatuaje_aleatorio(tonalidad_predicha)
        return tatuajes_recomendado


if __name__ == "__main__":


    # Obtener la ruta base del proyecto
    directorio_base = Path(__file__).resolve().parent.parent
    ruta_imagen_usuario = str (directorio_base / "Prediccion" / "piel12.jpg")

    try:
        # Crear instancia del controlador
        controlador = Controlador(ruta_imagen_usuario)

        # Obtener recomendaciones de tatuajes()
        recomendacion, tonalidadPredicha = controlador.procesar_imagen_y_recomendar()

        print("Tonalidad de piel predicha:", tonalidadPredicha)
        # Mostrar las recomendaciones
        print("Tatuajes recomendados:")

        recomendacion.datos_Imagen.show()  # Mostrar cada tatuaje recomendado

    except Exception as e:
        print(f"Error: {e}")
