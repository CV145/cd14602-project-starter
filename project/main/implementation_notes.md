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
