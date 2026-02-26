.PHONY: help install dev test lint format clean run-cli run-web run-api docs

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)AI Debate Platform - Available Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@echo "  make install          Install dependencies"
	@echo "  make dev              Install dependencies + dev tools"
	@echo ""
	@echo "$(GREEN)Running the Platform:$(NC)"
	@echo "  make run-web          Run Streamlit web UI"
	@echo "  make run-cli          Run CLI interface"
	@echo "  make run-api          Run Python API example"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make test             Run tests (placeholder)"
	@echo "  make lint             Check code with pylint"
	@echo "  make format           Format code with black"
	@echo "  make clean            Remove generated files"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  make docs             Open documentation"
	@echo ""
	@echo "$(GREEN)Git:$(NC)"
	@echo "  make commit-all       Stage and commit all changes"
	@echo "  make push             Push to remote repository"
	@echo ""

install:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev:
	@echo "$(BLUE)Installing dependencies + dev tools...$(NC)"
	pip install -r requirements.txt
	pip install black pylint pytest pytest-cov
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

run-web:
	@echo "$(BLUE)Starting Streamlit web UI...$(NC)"
	@echo "Opening http://localhost:8501"
	streamlit run app.py

run-cli:
	@echo "$(BLUE)AI Debate Platform - CLI Mode$(NC)"
	@echo ""
	@echo "Usage examples:"
	@echo "  python debate_cli.py --topic \"AI will improve employment\" --rounds 3"
	@echo "  python debate_cli.py --config debate_config.json"
	@echo ""
	python debate_cli.py --help

run-api:
	@echo "$(BLUE)AI Debate Platform - Python API Example$(NC)"
	@echo ""
	python -c "from src.debate import DebateConfig, DebateSession; \
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
	@echo "$(YELLOW)Note: Test suite not yet implemented$(NC)"
	@echo "Run: pytest tests/"
	@echo ""

lint:
	@echo "$(BLUE)Running pylint...$(NC)"
	-pylint app.py debate_cli.py src/debate/
	@echo "$(GREEN)✓ Lint check complete$(NC)"

format:
	@echo "$(BLUE)Formatting code with black...$(NC)"
	black app.py debate_cli.py src/debate/ --line-length 100
	@echo "$(GREEN)✓ Code formatted$(NC)"

clean:
	@echo "$(BLUE)Cleaning up generated files...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	rm -rf build/ dist/ *.egg-info
	rm -f debate_result*.json
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

docs:
	@echo "$(BLUE)Documentation Files:$(NC)"
	@echo ""
	@ls -1 docs/ | sed 's/^/  /'
	@echo ""
	@echo "$(YELLOW)Opening README...$(NC)"
	@command -v open >/dev/null 2>&1 && open README.md || less README.md

commit-all:
	@echo "$(BLUE)Staging and committing all changes...$(NC)"
	git add -A
	@if git diff --cached --quiet; then \
		echo "$(YELLOW)No changes to commit$(NC)"; \
	else \
		git commit -m "Updated via make commit-all"; \
		echo "$(GREEN)✓ Changes committed$(NC)"; \
	fi

push:
	@echo "$(BLUE)Pushing to remote...$(NC)"
	git push origin main
	@echo "$(GREEN)✓ Pushed to origin/main$(NC)"

.DEFAULT_GOAL := help

