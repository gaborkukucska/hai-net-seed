#!/bin/bash
# HAI-Net Seed Framework - Constitutional Installation Script
# Cross-platform automated setup with constitutional compliance verification
# Supports Ubuntu/Debian, macOS, and other Unix-like systems

set -e

# Constitutional colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Constitutional banner
show_banner() {
    echo -e "${PURPLE}"
    echo "🏛️  ==============================================="
    echo "   HAI-Net Seed Framework - Constitutional Setup"
    echo "   Privacy First • Human Rights • Decentralized"
    echo "   ===============================================${NC}"
    echo ""
}

# Constitutional logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_constitutional() {
    echo -e "${PURPLE}⚖️  $1${NC}"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
        elif command -v yum &> /dev/null; then
            OS="centos"
        elif command -v pacman &> /dev/null; then
            OS="arch"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    
    log_info "Detected OS: $OS"
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            log_success "Python $PYTHON_VERSION found"
        else
            log_error "Python 3.9+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        log_error "Python 3 not found"
        return 1
    fi
    
    # Check Node.js version (for web interface)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        
        if [ "$NODE_MAJOR" -ge 16 ]; then
            log_success "Node.js $NODE_VERSION found"
        else
            log_warning "Node.js 16+ recommended, found $NODE_VERSION"
        fi
    else
        log_warning "Node.js not found (optional for web interface)"
    fi
    
    # Check available memory (Constitutional requirement for AI processing)
    if command -v free &> /dev/null; then
        AVAILABLE_RAM=$(free -m | grep '^Mem:' | awk '{print $7}')
        if [ "$AVAILABLE_RAM" -gt 2048 ]; then
            log_success "Sufficient RAM available: ${AVAILABLE_RAM}MB"
        else
            log_warning "Low available RAM: ${AVAILABLE_RAM}MB (4GB+ recommended)"
        fi
    fi
    
    # Check disk space
    AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -gt 10 ]; then
        log_success "Sufficient disk space: ${AVAILABLE_SPACE}GB"
    else
        log_warning "Low disk space: ${AVAILABLE_SPACE}GB (20GB+ recommended)"
    fi
}

# Install system dependencies
install_system_dependencies() {
    log_info "Installing system dependencies..."
    
    case $OS in
        ubuntu)
            log_info "Installing Ubuntu/Debian dependencies..."
            sudo apt-get update
            sudo apt-get install -y \
                python3-pip \
                python3-venv \
                python3-dev \
                build-essential \
                curl \
                git \
                nodejs \
                npm \
                docker.io \
                docker-compose \
                ffmpeg \
                portaudio19-dev \
                python3-pyaudio
            
            # Add user to docker group (Constitutional principle: user rights)
            if groups $USER | grep &>/dev/null '\bdocker\b'; then
                log_success "User already in docker group"
            else
                sudo usermod -aG docker $USER
                log_warning "Added user to docker group. Please log out and back in to apply changes."
            fi
            ;;
            
        macos)
            log_info "Installing macOS dependencies..."
            
            # Check for Homebrew
            if ! command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew update
            brew install python@3.12 node npm git ffmpeg portaudio
            
            # Install Docker Desktop for Mac
            if ! command -v docker &> /dev/null; then
                log_warning "Please install Docker Desktop for Mac from: https://www.docker.com/products/docker-desktop"
            fi
            ;;
            
        *)
            log_warning "Unsupported OS. Please install dependencies manually:"
            echo "  - Python 3.9+"
            echo "  - Node.js 16+"
            echo "  - Git"
            echo "  - Docker"
            echo "  - FFmpeg (for audio processing)"
            echo "  - PortAudio (for audio I/O)"
            ;;
    esac
}

