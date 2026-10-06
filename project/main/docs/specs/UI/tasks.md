# tasks.md

**Project:** Flashcard CLI Quizzer in Python

**Feature:** Dual User Interface (CLI & Streamlit) and Session Controller Facade

**Version:** 1.0

## Tasks:

- [x] **Task 0:** Add `rich` and `streamlit` to dependencies in `requirements.txt`.
    - Done Check: `rich` and `streamlit` are listed in `project/main/requirements.txt` and installable via `pip install -r project/main/requirements.txt`.
- [x] **Task 1:** Write unit tests for `StateFileError`, two-phase grading (`grade_current_card`, `record_result`), and `OSError` propagation in `test_quiz_engine.py`.
    - Done Check: Unit tests in `project/main/tests/test_quiz_engine.py` verify that `StateFileError` captures file path, line number, and column number on invalid JSON; `grade_current_card` evaluates user input without advancing cards or mutating metrics; `record_result` updates metrics, records timestamps, and advances cards; `answer_current_card` preserves single-attempt functionality; and `_save_state` propagates `OSError`.
- [x] **Task 2:** Implement `StateFileError`, two-phase grading, and `OSError` propagation in `quiz_engine.py`.
    - Done Check: `StateFileError` exception is defined in `project/main/utils/quiz_engine.py`, `_init_state` raises `StateFileError` on `json.JSONDecodeError`, `grade_current_card` and `record_result` are implemented in `QuizEngine`, `_save_state` raises/propagates `OSError`, and all Task 1 tests pass.
- [x] **Task 3:** Write unit tests for `AdaptiveStrategy` explicit fail counts, due-time filtering, `seconds_until_next_due`, and queue serialization in `test_quiz_engine.py`.
    - Done Check: Unit tests in `project/main/tests/test_quiz_engine.py` verify that `record_attempt(card, fails)` routes fail counts (0 -> 15min, 1 -> 10min, 2 -> 5min), `get_next_card()` filters cards by elapsed interval against `last_seen`, `seconds_until_next_due()` returns remaining seconds or `None`, and `to_dict()` / `from_dict()` roundtrips queues and timestamps.
- [x] **Task 4:** Implement `AdaptiveStrategy` explicit fail counts, due-time filtering, and serialization in `quiz_engine.py`.
    - Done Check: `AdaptiveStrategy` in `project/main/utils/quiz_engine.py` accepts explicit fail count parameters, returns only due cards in `get_next_card()`, implements `seconds_until_next_due()`, and implements `to_dict()` and `from_dict()`, passing all Task 3 tests.
- [x] **Task 5:** Write unit tests for reserved key filtering and all-decks lifetime stats in `test_quiz_engine.py`.
    - Done Check: Unit tests in `project/main/tests/test_quiz_engine.py` verify that deck stats calculations ignore `_active_session` and `_settings` keys, and `get_all_decks_stats()` computes total correct, total attempts, and lifetime accuracy across standard and `upload:` decks.
- [x] **Task 6:** Implement reserved key filtering and `get_all_decks_stats()` in `quiz_engine.py`.
    - Done Check: `QuizEngine` in `project/main/utils/quiz_engine.py` ignores reserved keys in stats reporting and provides `get_all_decks_stats()`, passing all Task 5 tests.
- [x] **Task 7:** Write unit tests for deck validation, deck loading, and latest deck discovery in `test_session_controller.py`.
    - Done Check: Unit tests in `project/main/tests/test_session_controller.py` verify rejection of missing files, non-`.json` files, files > 1 MB, empty decks (`[]`), and card fronts named `_settings`; verification of duplicate front warnings; and latest deck lookup selecting the non-upload deck with the greatest `last_seen` timestamp (or `None` with no history).
- [x] **Task 8:** Implement deck validation, loading, and latest deck lookup in `session_controller.py`.
    - Done Check: `SessionController` is created in `project/main/utils/session_controller.py` implementing deck path validation, data loading, error reporting, and latest deck resolution, passing all Task 7 tests.
