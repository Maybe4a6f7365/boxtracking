#!/bin/bash

set -euo pipefail

declare -A COLORS=(
    [RED]='\033[0;31m'
    [GREEN]='\033[0;32m'
    [YELLOW]='\033[1;33m'
    [BLUE]='\033[0;34m'
    [PURPLE]='\033[0;35m'
    [CYAN]='\033[0;36m'
    [NC]='\033[0m'
)

readonly VENV_DIR="venv"
readonly PYTHON_CMD="python3"
readonly APP_NAME="VisionTrack"
readonly APP_DESCRIPTION="Viral Box Tracking Effect"
readonly BACKEND_URL="http://localhost:5000"
readonly FRONTEND_PATH="$HOME/boxtracking/index.html"

readonly REQUIRED_PACKAGES=(
    "flask:flask"
    "flask_cors:flask_cors"
    "numpy:numpy"
    "opencv-python:cv2"
    "werkzeug:werkzeug"
    "pillow:PIL"
)

log() {
    local level=$1
    local message=$2
    echo -e "${COLORS[$level]}$message${COLORS[NC]}"
}

log_header() {
    echo -e "${COLORS[CYAN]}$APP_NAME - $APP_DESCRIPTION${COLORS[NC]}"
    echo -e "${COLORS[CYAN]}$(printf '=%.0s' {1..50})${COLORS[NC]}"
    echo
}

log_section() {
    echo -e "${COLORS[YELLOW]}▶ $1${COLORS[NC]}"
}

log_success() {
    echo -e "${COLORS[GREEN]}✓ $1${COLORS[NC]}"
}

log_error() {
    echo -e "${COLORS[RED]}✗ $1${COLORS[NC]}"
}

log_info() {
    echo -e "${COLORS[BLUE]}ℹ $1${COLORS[NC]}"
}

check_python() {
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        log_error "Python 3 is required but not installed"
        log YELLOW "Please install Python 3 on your system:"
        log_info "Ubuntu/Debian: sudo apt install python3"
        log_info "Arch Linux: sudo pacman -S python"
        exit 1
    fi
    log_success "Python 3 found: $($PYTHON_CMD --version)"
}

setup_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        log_section "Creating Python virtual environment"
        $PYTHON_CMD -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
}

activate_venv() {
    log_section "Activating virtual environment"
    
    local current_shell
    current_shell=$(basename "$SHELL")
    log_info "Detected $current_shell shell"
    
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        source "$VENV_DIR/bin/activate"
        log_success "Virtual environment activated"
        
        if [[ "$VIRTUAL_ENV" == "$(pwd)/$VENV_DIR" ]]; then
            log_success "Virtual environment path confirmed: $VIRTUAL_ENV"
        else
            log YELLOW "Virtual environment may not be properly activated"
            log_info "Expected: $(pwd)/$VENV_DIR"
            log_info "Actual: ${VIRTUAL_ENV:-'Not set'}"
        fi
    else
        log_error "Virtual environment activation script not found"
        exit 1
    fi
}

is_package_installed() {
    local package_name=$1
    local import_name=${2:-$1}
    
    if "$VENV_DIR/bin/python" -c "import $import_name" 2>/dev/null; then
        log_success "$package_name already installed"
        return 0
    else
        return 1
    fi
}

install_packages() {
    log_section "Installing missing dependencies"
    
    log_info "Upgrading pip and build tools"
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel --quiet
    
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing from requirements.txt"
        if "$VENV_DIR/bin/pip" install -r requirements.txt --quiet; then
            log_success "Dependencies installed from requirements.txt"
            return 0
        else
            log YELLOW "requirements.txt installation failed, trying individual packages"
        fi
    fi
    
    declare -A PACKAGE_VERSIONS=(
        [Flask]=">=2.3.3"
        [Flask-CORS]=">=4.0.0"
        [numpy]=">=1.26.0"
        [opencv-python]=">=4.9.0.80"
        [Werkzeug]=">=2.3.7"
        [Pillow]=">=10.0.1"
    )
    
    for package in "${!PACKAGE_VERSIONS[@]}"; do
        log_info "Installing $package"
        "$VENV_DIR/bin/pip" install "$package${PACKAGE_VERSIONS[$package]}" --quiet
    done
    
    log_success "Individual package installation complete"
}

