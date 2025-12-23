#!/bin/bash

# Jarvis Assistant Installation Script
# Author: its4yus4
# License: MIT
# GitHub: https://github.com/its4yus4/jarvis-assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "    ╔══════════════════════════════════════════════╗"
    echo "    ║                                              ║"
    echo "    ║           🤖 Jarvis Assistant                ║"
    echo "    ║        Installation Script v2.1.0            ║"
    echo "    ║                MIT License                   ║"
    echo "    ║                                              ║"
    echo "    ╚══════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

show_license() {
    echo -e "${YELLOW}"
    echo "================================================"
    echo "                MIT LICENSE                     "
    echo "================================================"
    echo -e "${NC}"
    echo "Copyright (c) 2024 its4yus4"
    echo ""
    echo "Permission is hereby granted, free of charge, to any person obtaining a copy"
    echo "of this software and associated documentation files (the 'Software'), to deal"
    echo "in the Software without restriction, including without limitation the rights"
    echo "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell"
    echo "copies of the Software, and to permit persons to whom the Software is"
    echo "furnished to do so, subject to the following conditions:"
    echo ""
    echo "The above copyright notice and this permission notice shall be included in all"
    echo "copies or substantial portions of the Software."
    echo ""
    echo "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR"
    echo "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,"
    echo "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE"
    echo "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER"
    echo "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,"
    echo "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."
    echo -e "${YELLOW}"
    echo "================================================"
    echo -e "${NC}"
}

check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python3 not found. Please install Python 3.7 or higher."
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &>/dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 not found. Please install pip."
        exit 1
    fi
    
    # Check macOS version
    if [[ "$(uname)" == "Darwin" ]]; then
        MACOS_VERSION=$(sw_vers -productVersion)
        print_success "macOS $MACOS_VERSION detected"
    else
        print_error "This script is for macOS only."
        exit 1
    fi
}

install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Create virtual environment (optional)
    if [ ! -d "venv" ]; then
        print_step "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip3 install --upgrade pip
        pip3 install -r requirements.txt
        
        if [ $? -eq 0 ]; then
            print_success "Python dependencies installed"
        else
            print_error "Failed to install Python dependencies"
            exit 1
        fi
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install PyAudio (special handling for macOS)
    print_step "Installing PyAudio..."
    if command -v brew &>/dev/null; then
        brew install portaudio
        pip3 install pyaudio
        print_success "PyAudio installed via Homebrew"
    else
        print_warning "Homebrew not found. Trying to install PyAudio with pip..."
        pip3 install pyaudio
        
        if [ $? -ne 0 ]; then
            print_warning "PyAudio installation might fail. If so, run:"
            echo "  brew install portaudio"
            echo "  pip3 install pyaudio"
        else
            print_success "PyAudio installed"
        fi
    fi
}

setup_configuration() {
    print_step "Setting up configuration..."
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p images
    mkdir -p examples
    
    # Check if config files exist
    if [ ! -f "apps_config.json" ]; then
        print_warning "apps_config.json not found. It will be created on first run."
    fi
    
    if [ ! -f "config.json" ]; then
        print_warning "config.json not found. It will be created on first run."
    fi
    
    # Check if license file exists
    if [ ! -f "LICENSE" ]; then
        print_warning "LICENSE file not found. Creating MIT License..."
        cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Ayush kumar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
        print_success "Created LICENSE file"
    fi
    
    # Make scripts executable
    chmod +x jarvis.py
    if [ -f "setup.py" ]; then
        chmod +x setup.py
    fi
    
    print_success "Configuration setup complete"
}

setup_permissions() {
    print_step "Setting up permissions..."
    
    echo -e "${YELLOW}"
    echo "================================================"
    echo "IMPORTANT: Microphone Permission Required"
    echo "================================================"
    echo "After installation, you need to grant microphone"
    echo "permission to Terminal or Python in:"
    echo ""
    echo "System Preferences → Security & Privacy → Privacy"
    echo "→ Microphone"
    echo ""
    echo "1. Open System Preferences"
    echo "2. Go to Security & Privacy → Privacy"
    echo "3. Select Microphone from the left panel"
    echo "4. Check Terminal (and Python if listed)"
    echo "5. You may need to restart Terminal after granting"
    echo "================================================"
    echo -e "${NC}"
    
    read -p "Press Enter to continue..."
}

