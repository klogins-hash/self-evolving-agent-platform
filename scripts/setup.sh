#!/bin/bash

# Self-Evolving Agent Platform - Setup Script
echo "🚀 Setting up Self-Evolving Agent Platform MVP..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
else
    echo "✅ .env file already exists"
fi

# Setup backend
echo "🔧 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p tests/backend
mkdir -p tests/frontend
mkdir -p tests/integration

# Create basic test files
echo "🧪 Creating test structure..."
cat > tests/__init__.py << 'EOF'
# Test package
EOF

cat > tests/backend/__init__.py << 'EOF'
# Backend tests
EOF

cat > tests/frontend/__init__.py << 'EOF'
# Frontend tests
EOF

cat > tests/integration/__init__.py << 'EOF'
# Integration tests
EOF

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Start the backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "3. Start the frontend: cd frontend && source venv/bin/activate && chainlit run app.py"
echo "4. Or use Docker: docker-compose up"
echo ""
echo "🌐 Access the platform at:"
echo "   • Backend API: http://localhost:8000"
echo "   • Frontend UI: http://localhost:8001"
echo "   • API Docs: http://localhost:8000/docs"
