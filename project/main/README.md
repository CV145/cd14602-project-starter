# AI-Assisted Development Project Starter

This is a Python project template for learning AI-assisted software development. You will build upon this foundation to create a functional application while collaborating with AI coding assistants to apply software engineering best practices including design patterns, separation of concerns, test-driven development, and comprehensive documentation.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application (CLI):**
   ```bash
   python main.py -f data/sample_deck.json -m sequential
   ```

4. **Launch Streamlit Web App:**
   ```bash
   streamlit run streamlit_frontend.py
   ```

5. **Run tests:**
   ```bash
   python -m pytest
   ```

## 🎮 Flashcard Quizzer Interfaces

### CLI Usage (`cli_frontend.py` & `main.py`)

Run the CLI using `python main.py`:

```bash
python main.py [FLAGS]
```

#### Flags
- `-f, --file PATH`: Optional. Path to flashcard deck JSON (≤ 1 MB). If omitted, automatically selects the latest non-upload deck studied from `data/quiz_state.json`.
- `-m, --mode {sequential,random,adaptive}`: Quiz progression strategy (case-insensitive, defaults to `sequential`).
  - `sequential`: Cycles through deck in order.
  - `random`: Random selection without replacement.
  - `adaptive`: Spaced Repetition Algorithm (SRA) with 2 attempts per card and priority queues (new → 5min → 10min → 15min).
- `--stats`: Displays cross-deck lifetime accuracy and attempt totals in a formatted table and exits with code `0`.
- `--state PATH`: Path to persistent state file (defaults to `data/quiz_state.json`).

#### In-Quiz Commands & Interaction
- Type your answer and press **Enter** (case-insensitive match).
- `skip`: Skips current card, reveals answer, and records 1 incorrect (routes to 5min Difficult queue in adaptive mode).
- `exit` or **Ctrl+C** / **Ctrl+D**: Prompts confirmation `Quit? (y/n)`. Confirmed quit displays end-of-session summary and exits cleanly with code `0`.
- Collisions: If a card's answer is literally `exit` or `skip`, it is graded first and confirmation is prompted before recording.
- Exit Codes: `0` on success or clean quit; `1` on all errors (single-line friendly message with no tracebacks).

### Streamlit Web App (`streamlit_frontend.py`)

Launch the local web dashboard:

```bash
streamlit run streamlit_frontend.py
```

Features:
- Deck dropdown automatically populated from `data/*.json` (excluding state file).
- File uploader for custom decks (`upload:<name>` namespace).
- Interactive card view with instant feedback (`st.success` / `st.error`).
- Adaptive queue counts, customizable review intervals, and deck progress reset.
- Automatic session resumption prompt after page refresh.

### ⚠️ Concurrency Constraint

The application operates in a **single-user, single-active-process** model:
- Only one front-end (CLI or Streamlit) should run at a time against `quiz_state.json`.
- Running multiple instances or opening multiple concurrent browser tabs simultaneously is unsupported (last writer wins) as the system deliberately avoids distributed file locking complexities.

### 🛠️ Development Tools

#### Code Quality Tools

- **Black**: Code formatter
  ```bash
  black .
  ```

- **isort**: Import organizer
  ```bash
  isort .
  ```

- **flake8**: Linting
  ```bash
  flake8 .
  ```

- **mypy**: Type checking
  ```bash
  mypy .
  ```

- **pytest**: Testing framework
  ```bash
  python -m pytest --cov=. --cov-report=html
  ```

#### Pre-commit Hooks (Optional)

Set up pre-commit hooks for automatic code quality checks:

```bash
pre-commit install
```

## Testing

The project includes comprehensive unit tests demonstrating proper testing practices for AI-assisted development.

### Tests Break Down

The test suite contains 95 tests across 8 modules achieving 95% total code coverage:

- **Quiz Modes (`test_quiz_modes.py`)**: Tests Strategy pattern implementations (`SequentialStrategy`, `RandomStrategy`, `AdaptiveStrategy`), Spaced Repetition queue routing, priority serving (new → 5min → 10min → 15min), and time decay.
- **Quiz Engine (`test_quiz_engine.py`)**: Tests engine orchestration, session scoring, corrupted state JSON detection (`StateFileError`), and atomic state file persistence.
- **Session Controller (`test_session_controller.py`)**: Tests the Facade pattern managing user turn processing, adaptive retry loops, command vs answer collision disambiguation, and session recovery.
- **CLI Frontend (`test_cli_frontend.py`)**: Validates argument parsing, exit codes (code 1 on error, code 0 on quit), formatted Rich tables, and interactive quit confirmation.
- **Streamlit Frontend (`test_streamlit_frontend.py`)**: Headless UI testing using Streamlit's `AppTest` framework covering session initialization, card advancement, feedback persistence, and deck resets.
- **Integration Tests (`test_integration.py`)**: Full end-to-end integration flows through the flashcard lifecycle.
- **File Handler (`test_file_handler.py`)**: Tests data validation, schema normalization, path traversal guards, and file size limits.
- **TaskManager (`test_task_manager.py`)**: Verifies legacy starter CRUD task operations.

```bash
# Run all tests
pytest

# Run with coverage report (aim for >80% coverage)
python -m pytest --cov=. --cov-report=html

# Run specific test file with verbose output
python -m pytest tests/test_task_manager.py -v

# Run all quality checks
black . && isort . && flake8 . && mypy . && pytest
```

## Project Instructions

This section contains all the student deliverables for this project.

