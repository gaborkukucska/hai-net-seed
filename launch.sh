#!/bin/bash
# HAI-Net Seed Framework - Constitutional Launch Script
# Easy startup with constitutional compliance verification
# Supports development, production, and service modes

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
    echo "🚀 ==============================================="
    echo "   HAI-Net Seed Framework - Constitutional Launch"
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

# Check if HAI-Net is installed
check_installation() {
    if [ ! -d "venv" ]; then
        log_error "Virtual environment not found. Please run ./install.sh first"
        exit 1
    fi
    
    if [ ! -f "core/config/settings.py" ]; then
        log_error "HAI-Net core files not found. Please run ./install.sh first"
        exit 1
    fi
    
    log_success "HAI-Net installation detected"
}

# Constitutional compliance check
verify_constitutional_compliance() {
    log_constitutional "Verifying constitutional compliance..."
    
    source venv/bin/activate
    
    # Run constitutional compliance verification
    python3 -c "
from core.config.settings import HAINetSettings, validate_constitutional_compliance

try:
    settings = HAINetSettings()
    violations = validate_constitutional_compliance(settings)
    
    if violations:
        print('❌ Constitutional violations detected:')
        for violation in violations:
            print(f'  - {violation}')
        exit(1)
    else:
        print('✅ Constitutional compliance verified')
        print('✅ Privacy First: Enabled')
        print('✅ Human Rights: Protected')
        print('✅ Decentralization: Active')
        print('✅ Community Focus: Enabled')
except Exception as e:
    print(f'❌ Constitutional verification failed: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_constitutional "All constitutional principles verified"
    else
        log_error "Constitutional compliance verification failed"
        exit 1
    fi
}

# Check for running processes and clean them up
check_running_processes() {
    log_info "Checking for running HAI-Net processes..."
    
    # Check for existing HAI-Net processes and terminate them
    if pgrep -f "core.web.server" > /dev/null; then
        log_warning "HAI-Net web server is already running. Cleaning up..."
        pkill -f "core.web.server"
        sleep 2 # Give it a moment to shut down
        log_success "Cleanup complete."
    fi
    
    # Check for port conflicts
    if netstat -ln 2>/dev/null | grep -q ":8080 "; then
        log_warning "Port 8080 is already in use"
    fi
    
    if netstat -ln 2>/dev/null | grep -q ":8000 "; then
        log_warning "Port 8000 is already in use"
    fi
}

# Show launch options
show_launch_options() {
    echo -e "${CYAN}HAI-Net Launch Options:${NC}"
    echo "  1) 🖥️  Development Mode (with logs)"
    echo "  2) 🌐 Web Interface Only"
    echo "  3) 🐳 Docker Production Mode"
    echo "  4) 🔧 Service Mode (systemd)"
    echo "  5) 🧪 Test Mode (constitutional tests)"
    echo "  6) 🛠️  Debug Mode (verbose logging)"
    echo "  0) ❌ Cancel"
    echo ""
}

# Launch development mode
launch_development() {
    log_info "Starting HAI-Net in development mode..."
    
    source venv/bin/activate
    
    # Set development environment variables
    export HAINET_MODE="development"
    export HAINET_LOG_LEVEL="DEBUG"
    export HAINET_CONSTITUTIONAL_COMPLIANCE="true"
    
    log_success "Starting constitutional AI network..."
    log_info "Web Interface: http://localhost:8080"
    log_info "API Documentation: http://localhost:8000/docs"
    log_info "Press Ctrl+C to stop"
    echo ""
    
    python -m core.web.server
}

# Launch web interface only
launch_web_only() {
    log_info "Starting HAI-Net web interface only..."
    
    source venv/bin/activate
    
    # Check if React build exists
    if [ ! -d "web/build" ] && [ -d "web" ]; then
        log_info "Building React web interface..."
        cd web
        npm run build
        cd ..
    fi
    
    export HAINET_MODE="web_only"
    export HAINET_LOG_LEVEL="INFO"
    
    log_success "Web interface starting..."
    log_info "Available at: http://localhost:8080"
    log_info "Press Ctrl+C to stop"
    echo ""
    
    python -c "
from core.web.server import create_app
import uvicorn

app = create_app()
uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')
"
}

# Launch Docker production mode
launch_docker() {
    log_info "Starting HAI-Net in Docker production mode..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker first"
        exit 1
    fi
    
    # Check if Docker image exists
    if ! docker image inspect hainet-seed:constitutional &> /dev/null; then
        log_info "Building constitutional Docker image..."
        docker build -t hainet-seed:constitutional .
    fi
    
    # Stop existing container if running
    if docker ps | grep -q hainet-hub; then
        log_info "Stopping existing HAI-Net container..."
        docker stop hainet-hub
        docker rm hainet-hub
    fi
    
    log_success "Starting constitutional Docker container..."
    
    docker run -d \
        --name hainet-hub \
        -p 8080:8080 \
        -p 8000:8000 \
        -p 4001:4001 \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/config:/app/config \
        -v $(pwd)/logs:/app/logs \
        --restart unless-stopped \
        hainet-seed:constitutional
    
    log_success "HAI-Net Docker container started"
    log_info "Container ID: $(docker ps | grep hainet-hub | cut -d' ' -f1)"
    log_info "Web Interface: http://localhost:8080"
    log_info "View logs: docker logs -f hainet-hub"
    log_info "Stop container: docker stop hainet-hub"
}

# Launch service mode
launch_service() {
    log_info "Managing HAI-Net system service..."
    
    if [ ! -f "/etc/systemd/system/hainet.service" ]; then
        log_error "System service not found. Run ./install.sh and create service"
        exit 1
    fi
    
    echo "Service Management Options:"
    echo "  1) Start service"
    echo "  2) Stop service" 
    echo "  3) Restart service"
    echo "  4) View status"
    echo "  5) View logs"
    echo ""
    
    read -p "Choose option (1-5): " -n 1 -r
    echo ""
    
    case $REPLY in
        1)
            sudo systemctl start hainet
            log_success "HAI-Net service started"
            ;;
        2)
            sudo systemctl stop hainet
            log_success "HAI-Net service stopped"
            ;;
        3)
            sudo systemctl restart hainet
            log_success "HAI-Net service restarted"
            ;;
        4)
            sudo systemctl status hainet
            ;;
        5)
            sudo journalctl -u hainet -f
            ;;
        *)
            log_error "Invalid option"
            exit 1
            ;;
    esac
}

