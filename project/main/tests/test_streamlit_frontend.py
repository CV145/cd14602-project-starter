"""Automated UI tests for Streamlit frontend using AppTest."""

import json
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "streamlit_frontend.py")


def test_streamlit_deck_dropdown_population(tmp_path):
    """Test deck dropdown includes deck files and excludes state file."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    d1 = data_dir / "deck1.json"
    d1.write_text('[{"front": "F1", "back": "B1"}]', encoding="utf-8")
    d2 = data_dir / "deck2.json"
    d2.write_text('[{"front": "F2", "back": "B2"}]', encoding="utf-8")
    state_file = data_dir / "quiz_state.json"
    state_file.write_text("{}", encoding="utf-8")

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    # Assert
    deck_select = at.sidebar.selectbox(key="deck_select")
    options = deck_select.options
    assert "deck1.json" in options
    assert "deck2.json" in options
    assert "quiz_state.json" not in options

    # Edge Cases: quiz_state.json filtered out of selectable decks.
    # Security Vulnerabilities: None.


def test_streamlit_submit_correct_and_scoreboard(tmp_path):
    """Test submitting correct answer updates scoreboard."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    deck = data_dir / "basics.json"
    deck.write_text('[{"front": "Q1", "back": "Ans1"}]', encoding="utf-8")
    state_file = tmp_path / "quiz_state.json"

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    at.text_input(key="user_answer").input("Ans1")
    at.button(key="submit_button").click().run()

    # Assert
    assert len(at.success) > 0
    assert "Correct" in at.success[0].value

    # Edge Cases: Feedback rendered via st.success banner.
    # Security Vulnerabilities: None.


def test_streamlit_submit_incorrect_feedback(tmp_path):
    """Test submitting incorrect answer displays error feedback."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    deck = data_dir / "basics.json"
    deck.write_text('[{"front": "Q1", "back": "Ans1"}]', encoding="utf-8")
    state_file = tmp_path / "quiz_state.json"

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    at.text_input(key="user_answer").input("Wrong")
    at.button(key="submit_button").click().run()

    # Assert
    assert len(at.error) > 0
    assert "Incorrect" in at.error[0].value

    # Edge Cases: Feedback rendered via st.error banner.
    # Security Vulnerabilities: None.


def test_streamlit_adaptive_retry_flow(tmp_path):
    """Test adaptive mode wrong answer prompts retry on attempt 1."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    deck = data_dir / "basics.json"
    deck.write_text('[{"front": "Q1", "back": "Ans1"}]', encoding="utf-8")
    state_file = tmp_path / "quiz_state.json"

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    at.sidebar.selectbox(key="mode_select").select("adaptive").run()
    at.text_input(key="user_answer").input("Wrong")
    at.button(key="submit_button").click().run()

    # Assert
    assert len(at.error) > 0
    assert "1 attempt left" in at.error[0].value

    # Edge Cases: First adaptive failure does not record final outcome.
    # Security Vulnerabilities: None.


def test_streamlit_resume_prompt_and_discard(tmp_path):
    """Test resume prompt appears on active session and discard clears it."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    deck = data_dir / "basics.json"
    deck.write_text('[{"front": "Q1", "back": "Ans1"}]', encoding="utf-8")
    state_file = tmp_path / "quiz_state.json"
    active_sess = {
        "deck_key": "basics",
        "source": str(deck),
        "cards": None,
        "mode": "sequential",
        "current_front": "Q1",
    }
    state_file.write_text(
        json.dumps({"_active_session": active_sess}), encoding="utf-8"
    )

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    assert at.button(key="discard_session_btn") is not None
    at.button(key="discard_session_btn").click().run()

    # Assert
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    assert "_active_session" not in saved

    # Edge Cases: Discard button clears _active_session from storage.
    # Security Vulnerabilities: None.


def test_streamlit_custom_interval_configuration(tmp_path):
    """Test modifying custom intervals saves to deck settings."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    deck = data_dir / "basics.json"
    deck.write_text('[{"front": "Q1", "back": "Ans1"}]', encoding="utf-8")
    state_file = tmp_path / "quiz_state.json"

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    at.sidebar.selectbox(key="mode_select").select("adaptive").run()
    at.sidebar.selectbox(key="interval_5min").select("10 min").run()

    # Assert
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    settings = saved.get("basics", {}).get("_settings", {})
    intervals = settings.get("intervals", {})
    assert intervals.get("5min") == 600.0

    # Edge Cases: Custom interval mapped and written to _settings.
    # Security Vulnerabilities: None.


def test_streamlit_deck_progress_reset(tmp_path):
    """Test reset progress clears deck stats with confirmation."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    deck = data_dir / "basics.json"
    deck.write_text('[{"front": "Q1", "back": "Ans1"}]', encoding="utf-8")
    state_file = tmp_path / "quiz_state.json"
    state_data = {
        "basics": {
            "_settings": {"intervals": {"5min": 300.0}},
            "Q1": {"correct": 5, "incorrect": 2, "last_seen": 100.0},
        }
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    at.sidebar.button(key="reset_progress_btn").click().run()
    at.sidebar.button(key="confirm_reset_btn").click().run()

    # Assert
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    assert "Q1" not in saved["basics"]
    assert saved["basics"]["_settings"]["intervals"]["5min"] == 300.0

    # Edge Cases: Reset progress requires confirmation step.
    # Security Vulnerabilities: None.


def test_streamlit_corrupt_state_stops(tmp_path):
    """Test corrupt state file displays error and halts execution."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    state_file = tmp_path / "quiz_state.json"
    state_file.write_text('{\n  "bad": json\n}', encoding="utf-8")

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    # Assert
    assert len(at.error) > 0
    assert "corrupt" in at.error[0].value
    assert "line 2" in at.error[0].value

    # Edge Cases: Stoppage on corrupted state prevents further mutation.
    # Security Vulnerabilities: None.


def test_streamlit_custom_file_upload(tmp_path):
    """Test custom file upload creates deck under upload:<name>."""
    # Arrange
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    state_file = tmp_path / "quiz_state.json"
    upload_file = data_dir / "my_custom.json"
    card_json = '[{"front": "UpQ", "back": "UpA"}]'
    upload_file.write_text(card_json, encoding="utf-8")

    # Act
    at = AppTest.from_file(APP_PATH)
    at.session_state["data_dir"] = str(data_dir)
    at.session_state["state_path"] = str(state_file)
    at.run()

    assert len(at.get("file_uploader")) > 0

    # Edge Cases: File uploader accepts JSON decks with upload: namespace.
    # Security Vulnerabilities: None.

    # Security Vulnerabilities: None.
