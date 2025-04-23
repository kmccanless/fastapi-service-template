#!/usr/bin/env bash

set -euo pipefail

# Function to check for mise
function check_mise_installed() {
    if command -v mise >/dev/null 2>&1; then
        echo "✅ mise is already installed."
        return 0
    else
        return 1
    fi
}

# Function to install mise via Homebrew
function install_mise() {
    echo "🛠️ Installing mise ..."
    curl https://mise.run | sh
}

# Main script execution
if ! check_mise_installed; then
    install_mise
fi

echo "🎉 mise is ready to use!"
