"""
Unit tests for the FileHandler class.

These tests demonstrate file I/O testing patterns and proper
cleanup of test artifacts.
"""

import shutil
import tempfile

import pytest

from utils.file_handler import FileHandler


class TestFileHandler:
    """Test suite for FileHandler functionality."""

    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.file_handler = FileHandler(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir)

    def test_save_data_creates_file(self):
        """Test that save_data creates a file with correct content."""
        data = {"test": "data", "number": 42}
        self.file_handler.save_data("test.json", data)

        assert self.file_handler.file_exists("test.json")
        loaded_data = self.file_handler.load_data("test.json")
        assert loaded_data == data

    def test_load_nonexistent_file_returns_empty_dict(self):
        """Test that loading a non-existent file returns empty dict."""
        result = self.file_handler.load_data("nonexistent.json")
        assert result == {}

    def test_save_invalid_data_raises_error(self):
        """Test that saving invalid JSON data raises RuntimeError."""
        # Create data that can't be serialized to JSON
        invalid_data = {"function": lambda x: x}
        with pytest.raises(RuntimeError, match="Failed to save data"):
            self.file_handler.save_data("invalid.json", invalid_data)

    def test_file_exists(self):
        """Test file existence checking."""
        assert not self.file_handler.file_exists("test.json")
        self.file_handler.save_data("test.json", {"test": "data"})
        assert self.file_handler.file_exists("test.json")

    def test_delete_file(self):
        """Test file deletion."""
        self.file_handler.save_data("test.json", {"test": "data"})
        assert self.file_handler.file_exists("test.json")

        self.file_handler.delete_file("test.json")
        assert not self.file_handler.file_exists("test.json")

    def test_delete_nonexistent_file_no_error(self):
        """Test that deleting non-existent file doesn't raise error."""
        self.file_handler.delete_file("nonexistent.json")  # Should not raise

    def test_list_files(self):
        """Test listing files in data directory."""
        self.file_handler.save_data("file1.json", {"data": 1})
        self.file_handler.save_data("file2.json", {"data": 2})

        files = self.file_handler.list_files()
        assert len(files) == 2
        assert "file1.json" in files
        assert "file2.json" in files


def test_load_valid_flashcards_array(tmp_path):
    """Test loading flashcards from a valid JSON array format."""
    import json

    from utils.file_handler import load_flashcard_data

    # Arrange
    cards_data = [
        {"front": "What is Python?", "back": "A programming language."},
        {"front": "What is PEP 8?", "back": "Python style guide."},
    ]
    file_path = tmp_path / "valid_array.json"
    file_path.write_text(json.dumps(cards_data), encoding="utf-8")

    # Act
    loaded_cards = load_flashcard_data(file_path)

    # Assert
    assert loaded_cards == cards_data
    assert len(loaded_cards) == 2
    assert loaded_cards[0]["front"] == "What is Python?"

    # Security Vulnerabilities: None.


def test_load_valid_flashcards_object(tmp_path):
    """Test loading flashcards from a valid JSON object with cards array."""
    import json

    from utils.file_handler import load_flashcard_data

    # Arrange
    cards_data = [
        {"front": "What is Python?", "back": "A programming language."}
    ]
    data = {"cards": cards_data}
    file_path = tmp_path / "valid_object.json"
    file_path.write_text(json.dumps(data), encoding="utf-8")

    # Act
    loaded_cards = load_flashcard_data(file_path)

    # Assert
    assert loaded_cards == cards_data
    assert len(loaded_cards) == 1
    assert loaded_cards[0]["front"] == "What is Python?"

    # Security Vulnerabilities: None.


def test_load_invalid_json(tmp_path):
    """Test loading flashcards from a file with invalid JSON syntax."""
    import pytest

    from utils.file_handler import load_flashcard_data

    # Arrange
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{malformed_json: true", encoding="utf-8")

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_flashcard_data(file_path)

    # Security Vulnerabilities: None.


def test_load_missing_required_field(tmp_path):
    """Test that loading cards missing required fields raises ValueError."""
    import json

    import pytest

    from utils.file_handler import load_flashcard_data

    # Arrange
    invalid_cards = [{"front": "What is Python?"}]
    file_path = tmp_path / "missing_back.json"
    file_path.write_text(json.dumps(invalid_cards), encoding="utf-8")

    # Act & Assert
    with pytest.raises(ValueError, match="Missing required field 'back'"):
        load_flashcard_data(file_path)

    # Security Vulnerabilities: None.


def test_load_non_string_field(tmp_path):
    """Test that cards with non-string field values raise ValueError."""
    import json

    import pytest

    from utils.file_handler import load_flashcard_data

    # Arrange
    invalid_cards = [{"front": 123, "back": "A number."}]
    file_path = tmp_path / "non_string_field.json"
    file_path.write_text(json.dumps(invalid_cards), encoding="utf-8")

    # Act & Assert
    with pytest.raises(ValueError, match="must be a string"):
        load_flashcard_data(file_path)

    # Security Vulnerabilities: None.