### Learning Objectives
- **AI Collaboration**: Learn to effectively work with AI assistants to generate, review, and refactor code while maintaining code quality
- **Software Engineering**: Apply design patterns, separation of concerns, and modular architecture
- **Test-Driven Development**: Write and maintain comprehensive unit tests with good coverage
- **Code Quality**: Use linting, formatting, and type checking tools for professional-grade code
- **Documentation**: Document AI interactions and development decisions throughout the process

### AI-Assisted Development Workflow

#### 1. Planning Phase
- Use AI to help break down requirements into smaller, manageable tasks
- Ask for architectural suggestions and design pattern recommendations
- Review the `/ai_guidance/prompting_best_practices.md` for effective prompting techniques
- Use the provided slash commands in `/.claude/commands/` for common tasks

#### 2. Implementation Phase
- Generate initial code with AI assistance using specific, contextual prompts
- Always review and understand AI-generated code before accepting it
- Test AI-generated code thoroughly with various inputs and edge cases
- Refactor for clarity, maintainability, and adherence to project standards

#### 3. Review Phase
- Use AI to help identify potential issues or improvements
- Follow the `/ai_guidance/code_review_checklist.md` for systematic code review
- Ask for code review suggestions and alternative implementations
- Validate that the code follows project conventions and security best practices

#### 4. Documentation Phase
- Document your AI interactions in `/docs/ai_edit_log.md` with specific examples
- Explain your decisions and modifications to AI suggestions
- Complete the final report using `/docs/report_template.md`
- Update this README with new features and learnings

### Assessment Criteria

Your project will be evaluated on:

1. **Functionality**: Does the application work as intended with proper error handling?
2. **Code Quality**: Is the code well-structured, readable, and maintainable?
3. **Testing**: Are there comprehensive unit tests with good coverage (>80%)?
4. **AI Collaboration**: Did you effectively use AI assistance while maintaining code quality?
5. **Documentation**: Are your AI interactions and decisions well-documented?

### Example AI Prompts

- "Help me implement a priority queue for tasks using the strategy pattern"
- "Review this code for potential security vulnerabilities"
- "Suggest improvements to make this code more maintainable"
- "Help me write comprehensive unit tests for this function"

### AI Guidance Resources

- `/ai_guidance/prompting_best_practices.md` - Learn effective AI prompting techniques
- `/ai_guidance/code_review_checklist.md` - Systematic approach to reviewing AI-generated code
- `/.claude/commands/generate-function` - Generate well-structured Python functions
- `/.claude/commands/review-code` - Get comprehensive code reviews
- `/.claude/commands/debug-help` - Debug issues with AI assistance
- `/.claude/commands/refactor-code` - Refactor code with design patterns
- `/docs/design_patterns.md` - Examples of implementing design patterns with AI assistance

### Project Structure

```
project/main/
├── main.py                     # CLI entry point wrapper
├── cli_frontend.py             # Rich terminal CLI frontend
├── streamlit_frontend.py       # Streamlit web frontend
├── utils/                      # Core business logic & architecture
│   ├── __init__.py
│   ├── quiz_engine.py          # Strategy & Factory patterns (SRA queues, cards)
│   ├── session_controller.py   # Facade pattern (turn processing, state tracking)
│   ├── file_handler.py         # File loading, validation, and JSON I/O
│   └── task_manager.py         # Starter CRUD task utility
├── tests/                      # Comprehensive 95-test unit & integration suite
│   ├── __init__.py
│   ├── test_quiz_modes.py      # Strategy pattern tests
│   ├── test_quiz_engine.py     # Engine scoring & persistence tests
│   ├── test_session_controller.py # Facade controller turn tests
│   ├── test_cli_frontend.py    # CLI interaction & argument tests
│   ├── test_streamlit_frontend.py # Streamlit AppTest headless tests
│   ├── test_integration.py     # End-to-end integration flows
│   ├── test_file_handler.py    # Data validation tests
│   └── test_task_manager.py    # Task CRUD tests
├── data/                       # Bundled flashcard decks & state
│   ├── python_basics.json
│   ├── git_and_github.json
│   ├── sample_deck.json
│   └── quiz_state.json         # Persistent user progress & review timestamps
├── docs/                       # Project specifications & documentation
│   ├── ai_edit_log.md          # AI interaction tracking log
│   ├── design_patterns.md      # Design pattern documentation
│   ├── report_template.md      # Final project report template
│   └── specs/                  # Feature specifications and task breakdowns
├── ai_guidance/                # Prompting practices and review checklists
├── requirements.txt            # Project dependencies
└── README.md                  # Project overview & documentation
```

## Built With

* [Python](https://www.python.org/) - Core programming language
* [pytest](https://docs.pytest.org/) - Testing framework for comprehensive unit tests
* [pytest-cov](https://pytest-cov.readthedocs.io/) - Coverage reporting for tests
* [Black](https://black.readthedocs.io/) - Code formatter for consistent style
* [isort](https://pycqa.github.io/isort/) - Import organizer for clean code structure
* [flake8](https://flake8.pycqa.org/) - Linting tool for code quality
* [mypy](https://mypy.readthedocs.io/) - Static type checker for better code reliability
* [pre-commit](https://pre-commit.com/) - Git hook framework for automated quality checks
* [Claude](https://claude.ai/) - AI assistant for code generation and review

## License

[License](LICENSE.txt)

---

**Remember**: The goal is not just to build a working application, but to learn how to effectively collaborate with AI while maintaining high software engineering standards. Take time to understand the code, ask questions, and document your learning journey!
