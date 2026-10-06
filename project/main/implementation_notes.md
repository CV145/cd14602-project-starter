# Implementation Notes

### [2026-10-05] Task 0: Unit tests for load_flashcard_data
- Decision: Implemented tests in `tests/test_file_handler.py` using pytest `tmp_path` fixture to ensure isolated file environments without test artifacts.
- Assumption: `load_flashcard_data` will raise `ValueError` with informative messages when encountering malformed JSON syntax, missing keys, or non-string values.

### [2026-10-05] Task 1: Implement load_flashcard_data function in file_handler.py
- Decision: Implemented `load_flashcard_data` as a module-level function taking `Path | str` and returning `list[dict[str, Any]]` to support both array and object formats.
- Notes: Basic JSON reading and structure branching works; detailed field and type validation are partitioned into Tasks 3, 5, and 6.

### [2026-10-05] Tasks 2-8: JSON Parsing, Validation, Normalization, and Error Handling
- Decision: Refactored `load_flashcard_data` into a compact 35-line implementation adhering to the <=40 lines constraint while upholding all validation rules.
- Notes: Normalization unifies array format `[...]` and object format `{"cards": [...]}` into a uniform `list[dict[str, str]]`, rejecting empty strings, non-string types, and missing fields with clear `ValueError` messages.

### [2026-10-06] Quiz Engine Tasks 0-10: Strategy & Factory Implementation
- Decision: Implemented `Card`, `QuizMode` ABC, `SequentialStrategy`, `RandomStrategy`, `AdaptiveStrategy`, `QuizModeFactory`, and `QuizEngine` in `quiz_engine.py` using strict TDD, keeping every function under 40 lines.
- Notes: Injected mockable `time_provider` for deterministic spaced repetition testing, supported both snake_case and camelCase factory aliases, achieved 87% test coverage, and documented edge cases and security vulnerabilities per method.
