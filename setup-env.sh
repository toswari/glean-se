#!/bin/bash
#
# setup-env.sh - Environment Setup Script for FAQ RAG System
# 
# This script installs all required software and tools for the FAQ RAG system.
# Supports both macOS and WSL2/Ubuntu Linux.
#
# Usage:
#   ./setup-env.sh
#
# Requirements:
#   - sudo/admin privileges for system package installation
#   - Internet connection for downloading packages
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check if running in WSL2
        if grep -qi "microsoft" /proc/version 2>/dev/null; then
            OS="wsl2"
            log_info "Detected WSL2"
        else
            OS="ubuntu"
            log_info "Detected Ubuntu/Linux"
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
check_not_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Install Homebrew on macOS
install_homebrew() {
    if ! command_exists brew; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon
        if [[ "$(uname -m)" == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        log_success "Homebrew installed"
    else
        log_info "Homebrew already installed"
    fi
}

# Install Python
install_python() {
    if command_exists python3 && python3 --version | grep -q "3\.[1011]"; then
        log_info "Python 3.10+ already installed: $(python3 --version)"
        return
    fi
    
    log_info "Installing Python 3.11..."
    
    case $OS in
        macos)
            brew install python@3.11
            ;;
        wsl2|ubuntu)
            # Add deadsnakes PPA for latest Python
            sudo apt-get update
            sudo apt-get install -y software-properties-common
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt-get update
            sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
            ;;
    esac
    
    log_success "Python installed"
}

# Install Docker
install_docker() {
    if command_exists docker; then
        log_info "Docker already installed: $(docker --version)"
        return
    fi
    
    log_info "Installing Docker..."
    
    case $OS in
        macos)
            log_warning "Docker Desktop for Mac is required"
            log_info "Please download from: https://www.docker.com/products/docker-desktop/"
            log_info "Or install using Homebrew:"
            echo "  brew install --cask docker"
            ;;
        wsl2|ubuntu)
            sudo apt-get update
            sudo apt-get install -y ca-certificates curl gnupg
            sudo install -m 0755 -d /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            sudo chmod a+r /etc/apt/keyrings/docker.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin
            sudo usermod -aG docker $USER
            ;;
    esac
    
    log_success "Docker installed"
}

# Install Git
install_git() {
    if command_exists git; then
        log_info "Git already installed: $(git --version)"
        return
    fi
    
    log_info "Installing Git..."
    
    case $OS in
        macos)
            brew install git
            ;;
        wsl2|ubuntu)
            sudo apt-get update
            sudo apt-get install -y git
            ;;
    esac
    
    log_success "Git installed"
}

# Install curl
install_curl() {
    if command_exists curl; then
        log_info "curl already installed"
        return
    fi
    
    log_info "Installing curl..."
    
    case $OS in
        macos)
            brew install curl
            ;;
        wsl2|ubuntu)
            sudo apt-get update
            sudo apt-get install -y curl
            ;;
    esac
    
    log_success "curl installed"
}

# Install jq
install_jq() {
    if command_exists jq; then
        log_info "jq already installed"
        return
    fi
    
    log_info "Installing jq..."
    
    case $OS in
        macos)
            brew install jq
            ;;
        wsl2|ubuntu)
            sudo apt-get update
            sudo apt-get install -y jq
            ;;
    esac
    
    log_success "jq installed"
}

# Create Python virtual environment
setup_venv() {
    if [ -d ".venv" ]; then
        log_info "Virtual environment already exists"
        return
    fi
    
    log_info "Creating Python virtual environment..."
    python3 -m venv .venv
    log_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    log_info "Activating virtual environment..."
    source .venv/bin/activate
    log_success "Virtual environment activated"
}

# Install Python dependencies
install_dependencies() {
    if [ ! -f "requirements.txt" ]; then
        log_warning "requirements.txt not found, skipping dependency installation"
        return
    fi
    
    log_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Python dependencies installed"
}

# Setup environment variables
setup_env_vars() {
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env 2>/dev/null || touch .env
        log_warning "Please configure your .env file with required variables"
    else
        log_info ".env file already exists"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check Python
    if command_exists python3; then
        log_success "Python: $(python3 --version)"
    else
        log_error "Python not found"
        ((errors++))
    fi
    
    # Check Git
    if command_exists git; then
        log_success "Git: $(git --version)"
    else
        log_error "Git not found"
        ((errors++))
    fi
    
    # Check Docker
    if command_exists docker; then
        log_success "Docker: $(docker --version)"
    else
        log_error "Docker not found"
        ((errors++))
    fi
    
    # Check virtual environment
    if [ -d ".venv" ]; then
        log_success "Virtual environment: .venv exists"
    else
        log_error "Virtual environment not found"
        ((errors++))
    fi
    
    if [ $errors -gt 0 ]; then
        log_error "Verification failed with $errors error(s)"
        return 1
    fi
    
    log_success "All verifications passed!"
    return 0
}

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  FAQ RAG System - Environment Setup   ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
    
    check_not_root
    detect_os
    
    log_info "Starting environment setup for $OS..."
    echo
    
    install_curl
    install_git
    install_homebrew
    install_python
    install_docker
    install_jq
    
    echo
    setup_venv
    activate_venv
    install_dependencies
    setup_env_vars
    
    echo
    verify_installation
    
    echo
    log_success "Environment setup complete!"
    log_info "To activate the virtual environment, run: source .venv/bin/activate"
}

# Run main function
main "$@"
