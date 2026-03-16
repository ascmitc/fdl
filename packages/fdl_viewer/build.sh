#!/bin/bash
#
# Build script for FDL Viewer application.
#
# Creates a standalone macOS/Windows/Linux application using PyInstaller.
# Sets up a clean virtual environment with all dependencies.
#
# Usage:
#   ./build.sh [options]
#
# Options:
#   --no-clean    Skip cleaning build directories
#   --no-sign     Skip code signing (macOS)
#   --no-dmg      Skip DMG creation (macOS)
#   --notarize    Notarize the app (macOS)
#   --no-venv     Skip virtual environment creation (use current Python)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.build_venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}FDL Viewer Build Script${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Parse arguments
NO_VENV=false
BUILD_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-venv)
            NO_VENV=true
            shift
            ;;
        --no-clean|--no-sign|--no-dmg|--notarize)
            BUILD_ARGS="$BUILD_ARGS $1"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check for Python
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required but not found"
    exit 1
fi

log_info "System Python: $(python3 --version)"
log_info "Repository root: $REPO_ROOT"
log_info "Build directory: $SCRIPT_DIR"

# Clean build directories first
log_step "Cleaning build directories..."

if [ -d "$SCRIPT_DIR/build" ]; then
    log_info "Removing build/..."
    rm -rf "$SCRIPT_DIR/build"
fi

if [ -d "$SCRIPT_DIR/dist" ]; then
    log_info "Removing dist/..."
    rm -rf "$SCRIPT_DIR/dist"
fi

# Remove any existing spec files
for spec_file in "$SCRIPT_DIR"/*.spec; do
    if [ -f "$spec_file" ]; then
        log_info "Removing $(basename "$spec_file")..."
        rm -f "$spec_file"
    fi
done

log_info "Clean complete"

# Setup virtual environment
if [ "$NO_VENV" = false ]; then
    log_step "Setting up build virtual environment..."

    # Clean existing venv
    if [ -d "$VENV_DIR" ]; then
        log_info "Removing existing build venv..."
        rm -rf "$VENV_DIR"
    fi

    # Create fresh venv
    log_info "Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"

    # Activate venv
    source "$VENV_DIR/bin/activate"

    log_info "Virtual environment activated"
    log_info "Python: $(which python)"
    log_info "Pip: $(which pip)"

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip --quiet
else
    log_warn "Skipping virtual environment setup (--no-venv)"
fi

# Install dependencies
log_step "Installing dependencies..."

# Install workspace sub-packages individually (pip doesn't support uv workspace sources)
log_info "Installing fdl package..."
pip install -e "$REPO_ROOT/packages/fdl" --quiet

log_info "Installing fdl-imaging package..."
pip install -e "$REPO_ROOT/packages/fdl_imaging" --quiet

# Install PySide6 explicitly (core dependency)
log_info "Installing PySide6..."
pip install "PySide6>=6.5.0" --quiet

# Install OpenImageIO (image processing dependency)
log_info "Installing OpenImageIO..."
pip install OpenImageIO --quiet

# Install PyInstaller (build dependency)
log_info "Installing PyInstaller..."
pip install "pyinstaller>=5.0" --quiet

# Install fdl_viewer package in development mode
log_info "Installing fdl_viewer package..."
pip install -e "$SCRIPT_DIR" --quiet

# Verify installations
log_step "Verifying installations..."

python -c "import PySide6; print(f'  PySide6: {PySide6.__version__}')"
python -c "import OpenImageIO; print(f'  OpenImageIO: {OpenImageIO.VERSION_STRING}')"
python -c "import PyInstaller; print(f'  PyInstaller: {PyInstaller.__version__}')"
python -c "import fdl; print('  fdl: OK')"
python -c "import fdl_imaging; print('  fdl_imaging: OK')"
python -c "import fdl_viewer; print(f'  fdl_viewer: {fdl_viewer.__version__}')"

# Run the build
log_step "Starting PyInstaller build..."
echo ""

cd "$SCRIPT_DIR"
# Always pass --no-clean since we already cleaned above
python compile.py --no-clean $BUILD_ARGS

echo ""
log_step "Build process complete!"

# Deactivate venv if we created one
if [ "$NO_VENV" = false ]; then
    deactivate 2>/dev/null || true
    log_info "Virtual environment deactivated"
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Build finished successfully!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Output location: $SCRIPT_DIR/dist/"
ls -la "$SCRIPT_DIR/dist/" 2>/dev/null || echo "  (dist directory not found)"
