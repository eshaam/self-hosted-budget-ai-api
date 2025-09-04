# Self-Hosted Budget AI API

A beautiful, self-hosted AI assistant powered by Qwen2-0.5B-Instruct with a modern React frontend and secure Python FastAPI backend.

## 📋 API

```curl -v -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secure-api-key-here" \
  -d '{"prompt": "Test with valid key"}'
```


## 🚀 Features

- **Modern UI**: Beautiful Tailwind CSS React frontend with animations and responsive design
- **Self-Hosted AI**: Uses Qwen2-0.5B-Instruct model for local AI inference
- **Secure**: API key authentication and IP whitelisting
- **Production Ready**: Includes deployment scripts with Fabric
- **Real-time Chat**: Interactive chat interface with loading animations
- **Copy to Clipboard**: Easy copying of AI responses

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- CUDA-compatible GPU (optional, for faster inference)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/self-hosted-budget-ai-api.git
cd self-hosted-budget-ai-api
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# The model will be automatically downloaded on first run
# This may take several minutes depending on your internet connection
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Build for production (optional)
npm run build
```

## 🔧 Configuration

### Backend Configuration

The backend uses environment variables and configuration files:

1. **Environment Variables** (`.env` file):
```env
DEV_MODE=true
API_KEYS_FILE=config/api_keys.txt
WHITELIST_FILE=config/whitelist.txt
MODEL_CACHE_DIR=models
MAX_NEW_TOKENS=512
TEMPERATURE=0.7
HOST=0.0.0.0
PORT=8000
```

2. **API Keys** (`config/api_keys.txt`):
```
demo-key-12345
your-secure-api-key-here
```

3. **IP Whitelist** (`config/whitelist.txt`):
```
127.0.0.1
::1
192.168.1.0/24
10.0.0.0/8
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000` in development mode.

## 🚀 Running the Application

### Development Mode

1. **Start the Backend**:
```bash
cd backend
source venv/bin/activate
python -m app.main
```

2. **Start the Frontend** (in a new terminal):
```bash
cd frontend
npm run dev
```

3. **Access the Application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

### Production Mode

Use the provided Fabric deployment scripts:

```bash
cd backend
fab setup --host=your-server.com --user=deploy
fab deploy --host=your-server.com --user=deploy
```

## 📖 API Documentation

### Generate Text

**POST** `/api/generate`

**Headers:**
- `Content-Type: application/json`
- `X-API-Key: your-api-key`

**Request Body:**
```json
{
  "prompt": "Your question or prompt here"
}
```

**Response:**
```json
{
  "response": "AI generated response"
}
```

## 🤖 Model Information

This application uses **Qwen2-0.5B-Instruct**, a compact yet powerful language model:

- **Size**: ~500MB
- **Context Length**: 32K tokens
- **Languages**: Multilingual support
- **Performance**: Optimized for efficiency and speed

### Model Download

The model will be automatically downloaded on first run to the `models/` directory. This includes:
- Model weights
- Tokenizer files
- Configuration files

**Download Size**: ~500MB
**Disk Space Required**: ~1GB (including cache)

## 🔒 Security Features

- **API Key Authentication**: All requests require valid API keys
- **IP Whitelisting**: Restrict access to specific IP addresses/ranges
- **Development Mode**: Automatic localhost access in dev mode
- **CORS Protection**: Configured for secure cross-origin requests

## 🚀 Deployment

### Using Fabric (Recommended)

1. **Initial Server Setup**:
```bash
fab setup --host=your-server.com --user=deploy
```

2. **Deploy Application**:
```bash
fab deploy --host=your-server.com --user=deploy
```

3. **Available Commands**:
```bash
fab status    # Check application status
fab logs      # View application logs
fab rollback  # Rollback to previous version
fab backup_config  # Backup configuration files
```

### Manual Deployment

1. **Server Requirements**:
   - Ubuntu 20.04+ or similar
   - Python 3.8+
   - Node.js 16+
   - Nginx
   - PM2 (for process management)

2. **Setup Steps**:
   - Clone repository to `/var/www/self-hosted-budget-ai-api`
   - Install dependencies
   - Configure Nginx reverse proxy
   - Start services with PM2

## 🎨 Frontend Features

- **Modern Design**: Glassmorphism UI with gradient backgrounds
- **Responsive**: Works on desktop, tablet, and mobile
- **Animations**: Smooth transitions with Framer Motion
- **Dark Theme**: Beautiful dark theme with purple/cyan accents
- **Real-time Chat**: Interactive chat interface
- **Loading States**: Animated loading indicators
- **Error Handling**: User-friendly error messages
- **Copy Functionality**: One-click copying of AI responses

## 🛠️ Development

### Project Structure

```
self-hosted-budget-ai-api/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # AI model handling
│   │   ├── auth.py          # Authentication
│   │   └── config.py        # Configuration
│   ├── config/              # Configuration files
│   ├── deploy/              # Deployment scripts
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   └── main.jsx        # React entry point
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind configuration
└── nginx/                  # Nginx configuration
```

### Adding New Features

1. **Backend**: Add new endpoints in `app/main.py`
2. **Frontend**: Modify `src/App.jsx` for UI changes
3. **Styling**: Use Tailwind CSS classes
4. **Deployment**: Update Fabric scripts as needed

## 🐛 Troubleshooting

### Common Issues

1. **Model Download Fails**:
   - Check internet connection
   - Ensure sufficient disk space
   - Try clearing the `models/` directory

2. **CUDA Out of Memory**:
   - Reduce `MAX_NEW_TOKENS` in `.env`
   - Use CPU inference by setting `CUDA_VISIBLE_DEVICES=""`

3. **Frontend Build Fails**:
   - Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

4. **API Authentication Errors**:
   - Verify API key in `config/api_keys.txt`
   - Check IP whitelist in `config/whitelist.txt`

### Performance Optimization

1. **GPU Acceleration**: Ensure CUDA is properly installed
2. **Model Caching**: Keep the `models/` directory for faster startup
3. **Memory Management**: Monitor system resources during inference

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## 🙏 Acknowledgments

- **Qwen Team**: For the excellent Qwen2-0.5B-Instruct model
- **Hugging Face**: For the transformers library
- **FastAPI**: For the amazing web framework
- **React & Tailwind**: For the beautiful frontend stack
