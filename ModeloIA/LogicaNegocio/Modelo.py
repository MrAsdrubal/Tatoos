import torch
from pathlib import Path
from PIL import Image
from ModeloIA.LogicaNegocio.Imagen import Imagen  # Asegúrate de que esta importación sea válida.

class ModeloPrediccionPiel:
    """
    Clase encargada de cargar el modelo de predicción de tonalidad de piel
    y realizar predicciones basadas en imágenes procesadas.
    """

    def __init__(self, ruta_modelo: str):
        try:
            self.modeloCargado = torch.load(ruta_modelo, map_location=torch.device('cpu'), weights_only=False)
            self.modeloCargado.eval()  # Configurar el modelo en modo evaluación
        except Exception as e:
            raise ValueError(f"Error al cargar el modelo desde {ruta_modelo}: {e}")

        self.clases = ['claro', 'mestizo', 'moreno']

    def predecir(self, imagen: torch.Tensor) -> str:
        """
        Realiza la predicción de la tonalidad de piel basada en la imagen procesada.
        
        Args:
            imagen (torch.Tensor): Imagen preprocesada y convertida en un tensor.

        Returns:
            str: La clase predicha ('claro', 'mestizo', 'moreno').
        """
        if not isinstance(imagen, torch.Tensor):
            raise TypeError("La entrada debe ser un torch.Tensor preprocesado.")
        
        try:
            with torch.no_grad():
                salida = self.modeloCargado(imagen)  # Pasar la imagen al modelo
            _, indice_predicho = torch.max(salida, 1) 
                # Obtener índice de la clase predicha
            return self.clases[indice_predicho.item()]
        except Exception as e:
            raise RuntimeError(f"Error durante la predicción: {e}")


    