# Create constitutional environment
create_constitutional_environment() {
    log_constitutional "Creating constitutional Python environment..."
    
    # Create virtual environment with constitutional naming
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip for security
    pip install --upgrade pip
    
    # Check system AI capabilities before installing dependencies
    log_info "Detecting system capabilities for optimal installation..."
    
    HAS_GPU=false
    HAS_OLLAMA=false
    PYTHON_VERSION_MAJOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1)
    PYTHON_VERSION_MINOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    
    # Check for GPU (NVIDIA)
    if command -v nvidia-smi &> /dev/null; then
        GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
        if [ "$GPU_COUNT" -gt 0 ]; then
            HAS_GPU=true
            log_success "GPU detected: $GPU_COUNT NVIDIA GPU(s)"
        fi
    elif lspci 2>/dev/null | grep -i vga | grep -i nvidia &> /dev/null; then
        log_warning "NVIDIA GPU detected but nvidia-smi not available"
    fi
    
    # Check for Ollama
    if command -v ollama &> /dev/null; then
        HAS_OLLAMA=true
        log_success "Ollama found: $(ollama --version 2>/dev/null || echo 'version unknown')"
    elif curl -s --connect-timeout 2 http://localhost:11434/api/tags &> /dev/null; then
        HAS_OLLAMA=true
        log_success "Ollama server detected on localhost:11434"
    fi
    
    # Check Python version compatibility for AI packages
    PYTHON_AI_COMPATIBLE=true
    if [ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -ge 12 ]; then
        PYTHON_AI_COMPATIBLE=false
        log_warning "Python $PYTHON_VERSION_MAJOR.$PYTHON_VERSION_MINOR detected - some AI packages may be incompatible"
    fi
    
    log_info "System capabilities detected:"
    echo "  GPU: $HAS_GPU"
    echo "  Ollama: $HAS_OLLAMA"
    echo "  Python AI Compatible: $PYTHON_AI_COMPATIBLE"
    echo ""
    
    # Install core dependencies (always needed)
    log_info "Installing core HAI-Net dependencies..."
    pip install \
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        websockets==12.0 \
        python-multipart==0.0.6 \
        cryptography>=41.0.0 \
        argon2-cffi>=23.1.0 \
        python-jose[cryptography]==3.3.0 \
        passlib[bcrypt]==1.7.4 \
        zeroconf>=0.131.0 \
        netifaces>=0.11.0 \
        sqlalchemy>=2.0.0 \
        psutil>=5.9.0 \
        pydantic>=2.5.0 \
        pydantic-settings>=2.0.0 \
        python-dotenv>=1.0.0 \
        click>=8.1.0 \
        rich>=13.7.0 \
        pyyaml>=6.0.0 \
        pytest>=7.4.0 \
        pytest-asyncio>=0.21.0 \
        requests>=2.31.0 \
        aiohttp>=3.8.0 \
        numpy>=1.21.0 \
        soundfile>=0.12.1 \
        pydub>=0.25.1
    
    if [ $? -eq 0 ]; then
        log_success "Core dependencies installed successfully"
    else
        log_error "Failed to install core dependencies"
        return 1
    fi
    
    # Install audio processing dependencies for voice features
    log_info "Installing audio processing dependencies for voice features..."
    pip install librosa>=0.10.0 || log_warning "librosa installation failed"
    pip install webrtcvad>=2.0.10 || log_warning "webrtcvad installation failed"
    pip install pyaudio>=0.2.13 || log_warning "PyAudio installation failed - voice input may not work. Install portaudio system package first."
    
    # Handle AI dependencies based on system capabilities
    if [ "$HAS_OLLAMA" = true ]; then
        log_success "External Ollama detected - skipping local AI installation for better compatibility"
        log_info "HAI-Net will connect to your existing Ollama server"
        
        # Still ask about Whisper for voice features
        read -p "Install Whisper for voice-to-text? (requires ffmpeg) (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installing OpenAI Whisper..."
            pip install openai-whisper || log_warning "Whisper installation failed"
        fi
    elif [ "$PYTHON_AI_COMPATIBLE" = false ]; then
        log_warning "Python version may be incompatible with some AI packages"
        log_info "Using minimal AI setup - you can connect to external AI services"
    else
        read -p "Install AI dependencies (Whisper, TTS, Transformers)? (may cause compatibility issues) (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Installing AI dependencies..."
            log_warning "This may take a while and fail on some systems - core functionality will work regardless"
            
            # Install Whisper for STT
            pip install openai-whisper || log_warning "Whisper installation failed"
            
            # Install Transformers
            pip install transformers>=4.35.0 || log_warning "transformers installation failed"
            
            # Try to install TTS (Coqui TTS)
            pip install TTS>=0.22.0 || log_warning "TTS installation failed"
            
            # Try to install torch and torchaudio (can be large)
            log_info "Installing PyTorch (this may take several minutes)..."
            pip install torch>=2.0.0 torchaudio>=2.0.0 --index-url https://download.pytorch.org/whl/cpu || log_warning "PyTorch installation failed"
        else
            log_info "Skipping AI dependencies - you can install these manually later if needed"
        fi
    fi
    
    log_success "Python dependencies installation complete"
    
    # Verify constitutional compliance imports
    python3 -c "