test_installation() {
    print_step "Testing installation..."
    
    # Test Python imports
    if python3 -c "import speech_recognition, pyttsx3, colorama" &>/dev/null; then
        print_success "Python imports working"
    else
        print_error "Python imports failed"
        exit 1
    fi
    
    # Test microphone access
    if python3 -c "
import speech_recognition as sr
try:
    m = sr.Microphone()
    print('Microphone access: OK')
except:
    print('Microphone access: Failed')
" | grep -q "OK"; then
        print_success "Microphone access OK"
    else
        print_warning "Microphone access may be blocked"
    fi
    
    print_success "Installation test complete"
}

show_usage() {
    print_step "Installation complete!"
    
    echo -e "${CYAN}"
    echo "================================================"
    echo "                 USAGE GUIDE                    "
    echo "================================================"
    echo -e "${NC}"
    
    echo -e "${GREEN}Start Jarvis:${NC}"
    echo "  python3 jarvis.py"
    echo ""
    echo -e "${GREEN}With specific mode:${NC}"
    echo "  python3 jarvis.py --mode wake       # Wake word (default)"
    echo "  python3 jarvis.py --mode continuous # Always listening"
    echo "  python3 jarvis.py --mode manual     # Type commands"
    echo "  python3 jarvis.py --mode test       # Run tests"
    echo ""
    echo -e "${GREEN}License information:${NC}"
    echo "  python3 jarvis.py --license"
    echo "  cat LICENSE"
    echo ""
    echo -e "${GREEN}Debug mode:${NC}"
    echo "  python3 jarvis.py --debug"
    echo ""
    echo -e "${GREEN}Help:${NC}"
    echo "  python3 jarvis.py --help"
    echo ""
    echo -e "${CYAN}================================================"
    echo "License: MIT"
    echo "Author: its4yus4"
    echo "GitHub: https://github.com/its4yus4/jarvis-assistant"
    echo -e "================================================${NC}"
}

main() {
    print_banner
    
    echo -e "${YELLOW}Jarvis Assistant - MIT License${NC}"
    echo -e "${CYAN}This script will install Jarvis and its dependencies.${NC}"
    echo ""
    
    # Show license information
    read -p "Show license information? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_license
    fi
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then 
        print_warning "Running as root is not recommended."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled."
            exit 1
        fi
    fi
    
    # Confirm installation
    read -p "Proceed with installation? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi

    #add directories
    #!/bin/bash

echo "🔧 Jarvis Assistant - Smart Installer"
echo "======================================"

# Auto-create directories
mkdir -p logs images examples

# Auto-create log file
touch logs/jarvis.log 2>/dev/null || true

# Auto-create configs if missing
if [ ! -f "config.json" ]; then
    echo '{
        "wake_word": "hey jarvis",
        "version": "2.2.0",
        "license": "MIT"
    }' > config.json
    echo "✅ Created config.json"
fi

if [ ! -f "apps_config.json" ]; then
    echo '{
        "applications": {},
        "system_commands": {}
    }' > apps_config.json
    echo "✅ Created apps_config.json"
fi

echo ""
echo "📁 Directory structure created:"
echo "   logs/          - Log files"
echo "   images/        - Screenshots"
echo "   examples/      - Example configs"
echo ""
echo "🎉 Jarvis is ready to use!"
echo "👉 Run: python jarvis.py"
    
    # Run installation steps
    check_requirements
    install_dependencies
    setup_configuration
    setup_permissions
    test_installation
    show_usage
    
    echo -e "\n${GREEN}✅ Installation complete!${NC}"
    echo -e "${YELLOW}Remember to grant microphone permissions before running Jarvis.${NC}"
}

# Run main function
main "$@"
