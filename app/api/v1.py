from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from functools import wraps
import hashlib
import os
import uuid
from datetime import datetime

from ..models.database import Image, User, APIKey, db
from ..providers.provider_factory import ProviderFactory
from ..providers.base import ImageGenerationRequest

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Hash the provided key and check against database
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_obj = APIKey.query.filter_by(key_hash=key_hash, is_active=True).first()
        
        if not api_key_obj:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Update last used timestamp
        api_key_obj.last_used = datetime.utcnow()
        db.session.commit()
        
        # Set current user context
        request.current_user = api_key_obj.user
        return f(*args, **kwargs)
    
    return decorated_function

@api_v1_bp.route('/generate', methods=['POST'])
@require_api_key
def generate_image():
    """API endpoint for image generation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        provider_name = data.get('provider')
        prompt = data.get('prompt')
        size = data.get('size', '1024x1024')
        style = data.get('style')
        
        if not provider_name or not prompt:
            return jsonify({'error': 'Provider and prompt are required'}), 400
        
        # Get API key for the provider
        api_key = current_app.config.get(f'{provider_name.upper()}_API_KEY')
        if not api_key:
            return jsonify({'error': f'Provider {provider_name} not configured'}), 500
        
        # Create provider and generate image
        try:
            provider = ProviderFactory.create_provider(provider_name, api_key)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        generation_request = ImageGenerationRequest(
            prompt=prompt,
            size=size,
            style=style
        )
        
        response = provider.generate_image(generation_request)
        
        if response.success:
            # Save image to local storage
            image_id = str(uuid.uuid4())
            filename = f"{image_id}.png"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure upload directory exists
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(response.image_data)
            
            # Save metadata to database
            image = Image(
                id=image_id,
                filename=filename,
                original_prompt=prompt,
                provider=provider_name,
                model=response.metadata.get('model', 'unknown'),
                size=size,
                style=style,
                user_id=request.current_user.id,
                file_size=len(response.image_data)
            )
            
            db.session.add(image)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'image_id': image_id,
                'image_url': f'/static/images/{filename}',
                'metadata': {
                    'prompt': prompt,
                    'provider': provider_name,
                    'model': response.metadata.get('model'),
                    'size': size,
                    'style': style,
                    'created_at': image.created_at.isoformat()
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': response.error_message
            }), 500
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_v1_bp.route('/images', methods=['GET'])
@require_api_key
def list_images():
    """List all images for the authenticated user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        provider_filter = request.args.get('provider')
        
        query = Image.query.filter_by(user_id=request.current_user.id)
        
        if provider_filter:
            query = query.filter_by(provider=provider_filter)
        
        images = query.order_by(Image.created_at.desc())\
                      .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'images': [{
                'id': img.id,
                'filename': img.filename,
                'image_url': f'/static/images/{img.filename}',
                'prompt': img.original_prompt,
                'provider': img.provider,
                'model': img.model,
                'size': img.size,
                'style': img.style,
                'created_at': img.created_at.isoformat(),
                'is_favorite': img.is_favorite
            } for img in images.items],
            'pagination': {
                'page': images.page,
                'pages': images.pages,
                'per_page': images.per_page,
                'total': images.total
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_v1_bp.route('/images/<image_id>', methods=['GET'])
@require_api_key
def get_image(image_id):
    """Get single image details"""
    try:
        image = Image.query.filter_by(id=image_id, user_id=request.current_user.id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        return jsonify({
            'success': True,
            'image': {
                'id': image.id,
                'filename': image.filename,
                'image_url': f'/static/images/{image.filename}',
                'prompt': image.original_prompt,
                'provider': image.provider,
                'model': image.model,
                'size': image.size,
                'style': image.style,
                'created_at': image.created_at.isoformat(),
                'is_favorite': image.is_favorite,
                'file_size': image.file_size
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_v1_bp.route('/images/<image_id>', methods=['DELETE'])
@require_api_key
def delete_image(image_id):
    """Delete an image"""
    try:
        image = Image.query.filter_by(id=image_id, user_id=request.current_user.id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Delete file from filesystem
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Image deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api_v1_bp.route('/providers', methods=['GET'])
@require_api_key
def list_providers():
    """List available image generation providers"""
    try:
        providers = []
        for provider_name in ProviderFactory.get_available_providers():
            # Check if API key is configured
            api_key = current_app.config.get(f'{provider_name.upper()}_API_KEY')
            if api_key:
                # Create temporary provider instance to get details
                provider = ProviderFactory.create_provider(provider_name, api_key)
                providers.append({
                    'name': provider_name,
                    'models': provider.get_available_models(),
                    'supported_sizes': provider.get_supported_sizes()
                })
        
        return jsonify({
            'success': True,
            'providers': providers
        })
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500