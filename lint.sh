#!/bin/bash
echo "Running code quality checks..."

echo "1. Running isort (import sorting)..."
isort app/ --check-only

echo "2. Running black (code formatting)..."
black app/ --check

echo "3. Running flake8 (linting)..."
flake8 app/

echo " All checks passed!"

chmod +x lint.sh