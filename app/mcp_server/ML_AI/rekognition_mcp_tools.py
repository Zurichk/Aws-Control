from typing import Dict, Any, List
import boto3
import os
import base64
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class RekognitionMCPTools:
    """Herramientas MCP para Amazon Rekognition"""

    def __init__(self):
        self.region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    def detect_labels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta etiquetas (objetos, escenas, acciones) en una imagen"""
        try:
            image_bytes = base64.b64decode(params['image_base64'])
            region = params.get('region', self.region)
            max_labels = params.get('max_labels', 10)
            min_confidence = params.get('min_confidence', 70.0)

            rekognition_client = boto3.client('rekognition', region_name=region)

            response = rekognition_client.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=max_labels,
                MinConfidence=min_confidence
            )

            labels = []
            for label in response.get('Labels', []):
                labels.append({
                    'name': label.get('Name', ''),
                    'confidence': round(label.get('Confidence', 0), 2),
                    'instances': len(label.get('Instances', [])),
                    'parents': [parent.get('Name', '') for parent in label.get('Parents', [])]
                })

            return {
                'labels': labels,
                'total_labels': len(labels),
                'region': region,
                'max_labels': max_labels,
                'min_confidence': min_confidence
            }

        except Exception as e:
            logger.exception(f"Error detectando etiquetas: {e}")
            return {
                'error': str(e),
                'labels': [],
                'message': f"Error al detectar etiquetas: {str(e)}"
            }

    def detect_faces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta rostros en una imagen y analiza sus atributos"""
        try:
            image_bytes = base64.b64decode(params['image_base64'])
            region = params.get('region', self.region)

            rekognition_client = boto3.client('rekognition', region_name=region)

            response = rekognition_client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )

            faces = []
            for face_detail in response.get('FaceDetails', []):
                face_info = {
                    'confidence': round(face_detail.get('Confidence', 0), 2),
                    'bounding_box': face_detail.get('BoundingBox', {}),
                    'age_range': face_detail.get('AgeRange', {}),
                    'gender': face_detail.get('Gender', {}),
                    'emotions': [{
                        'type': emotion.get('Type', ''),
                        'confidence': round(emotion.get('Confidence', 0), 2)
                    } for emotion in face_detail.get('Emotions', [])],
                    'smile': face_detail.get('Smile', {}),
                    'eyeglasses': face_detail.get('Eyeglasses', {}),
                    'sunglasses': face_detail.get('Sunglasses', {}),
                    'beard': face_detail.get('Beard', {}),
                    'mustache': face_detail.get('Mustache', {}),
                    'eyes_open': face_detail.get('EyesOpen', {}),
                    'mouth_open': face_detail.get('MouthOpen', {}),
                    'pose': face_detail.get('Pose', {}),
                    'quality': face_detail.get('Quality', {})
                }
                faces.append(face_info)

            return {
                'faces': faces,
                'total_faces': len(faces),
                'region': region
            }

        except Exception as e:
            logger.exception(f"Error detectando rostros: {e}")
            return {
                'error': str(e),
                'faces': [],
                'message': f"Error al detectar rostros: {str(e)}"
            }

    def compare_faces(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compara rostros entre dos imágenes para encontrar similitudes"""
        try:
            source_image_bytes = base64.b64decode(params['source_image_base64'])
            target_image_bytes = base64.b64decode(params['target_image_base64'])
            region = params.get('region', self.region)
            similarity_threshold = params.get('similarity_threshold', 80.0)

            rekognition_client = boto3.client('rekognition', region_name=region)

            response = rekognition_client.compare_faces(
                SourceImage={'Bytes': source_image_bytes},
                TargetImage={'Bytes': target_image_bytes},
                SimilarityThreshold=similarity_threshold
            )

            face_matches = []
            for match in response.get('FaceMatches', []):
                face_matches.append({
                    'similarity': round(match.get('Similarity', 0), 2),
                    'confidence': round(match.get('Face', {}).get('Confidence', 0), 2),
                    'bounding_box': match.get('Face', {}).get('BoundingBox', {})
                })

            unmatched_faces = []
            for face in response.get('UnmatchedFaces', []):
                unmatched_faces.append({
                    'confidence': round(face.get('Confidence', 0), 2),
                    'bounding_box': face.get('BoundingBox', {})
                })

            return {
                'face_matches': face_matches,
                'unmatched_faces': unmatched_faces,
                'total_matches': len(face_matches),
                'total_unmatched': len(unmatched_faces),
                'region': region,
                'similarity_threshold': similarity_threshold
            }

        except Exception as e:
            logger.exception(f"Error comparando rostros: {e}")
            return {
                'error': str(e),
                'face_matches': [],
                'unmatched_faces': [],
                'message': f"Error al comparar rostros: {str(e)}"
            }

    def detect_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta y extrae texto de una imagen"""
        try:
            image_bytes = base64.b64decode(params['image_base64'])
            region = params.get('region', self.region)

            rekognition_client = boto3.client('rekognition', region_name=region)

            response = rekognition_client.detect_text(
                Image={'Bytes': image_bytes}
            )

            detected_text = []
            for text_detection in response.get('TextDetections', []):
                detected_text.append({
                    'detected_text': text_detection.get('DetectedText', ''),
                    'confidence': round(text_detection.get('Confidence', 0), 2),
                    'type': text_detection.get('Type', ''),
                    'id': text_detection.get('Id', 0),
                    'parent_id': text_detection.get('ParentId'),
                    'bounding_box': text_detection.get('Geometry', {}).get('BoundingBox', {}),
                    'polygon': text_detection.get('Geometry', {}).get('Polygon', [])
                })

            # Separar texto por líneas y palabras
            lines = [text for text in detected_text if text['type'] == 'LINE']
            words = [text for text in detected_text if text['type'] == 'WORD']

            # Extraer todo el texto como una cadena
            full_text = ' '.join([line['detected_text'] for line in lines])

            return {
                'detected_text': detected_text,
                'lines': lines,
                'words': words,
                'full_text': full_text,
                'total_detections': len(detected_text),
                'total_lines': len(lines),
                'total_words': len(words),
                'region': region
            }

        except Exception as e:
            logger.exception(f"Error detectando texto: {e}")
            return {
                'error': str(e),
                'detected_text': [],
                'lines': [],
                'words': [],
                'full_text': '',
                'message': f"Error al detectar texto: {str(e)}"
            }

# Instancia global
rekognition_tools = RekognitionMCPTools()

# Definición de herramientas MCP
REKOGNITION_MCP_TOOLS = [
    {
        'name': 'detect_labels',
        'description': 'Detecta etiquetas (objetos, escenas, acciones) en una imagen usando Amazon Rekognition',
        'parameters': {
            'type': 'object',
            'properties': {
                'image_base64': {
                    'type': 'string',
                    'description': 'Imagen codificada en base64 para analizar'
                },
                'region': {
                    'type': 'string',
                    'description': 'Región de AWS (por defecto us-east-1)',
                    'default': 'us-east-1'
                },
                'max_labels': {
                    'type': 'integer',
                    'description': 'Número máximo de etiquetas a detectar',
                    'default': 10
                },
                'min_confidence': {
                    'type': 'number',
                    'description': 'Confianza mínima para considerar una etiqueta (0-100)',
                    'default': 70.0
                }
            },
            'required': ['image_base64']
        }
    },
    {
        'name': 'detect_faces',
        'description': 'Detecta rostros en una imagen y analiza sus atributos (edad, género, emociones, etc.)',
        'parameters': {
            'type': 'object',
            'properties': {
                'image_base64': {
                    'type': 'string',
                    'description': 'Imagen codificada en base64 para analizar'
                },
                'region': {
                    'type': 'string',
                    'description': 'Región de AWS (por defecto us-east-1)',
                    'default': 'us-east-1'
                }
            },
            'required': ['image_base64']
        }
    },
    {
        'name': 'compare_faces',
        'description': 'Compara rostros entre dos imágenes para encontrar similitudes',
        'parameters': {
            'type': 'object',
            'properties': {
                'source_image_base64': {
                    'type': 'string',
                    'description': 'Imagen fuente codificada en base64'
                },
                'target_image_base64': {
                    'type': 'string',
                    'description': 'Imagen objetivo codificada en base64'
                },
                'region': {
                    'type': 'string',
                    'description': 'Región de AWS (por defecto us-east-1)',
                    'default': 'us-east-1'
                },
                'similarity_threshold': {
                    'type': 'number',
                    'description': 'Umbral de similitud mínimo (0-100)',
                    'default': 80.0
                }
            },
            'required': ['source_image_base64', 'target_image_base64']
        }
    },
    {
        'name': 'detect_text',
        'description': 'Detecta y extrae texto de una imagen usando Amazon Rekognition',
        'parameters': {
            'type': 'object',
            'properties': {
                'image_base64': {
                    'type': 'string',
                    'description': 'Imagen codificada en base64 para analizar'
                },
                'region': {
                    'type': 'string',
                    'description': 'Región de AWS (por defecto us-east-1)',
                    'default': 'us-east-1'
                }
            },
            'required': ['image_base64']
        }
    }
]