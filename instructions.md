Udacity part of Accenture logo

Instructions

Project Starter Github Repository
(opens in a new tab)https://github.com/udacity/cd14602-project-starter/tree/main/project(opens in a new tab)

Building the Flashcard Quizzer CLI Application

1. Project Structure
   You have been provided with a project repository containing the following skeleton. Do not delete the folder structure, as your AI agent needs this organization to separate concerns effectively.

main.py: Currently empty. This will be your entry point.
data/: Place your sample JSON files here.
utils/: For helper modules (you will generate file_handler.py here).
tests/: Currently empty. You will direct the AI to fill this with pytest cases.
docs/: Contains templates for your "AI Interaction Log." You must update this log as you work.
.claude/ or .env: Configuration files for your AI tools. 2. Implementation Milestones
You must guide your AI agent through these distinct development phases.

Phase 1: Data Layer & Validation
Create a system to load and validate flashcard data.

Requirement: The app must support JSON input in two formats:
Array Format: A simple list of objects [{"front": "...", "back": "..."}].
Object Format: A wrapper object {"cards": [...]}.
Error Handling: If the JSON is malformed or missing fields, the app must catch the error and print a friendly message (no raw Python tracebacks).

Phase 2: Core Logic & Design Patterns
Objective: Implement the quiz engine using the Strategy Pattern.

The Logic: You need three distinct ways to serve questions:
SequentialMode: Order 1, 2, 3...
RandomMode: Shuffled order.
AdaptiveMode: Prioritize cards the user gets wrong.
Implement a QuizMode abstract base class. Then create three classes that inherit from it. Use a Factory Pattern to select the correct mode based on user input."

Phase 3: The CLI & Interaction
Finally, build the user interface.

Requirements:
Use argparse to handle flags like -f (file), -m (mode), and --stats.
Display text colors (Green for correct, Red for incorrect).
Allow the user to type "exit" or press Ctrl+C to quit gracefully without errors.

 3. Testing Requirements
You are responsible for the quality of the AI's code. You must direct the AI to write a comprehensive test suite. Your final submission must pass the following test scenarios:

A. Data Loader Tests (test_flashcard_loader.py)

test_load_valid_flashcards_array: Does it load a list correctly?
test_load_invalid_json: Does it gracefully handle bad syntax?
test_load_missing_required_field: Does it reject cards without a "Back"?
B. Quiz Logic Tests (test_quiz_modes.py)

test_quiz_mode_factory: Does the factory return the correct class object?
test_adaptive_mode_behavior: Does it actually repeat incorrect questions?
C. Integration Tests (test_integration.py)

test_full_session: Simulate a user answering 3 questions and checking the final stats calculation.
How to verify: Run the full suite in your terminal:

python -m pytest tests/
Run the full suite in your terminal for report:

python -m pytest --cov=. --cov-report=html
Target: >80% code coverage.

4. Definition of Done
   Your project is complete when:

You can run python main.py -m adaptive -f data/python_basics.json and play a full game.
The code uses the Strategy and Factory patterns (checked by inspecting quiz_engine.py).
All tests pass, and flake8 reports no linting errors.
Your docs/ai_edit_log.md contains at least 5 examples of prompts you improved or logic you corrected. 5. Submission Checklist
Submit your GitHub repository link containing:

Complete codebase with all source files, tests, and documentation
Completed ai_edit_log.md with at least 5 detailed AI interaction examples
Final project report using the provided template (1000-1500 words)
Updated README.md with current setup instructions and feature descriptions
Test coverage report demonstrating >80% coverage
Code quality verification (all linting tools should pass without errors)
Tip: If the AI gets stuck or writes bad code, do not rewrite the Python yourself. Rewrite your prompt.

Flashcard Quizzer: AI-Assisted CLI Learning Application - Instructions
