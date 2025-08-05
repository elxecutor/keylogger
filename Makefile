# Makefile for Encrypted Keylogger Project

.PHONY: help install install-dev test test-coverage lint format clean build dist deploy-windows deploy-macos deploy-linux uninstall

# Default target
help:
	@echo "Available commands:"
	@echo "  install       - Install the package"
	@echo "  install-dev   - Install with development dependencies"
	@echo "  test          - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint          - Run linting (flake8)"
	@echo "  format        - Format code (black)"
	@echo "  clean         - Clean build artifacts"
	@echo "  build         - Build the package"
	@echo "  dist          - Create distribution packages"
	@echo "  deploy-windows - Deploy on Windows"
	@echo "  deploy-macos  - Deploy on macOS"
	@echo "  deploy-linux  - Deploy on Linux"
	@echo "  uninstall     - Uninstall the package"

# Installation
install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

# Testing
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

dist: build
	@echo "Distribution packages created in dist/"

# Platform-specific deployment
deploy-windows:
	@echo "Deploying on Windows..."
	cd deployment/windows && ./install_windows_enhanced.bat

deploy-macos:
	@echo "Deploying on macOS..."
	cd deployment/macos && chmod +x install_macos.sh && ./install_macos.sh

deploy-linux:
	@echo "Deploying on Linux..."
	cd deployment/linux && chmod +x install_linux.sh && ./install_linux.sh

# Uninstallation
uninstall:
	pip uninstall encrypted-keylogger -y

# Quick commands
run:
	python src/keylogger.py

cli:
	python src/keylogger_cli.py

# Development workflow
dev-setup: install-dev
	@echo "Development environment set up successfully!"

dev-test: format lint test
	@echo "All development checks passed!"
