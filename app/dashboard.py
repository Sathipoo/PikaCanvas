from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models.database import Image, Tag, db
from .providers.provider_factory import ProviderFactory
from .providers.base import ImageGenerationRequest
import os
import uuid
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    # Get recent images for the user
    recent_images = Image.query.filter_by(user_id=current_user.id)\
                              .order_by(Image.created_at.desc())\
                              .limit(6).all()
    
    # Get available providers
    providers = ProviderFactory.get_available_providers()
    
    return render_template('dashboard/index.html', 
                         recent_images=recent_images,
                         providers=providers)

@dashboard_bp.route('/generate', methods=['POST'])
@login_required
def generate_image():
    """Handle image generation from web UI"""
    try:
        provider_name = request.form.get('provider')
        prompt = request.form.get('prompt')
        size = request.form.get('size', '1024x1024')
        style = request.form.get('style')
        
        if not provider_name or not prompt:
            flash('Provider and prompt are required')
            return redirect(url_for('dashboard.index'))
        
        # Get API key for the provider
        api_key = current_app.config.get(f'{provider_name.upper()}_API_KEY')
        if not api_key:
            flash(f'API key not configured for {provider_name}')
            return redirect(url_for('dashboard.index'))
        
        # Create provider and generate image
        provider = ProviderFactory.create_provider(provider_name, api_key)
        
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
                user_id=current_user.id,
                file_size=len(response.image_data)
            )
            
            db.session.add(image)
            db.session.commit()
            
            flash('Image generated successfully!')
        else:
            flash(f'Generation failed: {response.error_message}')
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/gallery')
@login_required
def gallery():
    """Image gallery page"""
    page = request.args.get('page', 1, type=int)
    provider_filter = request.args.get('provider')
    
    query = Image.query.filter_by(user_id=current_user.id)
    
    if provider_filter:
        query = query.filter_by(provider=provider_filter)
    
    images = query.order_by(Image.created_at.desc())\
                  .paginate(page=page, per_page=12, error_out=False)
    
    providers = ProviderFactory.get_available_providers()
    
    return render_template('gallery/index.html', 
                         images=images,
                         providers=providers,
                         current_provider=provider_filter)

@dashboard_bp.route('/image/<image_id>')
@login_required
def view_image(image_id):
    """View single image details"""
    image = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    return render_template('gallery/detail.html', image=image)

@dashboard_bp.route('/image/<image_id>/delete', methods=['POST'])
@login_required
def delete_image(image_id):
    """Delete an image"""
    image = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    
    # Delete file from filesystem
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Delete from database
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully')
    return redirect(url_for('dashboard.gallery'))

@dashboard_bp.route('/image/<image_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(image_id):
    """Toggle favorite status of an image"""
    image = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    image.is_favorite = not image.is_favorite
    db.session.commit()
    
    return redirect(request.referrer or url_for('dashboard.gallery'))