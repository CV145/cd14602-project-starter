"""Unit tests for CLI frontend presentation, arguments, and signal handling."""

import json
from unittest.mock import patch

import cli_frontend


def test_cli_invalid_argument_exits_1(capsys):
    """Test unknown CLI flags print friendly message and exit code 1."""
    # Arrange
    args = ["--invalid-flag-1234"]

    # Act
    code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 1
    assert "error" in (captured.out + captured.err).lower()
    assert "Traceback" not in (captured.out + captured.err)

    # Edge Cases: Overrides default argparse exit code 2 to code 1.
    # Security Vulnerabilities: None.


def test_cli_invalid_mode_exits_1(tmp_path, capsys):
    """Test invalid quiz mode flag exits with code 1."""
    # Arrange
    deck = tmp_path / "deck.json"
    deck.write_text('[{"front": "F", "back": "B"}]', encoding="utf-8")
    args = ["-f", str(deck), "-m", "unsupported_mode"]

    # Act
    code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 1
    assert "unsupported_mode" in (captured.out + captured.err)

    # Edge Cases: Case-insensitive mode validation.
    # Security Vulnerabilities: None.


def test_cli_missing_deck_file_exits_1(tmp_path, capsys):
    """Test missing deck file prints single-line error and exits 1."""
    # Arrange
    missing_deck = tmp_path / "missing.json"
    args = ["-f", str(missing_deck)]

    # Act
    code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 1
    assert "not found" in (captured.out + captured.err).lower()
    assert "Traceback" not in (captured.out + captured.err)

    # Edge Cases: Friendly error without Python exception traceback.
    # Security Vulnerabilities: None.


def test_cli_no_file_and_no_history_exits_1(tmp_path, capsys):
    """Test omitting -f when state has no history exits with code 1."""
    # Arrange
    state = tmp_path / "state.json"
    args = ["--state", str(state)]

    # Act
    code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 1
    assert "No study history yet. Please provide a deck with -f." in (
        captured.out + captured.err
    )

    # Edge Cases: Clean exit when latest-deck discovery finds no history.
    # Security Vulnerabilities: None.


def test_cli_corrupt_state_file_exits_1(tmp_path, capsys):
    """Test malformed JSON in state file names path, line, and column."""
    # Arrange
    deck = tmp_path / "deck.json"
    deck.write_text('[{"front": "F", "back": "B"}]', encoding="utf-8")
    state = tmp_path / "corrupt_state.json"
    state.write_text('{\n  "bad": json\n}', encoding="utf-8")
    args = ["-f", str(deck), "--state", str(state)]

    # Act
    code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 1
    out = captured.out + captured.err
    assert "corrupt" in out
    assert "line 2" in out
    assert "column 10" in out
    assert "Traceback" not in out

    # Edge Cases: Never overwrites corrupted state files.
    # Security Vulnerabilities: None.


def test_cli_stats_with_history(tmp_path, capsys):
    """Test --stats flag prints lifetime table across all decks and exits 0."""
    # Arrange
    state = tmp_path / "state.json"
    state_data = {
        "deck1": {"F1": {"correct": 3, "incorrect": 1, "last_seen": 10.0}},
        "upload:up.json": {
            "F2": {"correct": 2, "incorrect": 0, "last_seen": 20.0}
        },
    }
    state.write_text(json.dumps(state_data), encoding="utf-8")
    args = ["--stats", "--state", str(state)]

    # Act
    code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 0
    assert "5" in captured.out  # total correct: 3 + 2
    assert "6" in captured.out  # total attempts: 4 + 2

    # Edge Cases: Aggregates stats across standard and upload decks.
    # Security Vulnerabilities: None.


def test_cli_stats_no_history(tmp_path, capsys):
    """Test --stats flag prints 'No study history yet' and exits 0."""
    # Arrange
    state = tmp_path / "state.json"
    args = ["--stats", "--state", str(state)]

    # Act
    code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 0
    assert "No study history yet" in captured.out

    # Edge Cases: Empty or missing state outputs friendly message.
    # Security Vulnerabilities: None.


def test_cli_keyboard_interrupt_and_quit_confirmation(tmp_path, capsys):
    """Test Ctrl+C prompts confirmation and quits gracefully on 'y'."""
    # Arrange
    deck = tmp_path / "deck.json"
    deck.write_text('[{"front": "Q1", "back": "A1"}]', encoding="utf-8")
    state = tmp_path / "state.json"
    args = ["-f", str(deck), "--state", str(state)]

    # Act: Simulate Ctrl+C at prompt, then 'y' at confirmation
    with patch("builtins.input", side_effect=[KeyboardInterrupt, "y"]):
        code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert code == 0
    assert "Quit? (y/n)" in captured.out
    assert "Summary" in captured.out or "accuracy" in captured.out.lower()

    # Edge Cases: Graceful summary print without unhandled exception.
    # Security Vulnerabilities: None.


def test_cli_quit_mid_adaptive_retry_records_nothing(tmp_path, capsys):
    """Test quitting during attempt 2 in adaptive mode does not record card."""
    # Arrange
    deck = tmp_path / "deck.json"
    deck.write_text('[{"front": "Q1", "back": "A1"}]', encoding="utf-8")
    state = tmp_path / "state.json"
    args = ["-f", str(deck), "-m", "adaptive", "--state", str(state)]

    # Act: Miss attempt 1, then type 'exit', confirm 'y'
    with patch("builtins.input", side_effect=["wrong", "exit", "y"]):
        code = cli_frontend.main(args)

    # Assert
    assert code == 0
    saved = json.loads(state.read_text(encoding="utf-8"))
    assert "deck" not in saved or "Q1" not in saved.get("deck", {})

    # Edge Cases: Incomplete card trial omitted from lifetime stats.
    # Security Vulnerabilities: None.
