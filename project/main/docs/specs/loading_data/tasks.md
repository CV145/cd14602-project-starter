# tasks.md

**Project:** Flashcard CLI Quizzer in Python

**Feature:** Flashcard Data Loading and Validation

**Version:** 1.0

## Tasks:

- [x] **Task 0:** Write unit tests for `load_flashcard_data` in `file_handler.py`.
    - Done Check: Unit tests cover valid JSON arrays, valid JSON objects with cards arrays, invalid JSON formats, missing fields, and non-string values.
- [x] **Task 1:** Implement `load_flashcard_data` function in `file_handler.py`.
    - Done Check: The `load_flashcard_data` function exists in `file_handler.py` and can read a JSON file, return a list of flashcard dictionaries, and handle basic errors.
- [x] **Task 2:** Implement JSON reading using the `json` module in `file_handler.py`.
    - Done Check: The `load_flashcard_data` function uses the `json` module to parse the input file content.
- [x] **Task 3:** Implement basic JSON validation in `file_handler.py`.
    - Done Check: The `load_flashcard_data` function checks if the JSON is valid and that each card object has "front" and "back" keys with non-empty string values.
- [x] **Task 4:** Implement error handling for invalid JSON format in `file_handler.py`.
    - Done Check: The `load_flashcard_data` function catches and handles errors related to invalid JSON format.
- [x] **Task 5:** Implement error handling for missing fields in flashcard objects in `file_handler.py`.
    - Done Check: The `load_flashcard_data` function catches and handles errors related to missing "front" or "back" keys in flashcard objects.
- [x] **Task 6:** Implement error handling for non-string values in flashcard fields in `file_handler.py`.
    - Done Check: The `load_flashcard_data` function catches and handles errors related to non-string values in "front" or "back" fields.
- [x] **Task 7:** Normalize JSON data to a consistent list of flashcard dictionaries in `file_handler.py`.
    - Done Check: The `load_flashcard_data` function normalizes JSON data to return a consistent list of flashcard dictionaries, regardless of input format (array or object).
- [x] **Task 8:** Add comprehensive error handling and informative messages to `file_handler.py`.
    - Done Check: The `load_flashcard_data` function includes detailed error handling and provides informative messages to the user/developer when validation fails.
