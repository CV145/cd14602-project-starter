# tasks.md

**Project:** Flashcard CLI Quizzer in Python

**Feature:** Quiz Engine (Strategy and Factory Patterns)

**Version:** 1.0

## Tasks:

- [x] **Task 0:** Write unit tests for `Card` domain model and answer evaluation in `test_quiz_modes.py`.
    - Done Check: Unit tests in `project/main/tests/test_quiz_modes.py` verify that `Card` instantiates with `front` and `back` strings, trims leading/trailing whitespace, and performs case-insensitive answer matching.
- [x] **Task 1:** Implement `Card` domain model in `quiz_engine.py`.
    - Done Check: `Card` class is implemented in `project/main/utils/quiz_engine.py` with `front: str`, `back: str`, and a `check_answer(user_input: str) -> bool` method that passes the Task 0 tests.
- [x] **Task 2:** Write unit tests for `SequentialStrategy` and `RandomStrategy` in `test_quiz_modes.py`.
    - Done Check: Unit tests in `project/main/tests/test_quiz_modes.py` verify that `SequentialStrategy` serves cards in order and wraps around to repeat indefinitely, and `RandomStrategy` serves cards non-deterministically.
- [x] **Task 3:** Implement abstract base class `QuizMode`, `SequentialStrategy`, and `RandomStrategy` in `quiz_engine.py`.
    - Done Check: `QuizMode` ABC with abstract methods `get_next_card()`, `record_attempt()`, and `has_cards()`, along with concrete classes `SequentialStrategy` and `RandomStrategy`, are implemented in `project/main/utils/quiz_engine.py` and pass the Task 2 tests.
- [x] **Task 4:** Write unit tests for `AdaptiveStrategy` spaced repetition queue transitions and time decay in `test_quiz_modes.py`.
    - Done Check: `test_adaptive_mode_behavior` exists in `project/main/tests/test_quiz_modes.py` and verifies priority order (`new` -> `5min` -> `10min` -> `15min`), attempt transitions (easy/0 fails advances to 15min, medium/1 fail moves to 10min, difficult/2 fails stays in 5min), and timestamp decay re-categorization using a mock time provider.
- [x] **Task 5:** Implement `AdaptiveStrategy` in `quiz_engine.py`.
    - Done Check: `AdaptiveStrategy` class is implemented in `project/main/utils/quiz_engine.py` with multi-tier queues, attempt tracking, custom intervals support, and inter-session time decay logic, passing `test_adaptive_mode_behavior`.
- [x] **Task 6:** Write unit tests for `QuizModeFactory` in `test_quiz_modes.py`.
    - Done Check: `test_quiz_mode_factory` exists in `project/main/tests/test_quiz_modes.py` and verifies instantiation via `create_sequential`, `create_random`, `create_adaptive`, camelCase aliases (`createSequential`, `createRandom`, `createAdaptive`), dynamic string selector `create_mode`, and `ValueError` on invalid mode strings.
- [x] **Task 7:** Implement `QuizModeFactory` in `quiz_engine.py`.
    - Done Check: `QuizModeFactory` is implemented in `project/main/utils/quiz_engine.py` with dedicated strategy factory methods, camelCase aliases, and dynamic string dispatch selector, passing `test_quiz_mode_factory`.
- [x] **Task 8:** Write unit tests for `QuizEngine` orchestration, score tracking, and persistent quiz state in `test_quiz_engine.py`.
    - Done Check: Unit tests in `project/main/tests/test_quiz_engine.py` verify card presentation, session correct/incorrect count tracking, auto-initialization of missing `data/quiz_state.json`, and lifetime accuracy percentage calculations (`(total_correct / total_attempts) * 100`).
- [x] **Task 9:** Implement `QuizEngine` in `quiz_engine.py`.
    - Done Check: `QuizEngine` is implemented in `project/main/utils/quiz_engine.py`, accepting cards and a strategy, managing the quiz session, updating `data/quiz_state.json` without crashing on missing files, and passing all Task 8 tests.
- [x] **Task 10:** Verify PEP 8 compliance, line length constraints, and test suite coverage.
    - Done Check: `flake8` returns zero warnings or errors across the new codebase, all functions are <= 40 lines with docstrings and security vulnerability notes, and `pytest` runs with all tests passing and >= 80% code coverage.
