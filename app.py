#!/usr/bin/env python
"""
Flask Web API for Contradiction Detection Engine
Provides REST API endpoints for deploying on Render
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from contradiction_engine.streaming import StreamingReader
from contradiction_engine.claims_simple import ClaimExtractor, ClaimStore
from contradiction_engine.reasoning import SimplifiedContradictionDetector
from contradiction_engine.config import CONTRADICTION_DELTA_THRESHOLD

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'txt'}
UPLOAD_FOLDER = tempfile.gettempdir()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_claims_from_text(text: str, temp_path: str) -> list:
    """
    Extract claims from text.
    
    Args:
        text: Input text content
        temp_path: Temporary file path for streaming
        
    Returns:
        list: Extracted claims
    """
    # Save text to temporary file for streaming
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Extract claims
    reader = StreamingReader(temp_path)
    extractor = ClaimExtractor()
    
    all_claims = []
    chunk_id = 0
    
    for chunk_text in reader.stream_chunks():
        chunk_claims = extractor.extract_from_chunk(chunk_text, chunk_id)
        all_claims.extend(chunk_claims)
        chunk_id += 1
    
    return all_claims


def detect_contradictions_from_claims(claims: list, threshold: float) -> list:
    """
    Detect contradictions from claims.
    
    Args:
        claims: List of claims
        threshold: Contradiction threshold
        
    Returns:
        list: Detected contradictions
    """
    detector = SimplifiedContradictionDetector(threshold=threshold)
    contradictions = detector.detect(claims)
    return contradictions


@app.route('/')
def index():
    """Serve the main web interface."""
    return send_from_directory('static', 'index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint for Render."""
    return jsonify({
        'status': 'healthy',
        'service': 'Contradiction Detection Engine',
        'version': '1.0.0'
    })


@app.route('/api/info', methods=['GET'])
def info():
    """System information endpoint."""
    return jsonify({
        'name': 'Hybrid Neuro-Symbolic Contradiction Engine',
        'description': 'Detects logical contradictions in narratives',
        'mode': 'simplified',
        'max_file_size': f'{MAX_FILE_SIZE / 1024 / 1024}MB',
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'default_threshold': CONTRADICTION_DELTA_THRESHOLD
    })


@app.route('/api/detect', methods=['POST'])
def detect_contradictions():
    """
    Main endpoint for contradiction detection.
    
    Accepts either:
    - File upload (multipart/form-data)
    - Raw text (application/json with 'text' field)
    
    Returns:
    - JSON with contradictions or consistent status
    """
    try:
        # Get threshold from request
        threshold = float(request.form.get('threshold', CONTRADICTION_DELTA_THRESHOLD))
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                }), 400
            
            # Read file content
            content = file.read()
            
            # Check file size
            if len(content) > MAX_FILE_SIZE:
                return jsonify({
                    'error': f'File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB'
                }), 400
            
            text = content.decode('utf-8')
        
        # Handle JSON text input
        elif request.is_json:
            data = request.get_json()
            text = data.get('text', '')
            threshold = float(data.get('threshold', threshold))
            
            if not text:
                return jsonify({'error': 'No text provided'}), 400
        
        else:
            return jsonify({'error': 'Invalid request format'}), 400
        
        # Validate text length
        word_count = len(text.split())
        if word_count < 10:
            return jsonify({'error': 'Text too short. Need at least 10 words.'}), 400
        
        logger.info(f"Processing text: {word_count} words, threshold: {threshold}")
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
            temp_path = temp_file.name
            temp_file.write(text)
        
        try:
            # Extract claims
            logger.info("Extracting claims...")
            claims = extract_claims_from_text(text, temp_path)
            logger.info(f"Extracted {len(claims)} claims")
            
            if not claims:
                return jsonify({
                    'status': 'consistent',
                    'message': 'No claims extracted. Text may be too simple or lack factual statements.',
                    'word_count': word_count,
                    'claims_count': 0,
                    'contradictions_count': 0,
                    'contradictions': []
                })
            
            # Detect contradictions
            logger.info("Detecting contradictions...")
            contradictions = detect_contradictions_from_claims(claims, threshold)
            logger.info(f"Found {len(contradictions)} contradictions")
            
            # Format response
            if contradictions:
                status = 'contradictions_found'
                message = f'Found {len(contradictions)} contradiction(s)'
                contradictions_data = [c.to_dict() for c in contradictions]
            else:
                status = 'consistent'
                message = 'No contradictions found. Narrative appears consistent.'
                contradictions_data = []
            
            return jsonify({
                'status': status,
                'message': message,
                'word_count': word_count,
                'claims_count': len(claims),
                'contradictions_count': len(contradictions),
                'contradictions': contradictions_data,
                'threshold': threshold
            })
        
        finally:
            # Cleanup temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except UnicodeDecodeError:
        return jsonify({'error': 'Invalid text encoding. Please use UTF-8.'}), 400
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': f'Processing error: {str(e)}'}), 500


@app.route('/api/sample', methods=['GET'])
def sample_text():
    """Return sample text with contradictions for testing."""
    sample = """
    Lord Edmund Blackwood was a wealthy nobleman who lived in Ravencrest Manor. 
    He was known throughout the kingdom for his generosity and kindness.
    
    Lord Edmund had three sons: William, Henry, and George. William was the eldest 
    and would inherit the estate. The family lived peacefully for many years.
    
    One winter, a terrible plague struck the region. Lord Edmund Blackwood fell ill 
    and died within days. The entire kingdom mourned his loss.
    
    The following spring, Lord Edmund attended the royal court in London, where he 
    was celebrated for his contributions to the arts. He appeared healthy and vigorous, 
    greeting old friends with his characteristic warmth.
    
    After Lord Edmund's death, his eldest son William took over management of the estate.
    However, William was actually the youngest of the three brothers, not the eldest.
    """
    
    return jsonify({
        'text': sample.strip(),
        'description': 'Sample text with intentional contradictions about Lord Edmund Blackwood'
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {e}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
