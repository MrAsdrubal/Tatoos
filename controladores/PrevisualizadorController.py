import os
import shutil
import cv2
import subprocess
from flask import render_template, request, session, redirect, url_for, send_from_directory, jsonify
from ModeloIA.LogicaNegocio.Controlador import Controlador
from pathlib import Path
from PIL import Image

class PrevisualizadorController:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.controlador = None
        self.master_directory = Path(__file__).resolve().parent.parent
        self.static_folder =  Path(__file__).resolve().parent.parent / 'static'
        self.processed_folder = os.path.join(upload_folder, 'processed')
        self.tonalidadPredicha = None
        self.rutaExe = "PrevisualizadorTatuajes.exe"
        self.textures_folder = "textures"
        self.path_tatuajes = os.path.join(self.static_folder, 'tatuajesSugeridos')
        os.makedirs(self.processed_folder, exist_ok=True)
        os.makedirs(self.path_tatuajes, exist_ok=True)

    def previsualizador(self):
        if 'username' not in session:
            return redirect(url_for('login'))

        uploaded_image = "original_piel2.jpg"
        processed_image = "piel2.jpg"
        tattoo_image = "t3.jpg"

        tatuajes = []  # Lista de imágenes sugeridas

        if request.method == 'POST':
            if 'imagen' not in request.files:
                return render_template('previsualizador.html', error='No se seleccionó ninguna imagen')

            file = request.files['imagen']
            if file.filename == '':
                return render_template('previsualizador.html', error='No se seleccionó ninguna imagen')

            if file:
                file_path = os.path.join(self.upload_folder, "original_piel2.jpg")
                self.validar_y_convertir_a_jpg(file, file_path)
                processed_file_path = self.center_zoom_image(file_path, "piel2.jpg")
                self.controlador = Controlador(processed_file_path)
                tatuajesRecomendados, self.tonalidadPredicha = self.controlador.procesar_imagen_y_recomendar()
                print("Tonalidad predicha: " + self.tonalidadPredicha)
                self.guardar_imagen(tatuajesRecomendados)
                self.copy_to_textures(processed_file_path, "piel2.jpg")



        # Cargar imágenes desde la carpeta tatuajesSugeridos
        for filename in os.listdir(self.path_tatuajes):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                tatuajes.append(url_for('static', filename=f'tatuajesSugeridos/{filename}'))

        return render_template('previsualizador.html',
                               uploaded_image=uploaded_image,
                               processed_image=processed_image,
                               tattoo_image=tattoo_image,
                               tonalidad_predicha=self.tonalidadPredicha,
                               tatuajes=tatuajes)

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

        directorioModelo3D = Path(__file__).resolve().parent.parent

        # Construir rutas completas utilizando Path
        self.rutaExe = str(directorioModelo3D / "Modelo3D" /self.rutaExe)
        try:
            #"C:/EPN/2024-B/IA/TattooPreview/Modelo3D/PrevisualizadorTatuajes.exe"
            # Ejecutar el archivo .exe usando subprocess
            subprocess.Popen(self.rutaExe, shell=True)
            return jsonify({"message": "Aplicación ejecutada correctamente"})
        except Exception as e:
            print(f"Error al ejecutar el archivo: {e}")
            return jsonify({"message": "Error al ejecutar la aplicación"}), 500

    def copy_to_textures(self, source_path, target_name):
        # Copiar una imagen al directorio de texturas del directorio MODELO3D
        self.textures_folder = str(self.master_directory / "Modelo3D" /self.textures_folder)
        destination_path = os.path.join(self.textures_folder, target_name)
        try:

            # Copiar el archivo sin eliminar el original
            shutil.copy2(source_path, destination_path)
            print(f"Imagen copiada a {destination_path}")
        except Exception as e:
            print(f"Error al copiar la imagen a textures: {e}")

    def guardar_imagen(self, imagenes):
        for i, imagen in enumerate(imagenes):
            # Generar el nombre del archivo usando el índice i
            nombre_archivo = f"tatuaje_{i + 1}.jpg"
            # Crear la ruta completa donde se guardará la imagen
            tattoo_output_path = os.path.join(self.path_tatuajes, nombre_archivo)
            # Guardar la imagen en la ruta especificada
            imagen.datos_Imagen.save(tattoo_output_path)

    def validar_y_convertir_a_jpg(self, file, output_filename):
        """
        Valida si el archivo es una imagen y lo guarda como .jpg si no lo es.

        Args:
            file: Archivo subido mediante request.files.
            output_filename: Nombre del archivo final con ruta donde se guardará la imagen.

        Returns:
            str: Ruta donde se guardó el archivo convertido o validado.
        """
        try:
            # Verificar si el archivo es una imagen válida
            img = Image.open(file)
            img.verify()  # Verifica si el archivo es una imagen válida
            file.seek(0)  # Reiniciar el puntero del archivo después de verify()

            # Verificar la extensión del archivo
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ['.jpg', '.jpeg']:
                # Convertir a formato JPG si no lo es
                img = Image.open(file)
                img.convert("RGB").save(output_filename, "JPEG")
                print(f"Imagen convertida y guardada como: {output_filename}")
            else:
                # Guardar directamente si ya es JPG
                file.save(output_filename)
                print(f"Imagen guardada directamente como: {output_filename}")

            return output_filename

        except Exception as e:
            print(f"Error al validar o convertir la imagen: {e}")
            raise ValueError("El archivo no es una imagen válida.")

    def preparar_tatuaje(self):
        """
                Copia una imagen a una carpeta destino.
                La ruta de la imagen original se recibe desde el frontend.
                """
        try:
            data = request.get_json()
            ruta_origen = data.get('ruta_imagen')  # Ruta original de la imagen
            # Eliminar el '/' inicial de ruta_origen si existe
            ruta_path = Path(ruta_origen.lstrip('/'))
            # Concatenar con self.master_directory
            ruta_final = str(self.master_directory / ruta_path)
            if not ruta_origen:
                return jsonify({"error": "No se recibió la ruta de la imagen"}), 400
            print(f"Imagen cargada como: {ruta_origen}")
            self.copy_to_textures(ruta_final, "t3.png")
            return jsonify({"message": "Imagen preparada exitosamente", "ruta_de_origen": ruta_origen}), 200

        except Exception as e:
            print(f"Error al copiar la imagen: {e}")
            return jsonify({"error": "Error al copiar la imagen"}), 500

    def refrescar_tatuaje(self):
        """
        Devuelve las imágenes actualizadas de tatuajes en formato JSON.
        """
        tatuajes = []

        # Obtener nuevas imágenes recomendadas
        if self.controlador:
            tatuajesRecomendados = self.controlador.obtener_actualizacion_tatuajes(self.tonalidadPredicha)
            self.guardar_imagen(tatuajesRecomendados)

        # Cargar imágenes desde la carpeta tatuajesSugeridos
        for filename in os.listdir(self.path_tatuajes):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                tatuajes.append(url_for('static', filename=f'tatuajesSugeridos/{filename}'))

        # Devolver las imágenes como JSON
        return jsonify({'tatuajes': tatuajes})

