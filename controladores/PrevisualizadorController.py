import os
import cv2
import numpy as np
import subprocess
from flask import render_template, request, session, redirect, url_for, send_from_directory, jsonify
from ModeloIA.LogicaNegocio.Controlador import Controlador
from ModeloIA.LogicaNegocio.Imagen import Imagen

class PrevisualizadorController:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.processed_folder = os.path.join(upload_folder, 'processed')
        self.tonalidadPredicha = None
        self.textures_folder = r"C:\\Users\\NW\\Downloads\\PrevisualizadorCuello\\PrevisualizadorCuello\\textures"
        os.makedirs(self.processed_folder, exist_ok=True)

    def previsualizador(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        uploaded_image = "original_piel2.jpg"
        processed_image = "piel2.jpg"
        tattoo_image = "t3.jpg"

        if request.method == 'POST':
            if 'imagen' not in request.files:
                return render_template('previsualizador.html', error='No se seleccionó ninguna imagen')

            file = request.files['imagen']
            if file.filename == '':
                return render_template('previsualizador.html', error='No se seleccionó ninguna imagen')

            if file:
                # Guardar la imagen original como "piel2.jpg"
                file_path = os.path.join(self.upload_folder, "original_piel2.jpg")
                file.save(file_path)

                controlador = Controlador(file_path)
                tatuajeRecomendado, self.tonalidadPredicha = controlador.procesar_imagen_y_recomendar()
                print("Tonalidad predicha:   " + self.tonalidadPredicha)

                # Guardar la imagen del tatuaje recomendado con nombre fijo
                tattoo_output_path = os.path.join(self.upload_folder, "t3.jpg")
                tatuajeRecomendado.datos_Imagen.save(tattoo_output_path)

                # Procesar la imagen con zoom centrado y guardar como processed_piel2.jpg
                processed_file_path = self.center_zoom_image(file_path, "piel2.jpg")

                # Copiar la imagen procesada y el tatuaje a la carpeta textures
                self.copy_to_textures(processed_file_path, "piel2.jpg")
                self.copy_to_textures(tattoo_output_path, "t3.png")

        return render_template('previsualizador.html',
                               uploaded_image=uploaded_image,
                               processed_image=processed_image,
                               tattoo_image=tattoo_image,
                               tonalidad_predicha=self.tonalidadPredicha)

    def center_zoom_image(self, image_path, filename):
        # Leer la imagen con OpenCV
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        # Calcular las coordenadas del recorte central con más zoom
        zoom_factor = 0.5  # Ajustado para mayor zoom (0.5 recorta más)
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)

        x1 = (width - new_width) // 2
        y1 = (height - new_height) // 2
        x2 = x1 + new_width
        y2 = y1 + new_height

        # Recortar la imagen
        cropped_image = image[y1:y2, x1:x2]

        # Redimensionar la imagen recortada al tamaño original
        zoomed_image = cv2.resize(cropped_image, (width, height), interpolation=cv2.INTER_LINEAR)

        # Guardar la imagen procesada con nombre fijo
        processed_path = os.path.join(self.processed_folder, filename)
        cv2.imwrite(processed_path, zoomed_image)

        return processed_path

    def uploaded_file(self, filename):
        # Servir el archivo desde la carpeta 'processed' o la raíz 'uploads'
        if os.path.exists(os.path.join(self.processed_folder, filename)):
            return send_from_directory(self.processed_folder, filename)
        return send_from_directory(self.upload_folder, filename)

    def previsualizar_tatuaje(self):
        # Ruta específica del archivo .exe
        exe_path = r"C:\\Users\\NW\\Downloads\\PrevisualizadorCuello\\PrevisualizadorCuello\\PrevisualizadorCuello.exe"
        try:
            # Ejecutar el archivo .exe usando subprocess
            subprocess.Popen(exe_path, shell=True)
            return jsonify({"message": "Aplicación ejecutada correctamente"})
        except Exception as e:
            print(f"Error al ejecutar el archivo: {e}")
            return jsonify({"message": "Error al ejecutar la aplicación"}), 500

    def copy_to_textures(self, source_path, target_name):
        # Copiar una imagen al directorio de textures con un nombre fijo sin borrar el original
        destination_path = os.path.join(self.textures_folder, target_name)
        try:
            # Copiar el archivo sin eliminar el original
            import shutil
            shutil.copy2(source_path, destination_path)
            print(f"Imagen copiada a {destination_path}")
        except Exception as e:
            print(f"Error al copiar la imagen a textures: {e}")
