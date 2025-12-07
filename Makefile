# Declare all phony targets
.PHONY: install clean lint code_check check-dead-code pipeline all

# Default target
.DEFAULT_GOAL := all

# Variables
SRC_PROJECT_NAME ?= morphx
SRC_PROJECT_TESTS ?= tests
SRC_ALL ?= .

# Install project dependencies
install:
	@echo "Installing dependencies..."
	@uv sync --all-extras
	@echo "✅ Dependencies installed."

# Clean cache and temporary files
clean:
	@echo "Cleaning cache and temporary files..."
	@find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete."

# Check code formatting and linting
lint:
	@echo "Running lint checks..."
	@uv run ruff check --fix $(SRC_ALL)/
	@uv run ruff format $(SRC_ALL)/
	@uv run nbqa ruff $(SRC_ALL)/
	@uv run isort $(SRC_ALL)/
	@uv run nbqa isort $(SRC_ALL)/
	@echo "✅ Linting complete."

# Static analysis and security checks
code_check:
	@echo "Running static code checks..."
	@uv run mypy $(SRC_PROJECT_NAME)/
	@uv run complexipy -f $(SRC_PROJECT_NAME)/
	@uv run bandit -r $(SRC_PROJECT_NAME)/ --exclude $(SRC_PROJECT_TESTS)
	@echo "✅ Code and security checks complete."

# Check dead code
check-dead-code:
	@echo "Checking dead code..."
	@uv run deadcode $(SRC_PROJECT_NAME)
	@echo "✅ Dead code check complete."

# Run code checks
pipeline: clean lint code_check
	@echo "✅ Pipeline complete."

# Run full workflow including install
all: install pipeline
	@echo "✅ All tasks complete."