check_dependencies() {
    log_section "Checking installed dependencies"
    
    local all_installed=true
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        IFS=':' read -r package_name import_name <<< "$package"
        if ! is_package_installed "$package_name" "$import_name"; then
            all_installed=false
        fi
    done
    
    if [[ "$all_installed" == true ]]; then
        log_success "All dependencies already installed!"
    else
        install_packages
    fi
}

test_backend() {
    log_section "Testing backend startup"
    
    if [[ ! -f "app.py" ]]; then
        log_error "app.py not found in current directory"
        log YELLOW "Please ensure you're running this script from the correct directory"
        exit 1
    fi
    
    if "$VENV_DIR/bin/python" -c "
import sys
sys.path.insert(0, '.')
try:
    import app
    print('Backend module can be imported successfully')
except Exception as e:
    print(f'Backend import failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        log_success "Backend module test passed"
    else
        log YELLOW "Backend module test failed, but continuing (may work anyway)"
    fi
}

test_imports() {
    log_section "Testing imports"
    
    if "$VENV_DIR/bin/python" -c "
import cv2
import numpy as np
import flask
import flask_cors
from werkzeug.utils import secure_filename
from PIL import Image

print('All imports successful!')
print(f'OpenCV version: {cv2.__version__}')
print(f'NumPy version: {np.__version__}')
print(f'Flask version: {flask.__version__}')
print(f'Pillow version: {Image.__version__}')
" 2>/dev/null; then
        log_success "All imports successful!"
    else
        log_error "Import test failed"
        log YELLOW "Please check the error messages above and try again"
        exit 1
    fi
}

setup_directories() {
    log_section "Creating necessary directories"
    mkdir -p uploads outputs
    log_success "Directories created"
}

start_application() {
    log_section "Starting $APP_NAME backend"
    
    if [[ ! -f "app.py" ]]; then
        log_error "app.py not found in current directory"
        log YELLOW "Please ensure you're running this script from the correct directory"
        exit 1
    fi
    
    log_success "Backend will run on $BACKEND_URL"
    
    echo
    log CYAN "Starting Python application..."
    log YELLOW "Press Ctrl+C to stop the server"
    echo
    
    "$VENV_DIR/bin/python" app.py &
    local server_pid=$!
    
    log_info "Waiting for server to start..."
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s --connect-timeout 1 "$BACKEND_URL" >/dev/null 2>&1; then
            log_success "Server is running and responding"
            break
        fi
        
        if ! kill -0 "$server_pid" 2>/dev/null; then
            log_error "Backend process terminated unexpectedly"
            log YELLOW "Common issues to check:"
            log_info "1. Make sure app.py exists in the current directory"
            log_info "2. Check if port 5000 is already in use"
            log_info "3. Verify all dependencies are properly installed"
            log_info "4. Check the app.py file for syntax errors"
            exit 1
        fi
        
        sleep 1
        ((attempt++))
        
        if [[ $((attempt % 5)) -eq 0 ]]; then
            log_info "Still waiting for server to respond... (${attempt}s)"
        fi
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        log_error "Server failed to respond after ${max_attempts} seconds"
        kill "$server_pid" 2>/dev/null || true
        exit 1
    fi
    
    log_success "Server is ready! Opening frontend..."
    if [[ -f "$FRONTEND_PATH" ]] && command -v xdg-open &> /dev/null; then
        xdg-open "$FRONTEND_PATH" 2>/dev/null &
    fi
    
    echo
    log_success "🎉 Setup complete! Application started successfully!"
    log_info "Frontend: $FRONTEND_PATH"
    log_info "Backend: $BACKEND_URL"
    echo
    log CYAN "Server is running... (Press Ctrl+C to stop)"
    
    wait "$server_pid"
}

main() {
    log_header
    check_python
    setup_venv
    activate_venv
    check_dependencies
    test_imports
    test_backend
    setup_directories
    start_application
}

trap 'log_error "Script execution failed at line $LINENO"' ERR

main "$@"