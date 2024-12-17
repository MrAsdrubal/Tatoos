
from typing import Any
import cv2
import numpy as np
from PIL import Image
from PIL.ImageFile import ImageFile

from ModeloIA.LogicaNegocio.Imagen import Imagen
import torch

class Preprocesamiento:

    etiquetas = ["claro", "mestizo", "negro"]

    @staticmethod
    def procesar(imagen: Imagen) -> torch.Tensor:
        """
        Realiza el preprocesamiento de la imagen (escalado, normalización, etc.).

        Args:
            imagen (Imagen): Instancia de la clase Imagen a procesar.

        Returns:
            Tensor: Imagen procesada lista para la predicción.
        """
        from torchvision import transforms
        from PIL import Image

        # 1. Definir las transformaciones necesarias
        transformaciones = transforms.Compose([
            transforms.Resize((224, 224)),            # Redimensionar la imagen a 224x224
            transforms.ToTensor(),                   # Convertir la imagen a un tensor
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalización según ImageNet
        ])

        # 2. Verificar que la imagen está cargada
        if imagen.datos_Imagen is None:
            raise ValueError("La imagen no ha sido cargada. Use el método 'cargar' antes de procesarla.")

        try:
            # Asegurar que la imagen cargada es un objeto PIL.Image
            imagen_pil = imagen.datos_Imagen.convert('RGB')  # Convertir a RGB si no lo es
        except AttributeError as e:
            raise ValueError(f"La imagen cargada no es válida: {e}")

        # 3. Aplicar las transformaciones
        imagen_tensor = transformaciones(imagen_pil).unsqueeze(0)  # Agregar dimensión de batch

        return imagen_tensor

    @ staticmethod
    def resalte_tonalidad_piel(image: ImageFile, etiquetaPredicha: str) -> Image:
        """
        Realiza el ajuste de tonalidad de piel en la imagen proporcionada y la redimensiona a 32x32 píxeles.

        Args:
            image (ImageFile): Imagen de tipo PIL.ImageFile.
            etiquetaPredicha (str): Etiqueta de tonalidad ("claro", "mestizo", "moreno").

        Returns:
            PIL.Image: Imagen ajustada y redimensionada a 32x32 píxeles.
        """
        # Convertir ImageFile (PIL) a NumPy (RGB)
        image_pil = image.convert("RGB")  # Asegurar que la imagen está en RGB
        image_np = np.array(image_pil)    # Convertir a arreglo NumPy
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)  # Convertir RGB -> BGR para OpenCV

        match etiquetaPredicha:
            case "claro":
                alpha = 0.6
                hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
                v_channel = hsv_image[:, :, 2]  # Canal V (brillo)

                max_idx = np.unravel_index(np.argmax(v_channel, axis=None), v_channel.shape)
                brightest_color = image_bgr[max_idx[0], max_idx[1]]  # Color más claro en BGR

                brightest_mask = np.full_like(image_bgr, brightest_color, dtype=np.uint8)
                adjusted_image = cv2.addWeighted(image_bgr, 1 - alpha, brightest_mask, alpha, 0)

            case "mestizo":
                alpha = 0.6
                lower_hsv = np.array([5, 50, 80])
                upper_hsv = np.array([25, 200, 180])
                hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

                mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
                selected_pixels = image_bgr[mask > 0]

                if len(selected_pixels) > 0:
                    average_color = np.mean(selected_pixels, axis=0).astype(np.uint8)
                else:
                    average_color = np.array([128, 96, 80], dtype=np.uint8)

                average_color_mask = np.full_like(image_bgr, average_color)
                adjusted_image = cv2.addWeighted(image_bgr, 1 - alpha, average_color_mask, alpha, 0)

            case "negro":
                alpha = 0.5
                lower_hsv = np.array([5, 30, 40])
                upper_hsv = np.array([20, 180, 90])
                hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

                mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
                selected_pixels = image_bgr[mask > 0]

                if len(selected_pixels) > 0:
                    average_color = np.mean(selected_pixels, axis=0).astype(np.uint8)
                else:
                    average_color = np.array([102, 52, 22], dtype=np.uint8)

                average_color_mask = np.full_like(image_bgr, average_color)
                smoothed_image = cv2.GaussianBlur(image_bgr, (15, 15), 0)
                adjusted_image = cv2.addWeighted(smoothed_image, 1 - alpha, average_color_mask, alpha, 0)

            case _:
                raise ValueError("Etiqueta no reconocida. Use 'claro', 'mestizo' o 'negro'.")

        # Convertir la imagen ajustada de vuelta a RGB y redimensionar a 32x32
        final_image = Image.fromarray(cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2RGB))
        final_image = final_image.resize((64, 64), Image.Resampling.LANCZOS)  # Redimensionar con antialiasing

        return final_image



