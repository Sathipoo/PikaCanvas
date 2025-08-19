# 🎨 PikaCanvas - Multi-Model AI Image Generation Platform

PikaCanvas is a comprehensive Flask-based web application and API platform that enables users to generate images using multiple AI model providers including OpenAI DALL-E, Stability AI, Google Gemini, and more.

## ✨ Features

### 🖼️ Multi-Provider Support
- **OpenAI DALL-E 3** - High-quality image generation
- **Stability AI** - Stable Diffusion models
- **Google Gemini** - (Coming soon)
- **Grok** - (Coming soon)

### 🌐 Dual Interface
- **Web Dashboard** - User-friendly interface for interactive image generation
- **REST API** - Programmatic access for integrations and automation

### 📚 Image Gallery
- Organized image library with metadata
- Filter by provider, date, and user
- Favorite images and download capabilities
- Image sharing and URL generation

### 🔐 Authentication
- Web-based login system
- API key authentication for programmatic access
- Multi-user support with isolated galleries

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pikacanvas
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Web Interface: http://localhost:5000
   - API Documentation: http://localhost:5000/api/v1

### Demo Accounts
- **Admin**: `admin` / `admin123`
- **Demo**: `demo` / `demo123`

## 🔧 Configuration

### Environment Variables
```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///pikacanvas.db

# API Keys
OPENAI_API_KEY=your_openai_api_key
STABILITY_API_KEY=your_stability_api_key
GOOGLE_API_KEY=your_google_api_key
GROK_API_KEY=your_grok_api_key

# Storage
UPLOAD_FOLDER=app/static/images
MAX_CONTENT_LENGTH=16777216
```

## 📖 API Usage

### Authentication
Include your API key in the request headers:
```bash
X-API-Key: your-api-key-here
```

### Generate Image
```bash
POST /api/v1/generate
Content-Type: application/json

{
  "provider": "openai",
  "prompt": "a majestic castle on a floating island",
  "size": "1024x1024",
  "style": "fantasy-art"
}
```

### List Images
```bash
GET /api/v1/images?page=1&per_page=20&provider=openai
```

### Get Image Details
```bash
GET /api/v1/images/{image_id}
```

### Delete Image
```bash
DELETE /api/v1/images/{image_id}
```

## 🏗️ Architecture

```
PikaCanvas/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── auth.py              # Authentication routes
│   ├── dashboard.py         # Web dashboard routes
│   ├── models/
│   │   └── database.py      # SQLAlchemy models
│   ├── providers/
│   │   ├── base.py          # Abstract provider class
│   │   ├── openai_provider.py
│   │   ├── stability_provider.py
│   │   └── provider_factory.py
│   ├── api/
│   │   └── v1.py            # API v1 endpoints
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS, images
├── requirements.txt
├── run.py                   # Application entry point
└── README.md
```

## 🎯 Roadmap

### Phase 1: MVP ✅
- [x] Flask application setup
- [x] OpenAI & Stability AI integration
- [x] Web dashboard
- [x] Basic API endpoints
- [x] Local image storage
- [x] User authentication

### Phase 2: Enhancements
- [ ] Google Gemini integration
- [ ] Grok API integration
- [ ] API key management
- [ ] Advanced filtering & search
- [ ] PostgreSQL migration

### Phase 3: Advanced Features
- [ ] AWS S3 integration
- [ ] Batch image generation
- [ ] Webhooks for async notifications
- [ ] Analytics dashboard
- [ ] Docker deployment

## 🛠️ Development

### Project Structure
- **Models**: SQLAlchemy models for database entities
- **Providers**: Abstracted AI provider integrations
- **API**: RESTful API endpoints
- **Templates**: Jinja2 HTML templates
- **Static**: CSS, JavaScript, and image assets

### Adding New Providers
1. Create a new provider class inheriting from `BaseImageProvider`
2. Implement required methods: `generate_image()`, `get_available_models()`, `get_supported_sizes()`
3. Register the provider in `ProviderFactory`

### Database Schema
- **Users**: Authentication and user management
- **Images**: Generated image metadata
- **Tags**: Image categorization
- **APIKeys**: API authentication tokens

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API examples

---

**PikaCanvas** - Unleash your creativity with AI-powered image generation! 🎨✨
