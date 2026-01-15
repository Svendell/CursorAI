#!/bin/bash
# Steam Auth Manager - Quick Setup Script

echo "=========================================="
echo "Steam Auth Manager - Quick Setup"
echo "=========================================="
echo ""

# Проверить Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

# Создать виртуальное окружение
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Активировать виртуальное окружение
echo ""
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✓ Virtual environment activated"

# Установить зависимости
echo ""
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Создать необходимые папки
echo ""
echo "Creating directories..."
mkdir -p mafiles backups logs data
echo "✓ Directories created"

# Показать инструкции
echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "To run the application:"
echo ""
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "  venv\Scripts\activate"
else
    echo "  source venv/bin/activate"
fi
echo "  python main.py"
echo ""
echo "To run tests:"
echo "  python tests.py"
echo ""
echo "To see examples:"
echo "  python example.py help"
echo ""
echo "Documentation:"
echo "  - README.md"
echo "  - INSTALL.md"
echo "  - DEVELOPER_GUIDE.md"
echo "  - PROJECT_SUMMARY.md"
echo ""
echo "=========================================="
