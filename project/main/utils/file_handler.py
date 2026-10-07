"""
File handling utility for data persistence.

This module demonstrates file I/O operations and error handling
patterns that students can learn from and extend.
"""

import json
from pathlib import Path
from typing import Any, Dict


class FileHandler:
    """Handle file operations for data persistence."""

    def __init__(self, data_dir: str = "data"):
        """Initialize FileHandler with target data directory."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Edge Cases: Creates data directory if it does not exist.
        # Security Vulnerabilities: None.

    def save_data(self, filename: str, data: Dict[str, Any]) -> None:
        """Save data to a JSON file."""
        filepath = self.data_dir / filename
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except (IOError, TypeError) as e:
            raise RuntimeError(f"Failed to save data to {filename}: {e}")

    def load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from a JSON file."""
        filepath = self.data_dir / filename
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except (IOError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load data from {filename}: {e}")

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in the data directory."""
        return (self.data_dir / filename).exists()

    def delete_file(self, filename: str) -> None:
        """Delete a file from the data directory."""
        filepath = self.data_dir / filename
        if filepath.exists():
            filepath.unlink()

    def list_files(self) -> list[str]:
        """List all files in the data directory."""
        return [f.name for f in self.data_dir.iterdir() if f.is_file()]


def load_flashcard_data(file_path: Path | str) -> list[dict[str, str]]:
    """Load and validate flashcard data from a JSON file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Flashcard file not found: {file_path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON format: {exc}") from exc

    raw_cards = (
        data
        if isinstance(data, list)
        else (data.get("cards") if isinstance(data, dict) else None)
    )
    if not isinstance(raw_cards, list):
        raise ValueError("Invalid JSON: expected list or 'cards' array")

    validated: list[dict[str, str]] = []
    for index, card in enumerate(raw_cards):
        if not isinstance(card, dict):
            raise ValueError(f"Card at index {index} must be a dictionary")
        for field in ("front", "back"):
            if field not in card:
                raise ValueError(f"Missing required field '{field}'")
            if not isinstance(card[field], str):
                raise ValueError(f"Field '{field}' must be a string")
            if not card[field].strip():
                raise ValueError(f"Field '{field}' cannot be empty")
        validated.append({"front": card["front"], "back": card["back"]})
    return validated

    # Security Vulnerabilities:
    # 1. Path traversal: arbitrary file paths read without sandboxing.
    # 2. DoS: large JSON files could cause high memory consumption.
