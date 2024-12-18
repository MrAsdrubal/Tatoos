import os
import shutil
import cv2
import subprocess
from flask import render_template, request, session, redirect, url_for, send_from_directory, jsonify
from pandas.core.interchange.from_dataframe import primitive_column_to_ndarray
from ModeloIA.LogicaNegocio.Controlador import Controlador
from pathlib import Path
from PIL import Image
from flask import session
from ModeloIA.LogicaNegocio.Preprocesamiento import Preprocesamiento


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

        nombre_imagen_original = "original_piel2.png"
        nombre_imagen_procesada = "piel2.jpg"
        nombre_tatuaje_recomendado = "t3.png"

        tatuajes = []  # Lista de imágenes sugeridas

        if request.method == 'POST':
            if 'imagen' not in request.files:
                return render_template('previsualizador.html', error='No se seleccionó ninguna imagen')

            file = request.files['imagen']
            if file.filename == '':
                return render_template('previsualizador.html', error='No se seleccionó ninguna imagen')

            if file:
                file_path = os.path.join(self.upload_folder, nombre_imagen_original)
                ruta_guardado_original = self.validar_y_convertir_a_png(file, file_path)
                processed_file_path = self.center_zoom_image(file_path, nombre_imagen_procesada)

                # Proceso de predicción
                self.controlador = Controlador(processed_file_path)
                tatuajesRecomendados, self.tonalidadPredicha = self.controlador.procesar_imagen_y_recomendar()

                # Guardar la tonalidad en la sesión
                session['tonalidad_predicha'] = self.tonalidadPredicha
                print("Tonalidad predicha guardada en sesión:", self.tonalidadPredicha)
                print(session['tonalidad_predicha'] )

                # Procesamiento adicional
                Imagen = Image.open(processed_file_path)
                MuestraTonalidadFinal = Preprocesamiento.resalte_tonalidad_piel(Imagen, self.tonalidadPredicha)
                MuestraTonalidadFinal.save(processed_file_path)

                self.guardar_imagen(tatuajesRecomendados)
                self.copy_to_textures(processed_file_path, nombre_imagen_procesada)

        # Cargar imágenes desde la carpeta tatuajesSugeridos
        for filename in os.listdir(self.path_tatuajes):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                tatuajes.append(url_for('static', filename=f'tatuajesSugeridos/{filename}'))

        return render_template('previsualizador.html',
                               uploaded_image=nombre_imagen_original,
                               processed_image=nombre_imagen_procesada,
                               tattoo_image=nombre_tatuaje_recomendado,
                               tonalidad_predicha=self.tonalidadPredicha,
                               tatuajes=tatuajes)

    def center_zoom_image(self, image_path, filename):
        # Leer la imagen con OpenCV
        image = cv2.imread(image_path)
        height, width = image.shape[:2]

        # Calcular las coordenadas del recorte central con más zoom
        zoom_factor = 0.4  # Ajustado para mayor zoom (0.5 recorta más)
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
        # Construir rutas completas utilizando Path
        rutaLocalExe = str(self.master_directory / "Modelo3D" /self.rutaExe)
        try:
            #"C:/EPN/2024-B/IA/TattooPreview/Modelo3D/PrevisualizadorTatuajes.exe"
            # Ejecutar el archivo .exe usando subprocess
            if self.rutaExe is None:
                return jsonify({"message": "No existe un tatuaje cargado"})
            subprocess.Popen(rutaLocalExe, shell=True)
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


    def validar_y_convertir_a_png(self, file, output_filename):
        """
        Valida si el archivo es una imagen y lo guarda como .png si no lo es.

        Args:
            file: Archivo subido mediante request.files.
            output_filename: Nombre del archivo final con ruta donde se guardara la imagen como .png.

        Returns:
            str: Ruta donde se guardo el archivo convertido o validado.
        """
        try:
            # Verificar si el archivo es una imagen valida
            img = Image.open(file)
            img.verify()  # Verifica si el archivo es una imagen valida
            file.seek(0)  # Reiniciar el puntero del archivo despues de verify()

            # Verificar la extension del archivo
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext != '.png':
                # Convertir a formato PNG si no lo es
                img = Image.open(file)
                img.save(output_filename, "PNG")
                print(f"Imagen convertida y guardada como: {output_filename}")
            else:
                # Guardar directamente si ya es PNG
                file.save(output_filename)
                print(f"Imagen guardada directamente como: {output_filename}")

            return output_filename

        except Exception as e:
            print(f"Error al validar o convertir la imagen: {e}")
            raise ValueError("El archivo no es una imagen valida.")

    def preparar_tatuaje(self):
        """
                Copia una imagen a una carpeta destino.
                La ruta de la imagen original se recibe desde el frontend.
                """
        try:
            file_name = "t3.png"
            data = request.get_json()
            ruta_origen = data.get('ruta_imagen')  # Ruta original de la imagen
            # Eliminar el '/' inicial de ruta_origen si existe
            ruta_path = Path(ruta_origen.lstrip('/'))
            # Concatenar con self.master_directory
            ruta_final = str(self.master_directory / ruta_path)
            if not ruta_origen:
                return jsonify({"error": "No se recibió la ruta de la imagen"}), 400
            print(f"Imagen cargada como: {ruta_origen}")
            self.copy_to_textures(ruta_final, file_name)
            return jsonify({"message": "Imagen preparada exitosamente", "ruta_de_origen": ruta_origen}), 200

        except Exception as e:
            print(f"Error al copiar la imagen: {e}")
            return jsonify({"error": "Error al copiar la imagen"}), 500

    def refrescar_tatuaje(self):
        """
        Actualiza y refresca las imágenes de tatuajes.
        """

        try:
            print("Refresco tatuaje")
            # Verificar si tonalidadPredicha está disponible
            print(self.tonalidadPredicha)
            if self.tonalidadPredicha is None:
                return jsonify({"error": "Tonalidad de piel no está definida"}), 500

            print("Proceso de prediccion")
            # Reinicializar el controlador con la imagen procesada más reciente
            processed_file_path = os.path.join(self.processed_folder, "piel2.jpg")
            self.controlador = Controlador(processed_file_path)

            # Obtener tatuajes actualizados
            print("Obteniendo tatuajes actualizados...")
            tatuajes = self.controlador.obtener_actualizacion_tatuajes(self.tonalidadPredicha)

            # Guardar las imágenes y generar URLs
            self.guardar_imagen(tatuajes)
            tattoos = [
                url_for('static', filename=f"tatuajesSugeridos/{filename}")
                for filename in os.listdir(self.path_tatuajes)
                if filename.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]

            return jsonify({"tatuajes": tattoos}), 200

        except Exception as e:
            print(f"Error al refrescar tatuajes: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500
