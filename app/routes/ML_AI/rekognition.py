from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
import boto3
import os
import base64
from io import BytesIO
from PIL import Image

rekognition = Blueprint('rekognition', __name__)

@rekognition.route('/rekognition')
def rekognition_dashboard():
    """Dashboard principal de Amazon Rekognition"""
    return render_template('ML_AI/rekognition/index.html')

@rekognition.route('/rekognition/labels', methods=['GET', 'POST'])
def detect_labels():
    """Detectar etiquetas en una imagen"""
    if request.method == 'POST':
        try:
            image_file = request.files.get('image')
            region = request.form.get('region', 'us-east-1')
            max_labels = int(request.form.get('max_labels', 10))
            min_confidence = float(request.form.get('min_confidence', 70.0))

            if not image_file:
                flash('Se requiere subir una imagen', 'error')
                return redirect(url_for('rekognition.detect_labels'))

            # Leer la imagen
            image_bytes = image_file.read()

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

            # Convertir imagen a base64 para mostrarla
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            image_format = Image.open(BytesIO(image_bytes)).format.lower()

            return render_template('ML_AI/rekognition/labels.html',
                                 labels=labels,
                                 image_b64=image_b64,
                                 image_format=image_format,
                                 region=region,
                                 max_labels=max_labels,
                                 min_confidence=min_confidence)

        except Exception as e:
            flash(f'Error detectando etiquetas: {str(e)}', 'error')
            return redirect(url_for('rekognition.detect_labels'))

    # GET request - mostrar formulario
    return render_template('ML_AI/rekognition/labels.html',
                         labels=None,
                         image_b64=None,
                         region='us-east-1',
                         max_labels=10,
                         min_confidence=70.0)

@rekognition.route('/rekognition/faces', methods=['GET', 'POST'])
def detect_faces():
    """Detectar rostros en una imagen"""
    if request.method == 'POST':
        try:
            image_file = request.files.get('image')
            region = request.form.get('region', 'us-east-1')

            if not image_file:
                flash('Se requiere subir una imagen', 'error')
                return redirect(url_for('rekognition.detect_faces'))

            # Leer la imagen
            image_bytes = image_file.read()

            rekognition_client = boto3.client('rekognition', region_name=region)

            response = rekognition_client.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['ALL']
            )

            faces = []
            for face_detail in response.get('FaceDetails', []):
                # Extraer información básica del rostro
                face_info = {
                    'confidence': round(face_detail.get('Confidence', 0), 2),
                    'bounding_box': face_detail.get('BoundingBox', {}),
                    'age_range': face_detail.get('AgeRange', {}),
                    'gender': face_detail.get('Gender', {}),
                    'emotions': face_detail.get('Emotions', []),
                    'smile': face_detail.get('Smile', {}),
                    'eyeglasses': face_detail.get('Eyeglasses', {}),
                    'sunglasses': face_detail.get('Sunglasses', {}),
                    'beard': face_detail.get('Beard', {}),
                    'mustache': face_detail.get('Mustache', {}),
                    'eyes_open': face_detail.get('EyesOpen', {}),
                    'mouth_open': face_detail.get('MouthOpen', {})
                }
                faces.append(face_info)

            # Convertir imagen a base64 para mostrarla
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            image_format = Image.open(BytesIO(image_bytes)).format.lower()

            return render_template('ML_AI/rekognition/faces.html',
                                 faces=faces,
                                 image_b64=image_b64,
                                 image_format=image_format,
                                 region=region)

        except Exception as e:
            flash(f'Error detectando rostros: {str(e)}', 'error')
            return redirect(url_for('rekognition.detect_faces'))

    # GET request - mostrar formulario
    return render_template('ML_AI/rekognition/faces.html',
                         faces=None,
                         image_b64=None,
                         region='us-east-1')

@rekognition.route('/rekognition/compare', methods=['GET', 'POST'])
def compare_faces():
    """Comparar rostros entre dos imágenes"""
    if request.method == 'POST':
        try:
            source_image = request.files.get('source_image')
            target_image = request.files.get('target_image')
            region = request.form.get('region', 'us-east-1')
            similarity_threshold = float(request.form.get('similarity_threshold', 80.0))

            if not source_image or not target_image:
                flash('Se requieren ambas imágenes para comparar', 'error')
                return redirect(url_for('rekognition.compare_faces'))

            # Leer las imágenes
            source_bytes = source_image.read()
            target_bytes = target_image.read()

            rekognition_client = boto3.client('rekognition', region_name=region)

            response = rekognition_client.compare_faces(
                SourceImage={'Bytes': source_bytes},
                TargetImage={'Bytes': target_bytes},
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

            # Convertir imágenes a base64
            source_b64 = base64.b64encode(source_bytes).decode('utf-8')
            target_b64 = base64.b64encode(target_bytes).decode('utf-8')
            source_format = Image.open(BytesIO(source_bytes)).format.lower()
            target_format = Image.open(BytesIO(target_bytes)).format.lower()

            return render_template('ML_AI/rekognition/compare.html',
                                 face_matches=face_matches,
                                 unmatched_faces=unmatched_faces,
                                 source_b64=source_b64,
                                 target_b64=target_b64,
                                 source_format=source_format,
                                 target_format=target_format,
                                 region=region,
                                 similarity_threshold=similarity_threshold)

        except Exception as e:
            flash(f'Error comparando rostros: {str(e)}', 'error')
            return redirect(url_for('rekognition.compare_faces'))

    # GET request - mostrar formulario
    return render_template('ML_AI/rekognition/compare.html',
                         face_matches=None,
                         unmatched_faces=None,
                         source_b64=None,
                         target_b64=None,
                         region='us-east-1',
                         similarity_threshold=80.0)

@rekognition.route('/rekognition/text', methods=['GET', 'POST'])
def detect_text():
    """Detectar texto en una imagen"""
    if request.method == 'POST':
        try:
            image_file = request.files.get('image')
            region = request.form.get('region', 'us-east-1')

            if not image_file:
                flash('Se requiere subir una imagen', 'error')
                return redirect(url_for('rekognition.detect_text'))

            # Leer la imagen
            image_bytes = image_file.read()

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

            # Convertir imagen a base64 para mostrarla
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            image_format = Image.open(BytesIO(image_bytes)).format.lower()

            return render_template('ML_AI/rekognition/text.html',
                                 detected_text=detected_text,
                                 image_b64=image_b64,
                                 image_format=image_format,
                                 region=region)

        except Exception as e:
            flash(f'Error detectando texto: {str(e)}', 'error')
            return redirect(url_for('rekognition.detect_text'))

    # GET request - mostrar formulario
    return render_template('ML_AI/rekognition/text.html',
                         detected_text=None,
                         image_b64=None,
                         region='us-east-1')