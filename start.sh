#!/usr/bin/env bash

set -euo pipefail

declare -r SCRIPT_NAME="${0##*/}"
declare -r VENV_DIR="venv"
declare -r PYTHON_CMD="python3"
declare -r BACKEND_URL="http://127.0.0.1:5000"
declare -r FRONTEND_PATH="$(pwd)/index.html"

declare -r RED='\033[0;31m'
declare -r GREEN='\033[0;32m'
declare -r BLUE='\033[0;34m'
declare -r CYAN='\033[0;36m'
declare -r NC='\033[0m'

log() {
    local level="$1" color="$2" message="$3"
    printf '%b%s%b\n' "$color" "$message" "$NC" >&2
}

log_success() { log SUCCESS "$GREEN" "✓ $1"; }
log_error() { log ERROR "$RED" "✗ $1"; }
log_info() { log INFO "$BLUE" "ℹ $1"; }

cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script failed with exit code $exit_code"
    fi
    exit "$exit_code"
}

trap cleanup EXIT

die() {
    log_error "$1"
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "$1 is required but not installed"
}

require_file() {
    [[ -f "$1" ]] || die "$1 not found"
}

check_python() {
    require_command "$PYTHON_CMD"
    log_success "Python 3 found: $($PYTHON_CMD --version)"
}

setup_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        log_info "Creating virtual environment"
        "$PYTHON_CMD" -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    else
        log_success "Virtual environment exists"
    fi
    
    source "$VENV_DIR/bin/activate"
    log_success "Virtual environment activated"
}

install_dependencies() {
    log_info "Installing dependencies"
    require_file "requirements.txt"
    
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel --quiet
    "$VENV_DIR/bin/pip" install -r requirements.txt --quiet
    log_success "Dependencies installed"
}

test_imports() {
    log_info "Testing imports"
    "$VENV_DIR/bin/python" -c "
import cv2, numpy as np, flask, flask_cors
from werkzeug.utils import secure_filename
from PIL import Image
print('All imports successful!')
" >/dev/null 2>&1 || die "Import test failed"
    
    log_success "All imports successful!"
}

setup_directories() {
    mkdir -p uploads outputs
    log_success "Directories created"
}

wait_for_server() {
    local pid="$1" max_attempts=30 attempt=0
    
    log_info "Waiting for server..."
    sleep 3
    
    while ((attempt < max_attempts)); do
        if ! kill -0 "$pid" 2>/dev/null; then
            die "Backend process terminated"
        fi
        
        if curl -s --connect-timeout 2 "$BACKEND_URL" >/dev/null 2>&1; then
            log_success "Server is running"
            return 0
        fi
        
        sleep 1
        ((++attempt))
    done
    
    die "Server failed to respond after ${max_attempts} seconds"
}

open_frontend() {
    if [[ -f "$FRONTEND_PATH" ]] && command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$FRONTEND_PATH" >/dev/null 2>&1 &
        log_success "Opening frontend"
    fi
}

start_application() {
    log_info "Starting backend"
    require_file "app.py"
    
    "$VENV_DIR/bin/python" app.py &
    local server_pid=$!
    
    wait_for_server "$server_pid"
    
    sleep 2
    
    curl -s --connect-timeout 1 "$BACKEND_URL" >/dev/null 2>&1 || die "Server stopped responding"
    
    open_frontend
    
    printf '\n'
    log_success "Application started successfully"
    log_info "Frontend: $FRONTEND_PATH"
    log_info "Backend: $BACKEND_URL"
    printf '\n'
    log_info "Server is running... (Press Ctrl+C to stop)"
    
    wait "$server_pid"
}

main() {
    printf '%bBoxTracker - Video Motion Tracking%b\n' "$CYAN" "$NC"
    printf '%b%s%b\n' "$CYAN" "$(printf '=%.0s' {1..50})" "$NC"
    printf '\n'
    
    check_python
    setup_venv
    install_dependencies
    test_imports
    setup_directories
    start_application
}

main "$@"