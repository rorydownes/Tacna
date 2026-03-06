#!/usr/bin/env bash
# Idempotent environment setup for Temporal RCM PoC using Homebrew.
# Safe to run multiple times; skips steps already done.

set -e

# Project root: directory containing this script (script lives at repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"

# --- Homebrew ---
if ! command -v brew &>/dev/null; then
  echo "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Ensure brew is on PATH for this session (Apple Silicon / Linux)
  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /home/linuxbrew/.linuxbrew/bin/brew ]]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  fi
else
  echo "Homebrew already installed."
fi

# Ensure brew is available (e.g. after just installing)
if command -v brew &>/dev/null; then
  export PATH="$(brew --prefix)/bin:$(brew --prefix)/sbin:$PATH"
fi

# --- Docker (Docker Desktop on macOS) ---
if ! command -v docker &>/dev/null; then
  echo "Installing Docker Desktop (Homebrew cask)..."
  if ! brew install --cask docker; then
    echo "First attempt failed (e.g. hub-tool conflict). Retrying with --force..."
    brew install --cask docker --force || true
  fi
  if command -v docker &>/dev/null; then
    echo "Docker Desktop installed."
  else
    echo "Docker cask install had issues (e.g. existing /usr/local/bin/hub-tool). Install Docker manually from https://docker.com if needed."
  fi
else
  echo "Docker already installed ($(docker --version))."
fi

# --- Python 3.12 ---
PYTHON_VERSION="python@3.12"
if ! brew list "$PYTHON_VERSION" &>/dev/null; then
  echo "Installing $PYTHON_VERSION..."
  brew install "$PYTHON_VERSION"
else
  echo "$PYTHON_VERSION already installed."
fi

# Use brew's python@3.12 explicitly; avoid system python3 which may be 3.14 (unsupported by asyncpg/pydantic-core)
# Homebrew may put the versioned binary in bin/ (python3.12) or unversioned in libexec/bin/ (python3)
BREW_PYTHON_PREFIX="$(brew --prefix "$PYTHON_VERSION")"
for candidate in "$BREW_PYTHON_PREFIX/bin/python3.12" "$BREW_PYTHON_PREFIX/libexec/bin/python3" "$BREW_PYTHON_PREFIX/bin/python3"; do
  if [[ -x "$candidate" ]]; then
    PYTHON_BIN="$candidate"
    break
  fi
done
if [[ -z "${PYTHON_BIN:-}" || ! -x "$PYTHON_BIN" ]]; then
  echo "Error: $PYTHON_VERSION not found under $BREW_PYTHON_PREFIX (tried bin/python3.12, libexec/bin/python3, bin/python3). Run: brew install $PYTHON_VERSION"
  exit 1
fi

# --- Virtual environment ---
VENV_DIR="$PROJECT_ROOT/.venv"
REQUIRED_MAJOR=3
REQUIRED_MINOR=12
if [[ -d "$VENV_DIR" ]]; then
  EXISTING_VER="$("$VENV_DIR/bin/python" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)" || true
  if [[ "$EXISTING_VER" != "$REQUIRED_MAJOR.$REQUIRED_MINOR" ]]; then
    echo "Removing existing .venv (Python $EXISTING_VER) and recreating with Python $REQUIRED_MAJOR.$REQUIRED_MINOR..."
    rm -rf "$VENV_DIR"
  fi
fi
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment at $VENV_DIR with Python $REQUIRED_MAJOR.$REQUIRED_MINOR..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists at $VENV_DIR (Python $REQUIRED_MAJOR.$REQUIRED_MINOR)."
fi

# --- Project dependencies ---
PIP="$VENV_DIR/bin/pip"
if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
  echo "Installing Python dependencies (idempotent)..."
  "$PIP" install -q --upgrade pip
  "$PIP" install -q -r "$PROJECT_ROOT/requirements.txt"
else
  echo "No requirements.txt found; skipping pip install."
fi

# --- .env from example ---
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
  echo "Creating .env from .env.example..."
  cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
else
  echo ".env already exists; leaving unchanged."
fi

echo ""
echo "Setup complete. Next steps:"
echo "  1. Start Docker Desktop if it is not running (required for docker-compose)."
echo "  2. Start the stack:  docker compose up --build"
echo "  3. Submit a test claim:  $VENV_DIR/bin/python scripts/submit_test_claim.py"
echo "  Or activate the venv first:  source $VENV_DIR/bin/activate"
