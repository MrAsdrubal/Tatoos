import torchvision.transforms as transforms
from ModeloIA.LogicaNegocio.Imagen import Imagen
import torch

class Preprocesamiento:

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