- [x] **Task 9:** Write unit tests for command parsing, collision handling, and adaptive 2-attempt flow in `test_session_controller.py`.
    - Done Check: Unit tests in `project/main/tests/test_session_controller.py` verify whitespace trimming, case-insensitive `exit` and `skip` commands, empty input rejection, 2-attempt progression in adaptive mode (first miss retry, second miss resolution), `skip` recorded as 1 incorrect / fail count 2, and literal `exit`/`skip` card answers graded before prompting confirmation.
- [x] **Task 10:** Implement command parsing, collision handling, and attempt progression in `session_controller.py`.
    - Done Check: `SessionController` in `project/main/utils/session_controller.py` implements input evaluation, command/answer collision resolution, and attempt progression state machine, passing all Task 9 tests.
- [x] **Task 11:** Write unit tests for `_active_session` persistence, session resumption, custom intervals, and progress reset in `test_session_controller.py`.
    - Done Check: Unit tests in `project/main/tests/test_session_controller.py` verify writing `_active_session` to state after recorded outcomes, resuming sessions for sequential, random, adaptive, and uploaded decks, discarding corrupt or missing sessions, updating `<deck>._settings.intervals`, and resetting deck progress while preserving `_settings`.
- [x] **Task 12:** Implement active session persistence, resumption, interval settings, and progress reset in `session_controller.py`.
    - Done Check: `SessionController` in `project/main/utils/session_controller.py` implements `_active_session` persistence and restoration, interval configuration management, and deck progress reset, passing all Task 11 tests.
- [x] **Task 13:** Write unit tests for CLI argument parsing, custom error exits, `--stats` formatting, signal handling, and summary output in `test_cli_frontend.py`.
    - Done Check: Unit tests in `project/main/tests/test_cli_frontend.py` verify CLI flags (`-f`, `-m`, `--stats`, `--state`), friendly red error messages with exit code 1 (including argument parsing failures and corrupt state files), `--stats` table output with exit code 0, handling of `KeyboardInterrupt` and `EOFError` with `Quit? (y/n)`, and summary statistics reporting.
- [x] **Task 14:** Implement CLI interface in `cli_frontend.py` and update `main.py` entry point.
    - Done Check: `project/main/cli_frontend.py` is implemented using `rich` and `SessionController`, `project/main/main.py` routes arguments via `sys.exit(cli_frontend.main(sys.argv[1:]))`, and all Task 13 tests pass.
- [x] **Task 15:** Implement end-to-end integration test `test_full_session` in `test_integration.py`.
    - Done Check: `test_full_session` in `project/main/tests/test_integration.py` executes `cli_frontend.main` on a temporary 3-card deck with scripted inputs (correct, incorrect, correct, `exit`, `y`), verifying exit code 0, summary output displaying 2 correct / 1 incorrect / 66.7%, and matching card stats in the state file.
- [x] **Task 16:** Write UI tests for Streamlit interface in `test_streamlit_frontend.py`.
    - Done Check: Automated tests in `project/main/tests/test_streamlit_frontend.py` using `streamlit.testing.v1.AppTest` verify deck list dropdown population (excluding state file), flashcard question/answer submission, feedback banners (`st.success`/`st.error`), adaptive retry flow, custom file upload under `upload:<name>`, session resume prompts, interval configuration, and deck progress reset.
- [x] **Task 17:** Implement Streamlit web application in `streamlit_frontend.py`.
    - Done Check: `project/main/streamlit_frontend.py` is implemented using `SessionController` and Streamlit widgets with runtime state managed in `st.session_state`, passing all Task 16 tests.
- [x] **Task 18:** Update project documentation in `README.md`.
    - Done Check: `project/main/README.md` documents CLI flags and usage, the Streamlit launch command (`streamlit run streamlit_frontend.py`), and the single-active-process concurrency constraint.
- [x] **Task 19:** Verify PEP 8 compliance, line length constraints, and test suite coverage.
    - Done Check: `flake8` returns zero warnings or errors across the entire codebase, all functions are <= 40 lines with docstrings and edge case/security vulnerability comments, and `pytest --cov=. --cov-report=html` runs with 100% test pass rate and > 80% coverage.
