#!/usr/bin/env python3
"""
QR Code Decoder and Validation Utility for INTELLIATTEND
Handles QR code decoding from images and validation against stored keys
"""

import os
import json
import cv2
import numpy as np
# Optional QR decoding import - graceful fallback if not available
try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("⚠️  pyzbar not available - QR decoding features disabled")
from PIL import Image
import hashlib
from datetime import datetime, timedelta
import base64
import io

class QRDecoder:
    """QR Code decoder and validator"""
    
    def __init__(self, config):
        self.config = config
        self.qr_keys_folder = config.get('QR_KEYS_FOLDER', 'QR_DATA/keys')
    
    def decode_qr_from_image(self, image_data, image_format='base64'):
        """
        Decode QR code from image data
        
        Args:
            image_data: Image data (base64 string, bytes, or file path)
            image_format: Format of image_data ('base64', 'bytes', 'path')
            
        Returns:
            List of decoded QR data strings
        """
        try:
            # Convert image data to OpenCV format
            if image_format == 'base64':
                # Decode base64 string
                if ',' in image_data:  # Remove data URL prefix if present
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
            elif image_format == 'bytes':
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
            elif image_format == 'path':
                if not os.path.exists(image_data):
                    raise FileNotFoundError(f"Image file not found: {image_data}")
                image = cv2.imread(image_data)
                
            else:
                raise ValueError(f"Unsupported image format: {image_format}")
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Decode QR codes
            if not PYZBAR_AVAILABLE:
                return []
            qr_codes = pyzbar.decode(image)
            
            decoded_data = []
            for qr in qr_codes:
                try:
                    qr_data = qr.data.decode('utf-8')
                    decoded_data.append({
                        'data': qr_data,
                        'type': qr.type,
                        'rect': qr.rect._asdict(),  # Bounding rectangle
                        'polygon': [point._asdict() for point in qr.polygon]  # Corner points
                    })
                except UnicodeDecodeError:
                    # Handle binary data
                    decoded_data.append({
                        'data': qr.data.hex(),
                        'type': qr.type,
                        'format': 'hex',
                        'rect': qr.rect._asdict(),
                        'polygon': [point._asdict() for point in qr.polygon]
                    })
            
            return decoded_data
            
        except Exception as e:
            print(f"Error decoding QR from image: {e}")
            return []
    
    def preprocess_image(self, image):
        """
        Preprocess image to improve QR code detection
        
        Args:
            image: OpenCV image
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return image
    
    def enhanced_qr_decode(self, image_data, image_format='base64'):
        """
        Enhanced QR decoding with multiple preprocessing techniques
        
        Args:
            image_data: Image data
            image_format: Format of image data
            
        Returns:
            List of decoded QR data with confidence scores
        """
        try:
            # Load original image
            if image_format == 'base64':
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                original = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif image_format == 'bytes':
                nparr = np.frombuffer(image_data, np.uint8)
                original = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif image_format == 'path':
                original = cv2.imread(image_data)
            else:
                raise ValueError(f"Unsupported format: {image_format}")
            
            if original is None:
                raise ValueError("Failed to load image")
            
            # Try multiple processing approaches
            processing_methods = [
                ('original', original),
                ('grayscale', cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)),
                ('preprocessed', self.preprocess_image(original))
            ]
            
            all_results = []
            
            for method_name, processed_img in processing_methods:
                try:
                    if not PYZBAR_AVAILABLE:
                        continue
                    qr_codes = pyzbar.decode(processed_img)
                    
                    for qr in qr_codes:
                        try:
                            qr_data = qr.data.decode('utf-8')
                            result = {
                                'data': qr_data,
                                'method': method_name,
                                'type': qr.type,
                                'rect': qr.rect._asdict(),
                                'polygon': [point._asdict() for point in qr.polygon],
                                'confidence': self.calculate_qr_confidence(qr)
                            }
                            all_results.append(result)
                        except UnicodeDecodeError:
                            pass  # Skip invalid encodings
                            
                except Exception as e:
                    print(f"Error with {method_name} method: {e}")
                    continue
            
            # Remove duplicates and sort by confidence
            unique_results = []
            seen_data = set()
            
            for result in sorted(all_results, key=lambda x: x['confidence'], reverse=True):
                if result['data'] not in seen_data:
                    unique_results.append(result)
                    seen_data.add(result['data'])
            
            return unique_results
            
        except Exception as e:
            print(f"Error in enhanced QR decode: {e}")
            return []
    
    def calculate_qr_confidence(self, qr_code):
        """
        Calculate confidence score for QR code detection
        
        Args:
            qr_code: pyzbar QR code object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            # Base confidence
            confidence = 0.5
            
            # Check polygon quality (4 corners expected)
            if len(qr_code.polygon) == 4:
                confidence += 0.2
            
            # Check rectangle area (larger is generally better)
            rect_area = qr_code.rect.width * qr_code.rect.height
            if rect_area > 10000:  # Reasonably sized QR code
                confidence += 0.2
            elif rect_area > 5000:
                confidence += 0.1
            
            # Check data length (INTELLIATTEND QR codes should be substantial)
            data_length = len(qr_code.data)
            if data_length > 100:  # Our QR codes are typically longer
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5
    
    def validate_qr_data(self, qr_data_str):
        """
        Validate QR data against stored secret keys
        
        Args:
            qr_data_str: QR code data string
            
        Returns:
            Validation result dictionary
        """
        try:
            # Parse QR data
            qr_data = json.loads(qr_data_str)
            
            # Extract required fields
            session_id = qr_data.get('sid')
            sequence = qr_data.get('seq')
            timestamp = qr_data.get('ts')
            version = qr_data.get('v')
            
            if not all([session_id, sequence is not None, timestamp, version]):
                return {
                    'valid': False,
                    'error': 'Missing required fields',
                    'details': 'QR code data is incomplete'
                }
            
            # Check version compatibility
            if version != '1.0':
                return {
                    'valid': False,
                    'error': 'Version mismatch',
                    'details': f'Expected version 1.0, got {version}'
                }
            
            # Check timestamp (not too old or too future)
            current_time = int(datetime.utcnow().timestamp())
            time_diff = abs(current_time - timestamp)
            
            if time_diff > 300:  # 5 minutes tolerance
                return {
                    'valid': False,
                    'error': 'Timestamp out of range',
                    'details': f'QR code is {time_diff} seconds old'
                }
            
            # Look for matching secret key file
            key_filename = f"key_s{session_id}_seq{sequence:03d}.json"
            key_path = os.path.join(self.qr_keys_folder, key_filename)
            
            if not os.path.exists(key_path):
                return {
                    'valid': False,
                    'error': 'Secret key not found',
                    'details': f'No key file found for session {session_id}, sequence {sequence}'
                }
            
            # Load and validate secret key
            with open(key_path, 'r') as f:
                secret_data = json.load(f)
            
            # Verify QR data matches secret
            if (secret_data.get('session_id') != session_id or 
                secret_data.get('sequence') != sequence):
                return {
                    'valid': False,
                    'error': 'Key mismatch',
                    'details': 'QR data does not match secret key'
                }
            
            # Check if QR has expired according to secret key
            expires_at = datetime.fromisoformat(secret_data.get('expires_at', ''))
            if datetime.utcnow() > expires_at:
                return {
                    'valid': False,
                    'error': 'QR code expired',
                    'details': f'QR expired at {expires_at}'
                }
            
            # Validate QR data hash
            stored_qr_data = secret_data.get('qr_data', '')
            if hashlib.md5(qr_data_str.encode()).hexdigest() != hashlib.md5(stored_qr_data.encode()).hexdigest():
                return {
                    'valid': False,
                    'error': 'Data integrity check failed',
                    'details': 'QR data has been tampered with'
                }
            
            # All validations passed
            return {
                'valid': True,
                'session_id': session_id,
                'sequence': sequence,
                'timestamp': timestamp,
                'base_token': secret_data.get('base_token'),
                'expires_at': expires_at.isoformat(),
                'details': 'QR code is valid'
            }
            
        except json.JSONDecodeError:
            return {
                'valid': False,
                'error': 'Invalid JSON format',
                'details': 'QR data is not valid JSON'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': 'Validation error',
                'details': str(e)
            }
    
    def process_student_scan(self, image_data, image_format='base64'):
        """
        Complete processing pipeline for student QR scan
        
        Args:
            image_data: Image data from student device
            image_format: Format of image data
            
        Returns:
            Processing result with validation
        """
        try:
            # Step 1: Decode QR codes from image
            qr_results = self.enhanced_qr_decode(image_data, image_format)
            
            if not qr_results:
                return {
                    'success': False,
                    'error': 'No QR code found',
                    'details': 'Could not detect any QR codes in the image'
                }
            
            # Step 2: Validate each QR code found
            validation_results = []
            
            for qr_result in qr_results:
                validation = self.validate_qr_data(qr_result['data'])
                validation_results.append({
                    'qr_data': qr_result['data'],
                    'confidence': qr_result['confidence'],
                    'method': qr_result['method'],
                    'validation': validation
                })
            
            # Step 3: Find the best valid QR code
            valid_results = [r for r in validation_results if r['validation']['valid']]
            
            if not valid_results:
                return {
                    'success': False,
                    'error': 'No valid QR codes found',
                    'details': 'QR codes detected but none passed validation',
                    'attempts': len(validation_results),
                    'validation_results': validation_results
                }
            
            # Return the highest confidence valid result
            best_result = max(valid_results, key=lambda x: x['confidence'])
            
            return {
                'success': True,
                'qr_data': best_result['qr_data'],
                'confidence': best_result['confidence'],
                'method': best_result['method'],
                'validation': best_result['validation'],
                'session_id': best_result['validation']['session_id'],
                'base_token': best_result['validation']['base_token'],
                'details': 'QR code successfully processed and validated'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'Processing error',
                'details': str(e)
            }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_image_format(image_data, max_size_mb=10):
    """
    Validate image format and size
    
    Args:
        image_data: Image data
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        Validation result
    """
    try:
        # Check size
        if len(image_data) > max_size_mb * 1024 * 1024:
            return {
                'valid': False,
                'error': f'Image too large (max {max_size_mb}MB)'
            }
        
        # Try to decode as image
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Base64 data URL
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
        else:
            image_bytes = image_data
        
        # Validate with PIL
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        
        return {
            'valid': True,
            'format': img.format,
            'size': img.size,
            'mode': img.mode
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Invalid image: {str(e)}'
        }

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_qr_decoder():
    """Test QR decoder functionality"""
    print("🧪 Testing QR Decoder...")
    
    config = {
        'QR_KEYS_FOLDER': 'QR_DATA/keys'
    }
    
    decoder = QRDecoder(config)
    
    # Test with sample data
    test_qr_data = {
        'v': '1.0',
        'sid': 1,
        'tok': 'test_token_123',
        'seq': 0,
        'ts': int(datetime.utcnow().timestamp()),
        'sec': 'test_security_token',
        'exp': int((datetime.utcnow() + timedelta(seconds=10)).timestamp())
    }
    
    test_data_str = json.dumps(test_qr_data, separators=(',', ':'))
    print(f"📝 Test QR Data: {test_data_str}")
    
    # Test validation
    result = decoder.validate_qr_data(test_data_str)
    print(f"✅ Validation Result: {result}")

if __name__ == "__main__":
    test_qr_decoder()