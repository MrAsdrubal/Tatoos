from PIL import Image
import os

class Imagen:
    """Clase que representa la imagen cargada por un usuario"""
    def __init__(self, ruta_Imagen):
        self.ruta_Imagen = ruta_Imagen
        self.datos_Imagen = None

    def cargarImagen(self):
        if not os.path.exists(self.ruta_Imagen):
            raise FileNotFoundError(f"La imagen no existe: {self.ruta_Imagen}")
        self.datos_Imagen = Image.open(self.ruta_Imagen)

