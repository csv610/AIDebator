.PHONY: help install dev test lint format clean run-cli run-web run-api docs

BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

help:
	@echo "$(BLUE)AI Debate Platform - Available Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@echo "  make install          Install project (editable)"
	@echo "  make dev              Install with dev extras"
	@echo ""
	@echo "$(GREEN)Running:$(NC)"
	@echo "  make run-cli          Run CLI interface"
	@echo "  make run-web          Run Streamlit web UI"
	@echo "  make run-api          Run Python API example"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make test             Run tests"
	@echo "  make lint             Check code with ruff"
	@echo "  make format           Format code with black"
	@echo "  make clean            Remove generated files"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  make docs             List documentation files"
	@echo ""

install:
	@echo "$(BLUE)Installing project in editable mode...$(NC)"
	pip install -e .
	@echo "$(GREEN)✓ Installed$(NC)"

dev:
	@echo "$(BLUE)Installing with dev extras...$(NC)"
	pip install -e ".[dev]"
	@echo "$(GREEN)✓ Dev install complete$(NC)"

run-cli:
	@echo "$(BLUE)AI Debate Platform - CLI Mode$(NC)"
	@echo ""
	@echo "Usage examples:"
	@echo "  aidebator --topic \"AI will improve employment\" --rounds 3"
	@echo "  aidebator --config debate_config.json"
	@echo ""
	aidebator --help

run-web:
	@echo "$(BLUE)Starting Streamlit web UI...$(NC)"
	@echo "Opening http://localhost:8501"
	streamlit run debate_sl.py

run-api:
	@echo "$(BLUE)AI Debate Platform - Python API Example$(NC)"
	@python3 -c "from src.debate import DebateConfig, DebateSession; \
	config = DebateConfig( \
	    topic='AI will improve employment', \
	    organizer_model='gpt-4', \
	    supporter_model='gpt-4', \
	    opposer_model='gpt-4', \
	    judge_model='gpt-4', \
	    num_rounds=1 \
	); \
	print('Config created successfully!'); \
	print(f'Topic: {config.topic}'); \
	print(f'Rounds: {config.num_rounds}')"

test:
	@echo "$(BLUE)Running tests...$(NC)"
	@if [ -f "./debatenv/bin/pytest" ]; then \
		./debatenv/bin/pytest tests/ -v --cov=src; \
	else \
		python3 -m pytest tests/ -v --cov=src; \
	fi
	@echo "$(GREEN)✓ Tests complete$(NC)"

lint:
	@echo "$(BLUE)Running ruff...$(NC)"
	ruff check debate_cli.py debate_sl.py src/debate/
	@echo "$(GREEN)✓ Lint check complete$(NC)"

format:
	@echo "$(BLUE)Formatting with black...$(NC)"
	black debate_cli.py debate_sl.py src/debate/ --line-length 100
	@echo "$(GREEN)✓ Format complete$(NC)"

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf build/ dist/
	rm -f debate_result*.json
	@echo "$(GREEN)✓ Clean complete$(NC)"

docs:
	@echo "$(BLUE)Documentation:$(NC)"
	@ls -1 docs/ | sed 's/^/  /'
	@echo ""
	@command -v open >/dev/null 2>&1 && open README.md || less README.md

.DEFAULT_GOAL := help
