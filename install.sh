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
                docker-compose
            
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
            brew install python@3.12 node npm git
            
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
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_warning "requirements.txt not found. Installing core dependencies..."
        pip install \
            fastapi \
            uvicorn \
            pydantic \
            pydantic-settings \
            cryptography \
            argon2-cffi \
            requests \
            psutil \
            zeroconf \
            netifaces \
            pytest \
            pytest-asyncio
    fi
    
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
            log_info "Installing Node.js dependencies..."
            npm install
            
            log_info "Building web interface..."
            npm run build
            
            log_success "Web interface built successfully"
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
    
    read -p "Run constitutional compliance tests? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_constitutional_tests
    fi
    
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
    
    # Show quick start command
    echo -e "${CYAN}Quick start:${NC}"
    echo "  source venv/bin/activate"
    echo "  python -m core.web.server"
    echo ""
}

# Run main installation
main "$@"