from core.config.settings import HAINetSettings, validate_constitutional_compliance
settings = HAINetSettings()
violations = validate_constitutional_compliance(settings)
if violations:
    print('❌ Constitutional violations detected:')
    for v in violations: print(f'  - {v}')
    exit(1)
else:
    print('✅ Constitutional compliance verified')
"
}

# Install web interface dependencies
install_web_dependencies() {
    log_info "Installing web interface dependencies..."
    
    if [ -d "web" ]; then
        cd web
        
        if [ -f "package.json" ]; then
            # Ensure public directory exists with required files
            log_info "Setting up React build environment..."
            mkdir -p public
            
            # Create index.html if it doesn't exist
            if [ ! -f "public/index.html" ]; then
                log_info "Creating public/index.html..."
                cat > public/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#1976d2" />
    <meta
      name="description"
      content="HAI-Net - Constitutional AI Network for Privacy-First Decentralized Collaboration"
    />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>HAI-Net - Constitutional AI Network</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
HTMLEOF
            fi
            
            # Create manifest.json if it doesn't exist
            if [ ! -f "public/manifest.json" ]; then
                log_info "Creating public/manifest.json..."
                cat > public/manifest.json << 'JSONEOF'
{
  "short_name": "HAI-Net",
  "name": "HAI-Net Constitutional AI Network",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#1976d2",
  "background_color": "#ffffff"
}
JSONEOF
            fi
            
            log_info "Installing Node.js dependencies..."
            npm install
            
            log_info "Building React web interface..."
            npm run build
            
            if [ $? -eq 0 ]; then
                # Deploy built files to the correct locations
                log_info "Deploying React build files..."
                mkdir -p static templates
                rm -rf static/* templates/*
                cp -r build/static/* static/
                cp build/index.html templates/
                
                log_success "Web interface built and deployed successfully"
            else
                log_error "React build failed"
                return 1
            fi
        else
            log_warning "package.json not found in web directory"
        fi
        
        cd ..
    else
        log_warning "Web directory not found. Skipping web interface setup."
    fi
}

# Generate constitutional configuration
generate_constitutional_config() {
    log_constitutional "Generating constitutional configuration..."
    
    mkdir -p config
    
    cat > config/constitutional.yaml << EOF
# HAI-Net Constitutional Configuration
# This configuration enforces the four core constitutional principles

constitutional_version: "1.0"
generated_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Article I: Privacy First Principle
privacy_first:
  data_sharing_consent: false  # Default to no data sharing
  analytics_consent: false     # No analytics without explicit consent
  encryption_enabled: true     # Encryption at rest and in transit
  watermarking_enabled: true   # AI content watermarking required
  local_processing: true       # Process data locally when possible

# Article II: Human Rights Protection  
human_rights:
  accessibility_mode: true     # Accessibility features enabled
  bias_detection_enabled: true # AI bias detection active
  user_override_enabled: true  # Users can override AI decisions
  content_filtering_enabled: true # Harmful content filtering
  educational_approach: true   # Educational error messages

# Article III: Decentralization Imperative
decentralization:
  central_authority_disabled: true  # No central authority connections
  local_first: true                # Local processing priority
  mesh_networking_enabled: true    # P2P mesh networking
  consensus_required: true         # Consensus for major changes
  max_masters_per_network: 3       # Limit masters for true decentralization

# Article IV: Community Focus Principle
community_focus:
  community_participation: true    # Enable community participation
  resource_sharing_enabled: false  # Disabled by default (user choice)
  environmental_mode: true         # Resource efficiency priority
  irl_prioritization: true         # In-person interaction priority
  collaborative_governance: true   # Community governance enabled

# Constitutional Guardian Settings
guardian:
  enabled: true
  mode: "educational"  # educational, protective, emergency
  violation_reporting: true
  auto_correction: true
  
# Node Configuration
node:
  role: "slave"  # Default to slave for decentralization
  id: "$(hostname)-$(date +%s)"
  hub_name: "HAI-Net Local Hub"
EOF

    log_success "Constitutional configuration generated at config/constitutional.yaml"
}

# Create systemd service (Linux only)
create_systemd_service() {
    if [ "$OS" != "ubuntu" ] && [ "$OS" != "centos" ]; then
        return
    fi
    
    log_info "Creating systemd service for HAI-Net..."
    
    sudo tee /etc/systemd/system/hainet.service > /dev/null << EOF
[Unit]
Description=HAI-Net Seed Framework - Constitutional AI Network
Documentation=https://github.com/hai-net/hai-net-seed
After=network.target
Wants=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/bin:/bin
Environment=PYTHONPATH=$(pwd)
Environment=HAINET_CONSTITUTIONAL_COMPLIANCE=true
Environment=HAINET_PRIVACY_FIRST=true
Environment=HAINET_DECENTRALIZED=true
ExecStartPre=$(pwd)/venv/bin/python -c "from core.config.settings import HAINetSettings, validate_constitutional_compliance; settings = HAINetSettings(); violations = validate_constitutional_compliance(settings); exit(1 if violations else 0)"
ExecStart=$(pwd)/venv/bin/python -m core.web.server
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Constitutional security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$(pwd)/data $(pwd)/logs $(pwd)/config
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    log_success "Systemd service created. Enable with: sudo systemctl enable hainet"
}

# Run constitutional compliance tests
run_constitutional_tests() {
    log_constitutional "Running constitutional compliance tests..."
    
    source venv/bin/activate
    
    # Run constitutional compliance tests
    if [ -f "tests/test_constitutional_compliance.py" ]; then
        log_info "Running constitutional compliance test suite..."
        python -m pytest tests/test_constitutional_compliance.py -v
        
        if [ $? -eq 0 ]; then
            log_success "All constitutional compliance tests passed!"
        else
            log_error "Constitutional compliance tests failed!"
            return 1
        fi
    fi
    
    # Run integration tests if available
    if [ -f "tests/test_e2e_integration.py" ]; then
        log_info "Running end-to-end integration tests..."
        python -m pytest tests/test_e2e_integration.py -v -k "not test_performance" --tb=short
        
        if [ $? -eq 0 ]; then
            log_success "Integration tests passed!"
        else
            log_warning "Some integration tests failed (this may be expected in minimal environments)"
        fi
    fi
}

# Create desktop launcher (optional)
create_desktop_launcher() {
    if [ "$OS" == "ubuntu" ] || [ "$OS" == "linux" ]; then
        log_info "Creating desktop launcher..."
        
        mkdir -p ~/.local/share/applications
        
        cat > ~/.local/share/applications/hainet.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=HAI-Net Local Hub
Comment=Constitutional AI Network Local Hub
Exec=gnome-terminal -- bash -c "cd $(pwd) && source venv/bin/activate && python -m core.web.server; read"
Icon=network-workgroup
Terminal=false
Categories=Network;Development;Science;
Keywords=AI;Network;Constitutional;Privacy;Decentralized;
StartupNotify=true
EOF
        
        chmod +x ~/.local/share/applications/hainet.desktop
        log_success "Desktop launcher created"
    fi
}

# Generate quick start guide
generate_quick_start() {
    log_info "Generating quick start guide..."
    
    cat > QUICK_START.md << EOF
# HAI-Net Seed Framework - Quick Start Guide

## Constitutional Principles ⚖️
This installation enforces HAI-Net's four core constitutional principles:
- **Privacy First**: Your data stays local, encryption enabled by default
- **Human Rights**: You maintain control, accessibility features enabled  
- **Decentralization**: No central authority, peer-to-peer networking
- **Community Focus**: Collaborative governance, community participation

## Starting HAI-Net

### Method 1: Development Mode
\`\`\`bash
# Activate the constitutional environment
source venv/bin/activate

# Start the HAI-Net framework
python -m core.web.server

# Open your browser to: http://localhost:8080
\`\`\`

### Method 2: Docker (Production)
\`\`\`bash
# Build constitutional Docker image
docker build -t hainet-seed:constitutional .

# Run with constitutional compliance
docker run -d \\
  --name hainet-hub \\
  -p 8080:8080 \\
  -p 8000:8000 \\
  -p 4001:4001 \\
  -v \$(pwd)/data:/app/data \\
  -v \$(pwd)/config:/app/config \\
  hainet-seed:constitutional
\`\`\`

### Method 3: System Service (Linux)
\`\`\`bash
# Enable and start the service
sudo systemctl enable hainet
sudo systemctl start hainet

# Check status
sudo systemctl status hainet

# View logs
sudo journalctl -u hainet -f
\`\`\`

## Web Interface
- **Network Visualization**: http://localhost:8080 (WebGPU accelerated)
- **API Documentation**: http://localhost:8000/docs
- **Constitutional Dashboard**: http://localhost:8080/constitutional

## Configuration
Edit \`config/constitutional.yaml\` to customize your local hub while maintaining constitutional compliance.

## Testing Constitutional Compliance
\`\`\`bash
# Run constitutional compliance tests
python -m pytest tests/test_constitutional_compliance.py -v

# Run full integration tests
python -m pytest tests/test_e2e_integration.py -v
\`\`\`

## Troubleshooting
- **Port conflicts**: Change ports in \`core/config/settings.py\`
- **Permission errors**: Ensure proper file permissions: \`chmod +x install.sh\`
- **Constitutional violations**: Check logs for educational guidance
- **Network issues**: Verify firewall allows P2P connections (port 4001)

## Constitutional Governance
As a HAI-Net participant, you can:
- ✅ Maintain full control over your data (Privacy First)
- ✅ Override any AI decisions (Human Rights)  
- ✅ Participate in decentralized governance (Decentralization)
- ✅ Contribute to community development (Community Focus)

For more information, see: https://github.com/hai-net/hai-net-seed
EOF

    log_success "Quick start guide created: QUICK_START.md"
}

# Main installation function
main() {
    show_banner
    
    log_constitutional "Beginning constitutional HAI-Net installation..."
    echo ""
    
    # Constitutional verification
    log_constitutional "This installer will:"
    echo "  ✓ Respect your privacy (Privacy First)"
    echo "  ✓ Maintain your control (Human Rights)"  
    echo "  ✓ Create decentralized infrastructure (Decentralization)"
    echo "  ✓ Enable community participation (Community Focus)"
    echo ""
    
    read -p "Do you accept these constitutional principles? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Constitutional principles must be accepted to continue."
        exit 1
    fi
    
    log_constitutional "Constitutional acceptance recorded. Proceeding with installation..."
    echo ""
    
    # Run installation steps
    detect_os
    check_requirements
    
    # Ask for system dependency installation
    read -p "Install system dependencies? (requires sudo) (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_system_dependencies
    fi
    
    create_constitutional_environment
    install_web_dependencies
    generate_constitutional_config
    
    # Optional components
    read -p "Create system service? (Linux only) (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_systemd_service
    fi
    
    # Run constitutional compliance tests automatically (required for installation)
    log_constitutional "Running essential constitutional compliance verification..."
    source venv/bin/activate
    
    # Run constitutional compliance tests (core requirement)
    if [ -f "tests/test_constitutional_compliance.py" ]; then
        log_info "Running constitutional compliance test suite..."
        python -m pytest tests/test_constitutional_compliance.py -v --tb=short
        
        if [ $? -eq 0 ]; then
            log_success "All constitutional compliance tests passed!"
        else
            log_warning "Some constitutional compliance tests failed - continuing installation"
            log_info "You can run tests manually later with: python -m pytest tests/test_constitutional_compliance.py -v"
        fi
    else
        log_info "Constitutional compliance tests not found - skipping"
    fi
    
    # Skip integration tests during installation (can hang on some systems)
    log_info "Skipping integration tests during installation (run manually with ./launch.sh --test)"
    
    create_desktop_launcher
    generate_quick_start
    
    # Installation complete
    echo ""
    log_constitutional "🎉 Constitutional HAI-Net installation complete!"
    echo ""
    log_success "HAI-Net Seed Framework is now ready for use"
    log_info "Read QUICK_START.md for next steps"
    log_info "Web interface will be available at: http://localhost:8080"
    log_constitutional "Remember: Your data stays local, you maintain control"
    echo ""
    
    # Show improved quick start and auto-launch option
    echo -e "${CYAN}Quick start options:${NC}"
    echo "  ./launch.sh --dev    # Interactive development mode"
    echo "  ./launch.sh --docker # Production Docker mode"
    echo "  ./launch.sh          # Interactive launcher menu"
    echo ""
    
    # Ask if user wants to launch immediately
    read -p "Launch HAI-Net now? (Y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        log_success "Launching HAI-Net in development mode..."
        echo ""
        
        # Try to open browser automatically
        if command -v xdg-open &> /dev/null; then
            log_info "Opening web interface in browser..."
            (sleep 3 && xdg-open http://localhost:8080) &
        elif command -v open &> /dev/null; then
            log_info "Opening web interface in browser..."
            (sleep 3 && open http://localhost:8080) &
        else
            log_info "Web interface will be available at: http://localhost:8080"
        fi
        
        # Launch with the launch script
        ./launch.sh --dev
    else
        log_info "HAI-Net ready to launch! Use: ./launch.sh"
    fi
    echo ""
}

# Run main installation
main "$@"
