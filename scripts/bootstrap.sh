#!/usr/bin/env bash

set -e

if ! command -v mise &> /dev/null; then
  echo "Mise not found. Installing..."
  curl https://mise.run | bash
  source "$HOME/.bashrc"
fi

mise install

if ! command -v copier &> /dev/null; then
  echo "Copier not found after mise install. Please check installation."
  exit 1
fi

copier copy . ../new-fastapi-service
cd ../new-fastapi-service

echo "Initializing git repo..."
git init
git add .
git commit -m "Initial commit from template"

echo "Remember to create a GitHub repo and push to it."
