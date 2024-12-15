# import os
# import pandas as pd
# from PIL import Image
# from Imagen import Imagen

# class BaseDeDatos:
#     def __init__(self, ruta_csv, ruta_carpeta_imagenes):
#         self.ruta_csv = ruta_csv
#         self.ruta_carpeta_imagenes = ruta_carpeta_imagenes
#         self.data = self.cargar_csv()

#     def cargar_csv(self):
#         """Carga la base de datos desde el archivo CSV."""
#         if not os.path.exists(self.ruta_csv):
#             raise FileNotFoundError(f"El archivo CSV no existe: {self.ruta_csv}")

#         data = pd.read_csv(self.ruta_csv)
#         return data

#     def obtener_tatuajes_por_tonalidad(self, tonalidad):
#         """
#         Obtiene los tatuajes recomendados para una tonalidad específica.

#         Args:
#             tonalidad (str): La tonalidad de piel predicha (e.g., 'claro', 'mestizo', 'moreno').

#         Returns:
#             list: Una lista de objetos Imagen correspondientes a las imágenes recomendadas.
#         """
#         if "Tonalidad_Recomendada" not in self.data.columns or "Nombre" not in self.data.columns:
#             raise ValueError("El archivo CSV debe contener las columnas 'Tonalidad_Recomendada' y 'Nombre'.")

#         # Filtrar por tonalidad
#         tatuajes = self.data[self.data["Tonalidad_Recomendada"] == tonalidad]

#         # Construir las rutas completas de las imágenes
#         rutas_imagenes = [
#             os.path.join(self.ruta_carpeta_imagenes, nombre)
#             for nombre in tatuajes["Nombre"]
#         ]

#         # Validar que las imágenes existan físicamente y crear objetos Imagen
#         imagenes_existentes = []
#         for ruta in rutas_imagenes:
#             if os.path.exists(ruta):
#                 imagen_obj = Imagen(ruta)
#                 imagen_obj.cargarImagen()  # Cargar la imagen en memoria
#                 imagenes_existentes.append(imagen_obj)

#             if len(imagenes_existentes) >= 5:
#                 break

#         return imagenes_existentes

import os
import random
import pandas as pd
from PIL import Image
from Imagen import Imagen

class BaseDeDatos:
    def __init__(self, ruta_csv, ruta_carpeta_imagenes):
        self.ruta_csv = ruta_csv
        self.ruta_carpeta_imagenes = ruta_carpeta_imagenes
        self.data = self.cargar_csv()

    def cargar_csv(self):
        """Carga la base de datos desde el archivo CSV."""
        if not os.path.exists(self.ruta_csv):
            raise FileNotFoundError(f"El archivo CSV no existe: {self.ruta_csv}")

        data = pd.read_csv(self.ruta_csv)
        return data

    def obtener_tatuajes_por_tonalidad(self, tonalidad):
        """
        Obtiene los tatuajes recomendados para una tonalidad específica.

        Args:
            tonalidad (str): La tonalidad de piel predicha (e.g., 'claro', 'mestizo', 'moreno').

        Returns:
            list: Una lista de objetos Imagen correspondientes a las imágenes recomendadas.
        """
        if "Tonalidad_Recomendada" not in self.data.columns or "Nombre" not in self.data.columns:
            raise ValueError("El archivo CSV debe contener las columnas 'Tonalidad_Recomendada' y 'Nombre'.")

        # Filtrar por tonalidad
        tatuajes = self.data[self.data["Tonalidad_Recomendada"] == tonalidad]

        # Construir las rutas completas de las imágenes
        rutas_imagenes = [
            os.path.join(self.ruta_carpeta_imagenes, nombre)
            for nombre in tatuajes["Nombre"]
        ]

        # Validar que las imágenes existan físicamente y crear objetos Imagen
        imagenes_existentes = []
        for ruta in rutas_imagenes:
            if os.path.exists(ruta):
                imagen_obj = Imagen(ruta)
                imagen_obj.cargarImagen()  # Cargar la imagen en memoria
                imagenes_existentes.append(imagen_obj)

        return imagenes_existentes

    def obtener_tatuaje_aleatorio(self, tonalidad):
        """
        Devuelve un tatuaje aleatorio que coincida con la tonalidad predicha.

        Args:
            tonalidad (str): La tonalidad de piel predicha.

        Returns:
            Imagen: Un objeto Imagen de un tatuaje aleatorio.
        """
        tatuajes = self.obtener_tatuajes_por_tonalidad(tonalidad)
        if not tatuajes:
            raise ValueError(f"No se encontraron tatuajes para la tonalidad: {tonalidad}")

        return random.choice(tatuajes)