# Launch test mode
launch_test_mode() {
    log_constitutional "Running constitutional compliance tests..."
    
    source venv/bin/activate
    
    # Run constitutional compliance tests
    log_info "Running constitutional compliance test suite..."
    python -m pytest tests/test_constitutional_compliance.py -v
    
    if [ $? -eq 0 ]; then
        log_success "Constitutional compliance tests passed!"
    else
        log_error "Constitutional compliance tests failed!"
        return 1
    fi
    
    # Ask about integration tests
    read -p "Run integration tests? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Running integration tests..."
        python -m pytest tests/test_e2e_integration.py -v --tb=short -k "not performance"
    fi
    
    log_success "Testing complete!"
}

# Launch debug mode
launch_debug() {
    log_info "Starting HAI-Net in debug mode..."
    
    source venv/bin/activate
    
    # Set debug environment variables
    export HAINET_MODE="debug"
    export HAINET_LOG_LEVEL="DEBUG"
    export HAINET_CONSTITUTIONAL_COMPLIANCE="true"
    export HAINET_VERBOSE_LOGGING="true"
    
    log_success "Debug mode active - verbose logging enabled"
    log_info "Web Interface: http://localhost:8080"
    log_info "API Documentation: http://localhost:8000/docs"
    log_info "All constitutional events will be logged"
    echo ""
    
    python -m core.web.server --debug
}

# Main launch function
main() {
    show_banner
    
    check_installation
    verify_constitutional_compliance
    check_running_processes
    
    echo ""
    show_launch_options
    
    read -p "Choose launch mode (0-6): " -n 1 -r
    echo ""
    echo ""
    
    case $REPLY in
        1)
            launch_development
            ;;
        2)
            launch_web_only
            ;;
        3)
            launch_docker
            ;;
        4)
            launch_service
            ;;
        5)
            launch_test_mode
            ;;
        6)
            launch_debug
            ;;
        0)
            log_info "Launch cancelled"
            exit 0
            ;;
        *)
            log_error "Invalid option. Please choose 0-6"
            exit 1
            ;;
    esac
}

# Show help
show_help() {
    echo "HAI-Net Launch Script - Constitutional AI Network"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --dev, -d        Launch development mode directly"
    echo "  --web, -w        Launch web interface only"
    echo "  --docker         Launch Docker production mode"
    echo "  --service, -s    Manage system service"
    echo "  --test, -t       Run constitutional tests"
    echo "  --debug          Launch debug mode"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Interactive mode: $0 (no arguments)"
    echo ""
}

# Handle command line arguments
if [ $# -eq 0 ]; then
    # No arguments - run interactive mode
    main
else
    case $1 in
        --dev|-d)
            show_banner
            check_installation
            verify_constitutional_compliance
            launch_development
            ;;
        --web|-w)
            show_banner
            check_installation
            verify_constitutional_compliance
            launch_web_only
            ;;
        --docker)
            show_banner
            check_installation
            launch_docker
            ;;
        --service|-s)
            show_banner
            launch_service
            ;;
        --test|-t)
            show_banner
            check_installation
            launch_test_mode
            ;;
        --debug)
            show_banner
            check_installation
            verify_constitutional_compliance
            launch_debug
            ;;
        --help|-h)
            show_help
            ;;
        *)
            log_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
fi
