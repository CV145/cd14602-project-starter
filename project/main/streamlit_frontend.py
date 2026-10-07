"""Streamlit presentation layer for Flashcard Quizzer web application."""

import json
from pathlib import Path
from typing import Any

import streamlit as st

from utils.quiz_engine import AdaptiveStrategy
from utils.session_controller import SessionController

INTERVAL_SECONDS = {
    "5 min": 300.0,
    "10 min": 600.0,
    "15 min": 900.0,
    "30 min": 1800.0,
    "1 h": 3600.0,
    "24 h": 86400.0,
    "1 week": 604800.0,
}


def _get_config_paths() -> tuple[Path, Path]:
    """Retrieve data directory and state file paths from session state."""
    data_dir = Path(st.session_state.get("data_dir", "data"))
    default_state = data_dir / "quiz_state.json"
    state_path = Path(st.session_state.get("state_path", default_state))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, state_path

    # Edge Cases: Preserves pre-configured testing paths in session state.
    # Security Vulnerabilities: None.


def _check_state_integrity(state_path: Path) -> dict[str, Any]:
    """Verify persistent state file integrity or stop on corruption."""
    if not state_path.is_file():
        return {}
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        err_msg = (
            f"{state_path.name} is corrupt: {exc.msg} at line {exc.lineno}, "
            f"column {exc.colno}. Fix or delete the file."
        )
        st.error(err_msg)
        st.stop()
    except OSError as exc:
        st.error(f"Cannot read state file: {exc}")
        st.stop()
    return {}

    # Edge Cases: Calls st.stop() to halt rendering on corrupted state.
    # Security Vulnerabilities: None.


def _discover_deck_options(data_dir: Path, state_path: Path) -> list[str]:
    """Find all JSON decks in data directory excluding the state file."""
    state_name = state_path.name
    files = sorted(
        [f.name for f in data_dir.glob("*.json") if f.name != state_name]
    )
    return files

    # Edge Cases: State file is filtered out of deck selection dropdown.
    # Security Vulnerabilities: None.


def _get_or_create_controller(
    deck_path: Path, mode: str, state_path: Path
) -> SessionController:
    """Retrieve cached SessionController or initialize on deck/mode shift."""
    curr_deck = str(deck_path)
    if (
        st.session_state.get("controller") is None
        or st.session_state.get("active_deck") != curr_deck
        or st.session_state.get("active_mode") != mode
    ):
        st.session_state["controller"] = SessionController(
            deck_path, mode=mode, state_path=state_path
        )
        st.session_state["active_deck"] = curr_deck
        st.session_state["active_mode"] = mode
        st.session_state["session_active"] = False
        st.session_state["feedback"] = None

    return st.session_state["controller"]

    # Edge Cases: Resets session_active and feedback on deck or mode shift.
    # Security Vulnerabilities: None.


def _render_intervals_config(controller: SessionController) -> None:
    """Render adaptive interval selection dropdowns in sidebar."""
    st.sidebar.markdown("### Adaptive Intervals")
    current = controller.get_custom_intervals()
    options = list(INTERVAL_SECONDS.keys())

    cur_5 = "5 min" if current.get("5min") == 300.0 else "10 min"
    selected_5 = st.sidebar.selectbox(
        "5min Queue Interval",
        options,
        index=options.index(cur_5) if cur_5 in options else 0,
        key="interval_5min",
    )
    new_intervals = {
        "5min": INTERVAL_SECONDS[selected_5],
        "10min": current.get("10min", 600.0),
        "15min": current.get("15min", 900.0),
    }
    controller.set_custom_intervals(new_intervals)

    # Edge Cases: Maps human readable times to epoch seconds in settings.
    # Security Vulnerabilities: None.


def _render_sidebar(
    controller: SessionController, data_dir: Path, state_path: Path
) -> None:
    """Render sidebar controls, deck stats, and queue distribution."""
    st.sidebar.title("Quizzer Controls")
    st.sidebar.file_uploader(
        "Upload Custom Deck (.json)", type=["json"], key="deck_uploader"
    )

    if st.sidebar.button("Reset Progress", key="reset_progress_btn"):
        st.session_state["show_reset_confirm"] = True

    if st.session_state.get("show_reset_confirm"):
        st.sidebar.warning("Reset all card progress for this deck?")
        if st.sidebar.button("Confirm Reset", key="confirm_reset_btn"):
            controller.reset_deck_progress()
            st.session_state["controller"] = None
            st.session_state["feedback"] = None
            st.session_state["session_active"] = False
            st.session_state["show_reset_confirm"] = False
            st.rerun()

    if controller.mode == "adaptive":
        _render_intervals_config(controller)

    _render_stats_panel(controller)

    # Edge Cases: Purges cached controller and feedback on confirmed reset.
    # Security Vulnerabilities: None.


def _render_stats_panel(controller: SessionController) -> None:
    """Display scoreboard, lifetime accuracy, and queue counts."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Session Scoreboard")
    correct = controller.engine.session_correct
    incorrect = controller.engine.session_incorrect
    st.sidebar.write(f"Correct: **{correct}** | Incorrect: **{incorrect}**")

    lifetime = controller.engine.get_lifetime_accuracy()
    st.sidebar.write(f"Deck Lifetime Accuracy: **{lifetime:.1f}%**")

    if isinstance(controller.engine.strategy, AdaptiveStrategy):
        st.sidebar.markdown("### Spaced Repetition Queues")
        strat = controller.engine.strategy
        for q_name in ("new", "5min", "10min", "15min"):
            st.sidebar.write(f"{q_name}: {len(strat.queues.get(q_name, []))}")

    # Edge Cases: Displays live count per adaptive queue.
    # Security Vulnerabilities: None.


def _handle_submission(controller: SessionController) -> None:
    """Process answer submission and save feedback for next render pass."""
    ans = st.session_state.get("user_answer", "")
    res = controller.process_input(ans)
    if res.status == "empty":
        st.warning("Please type an answer (or click Skip)")
        return

    if res.status == "retry":
        st.session_state["feedback"] = ("error", res.message)
    elif res.status == "correct":
        st.session_state["feedback"] = ("success", "✔ Correct!")
    elif res.status == "incorrect":
        msg = f"✘ Incorrect. Answer: {res.correct_answer}"
        st.session_state["feedback"] = ("error", msg)

    st.rerun()

    # Edge Cases: Inline warning on empty input; queues feedback & reruns.
    # Security Vulnerabilities: None.


def _render_card_panel(controller: SessionController) -> None:
    """Render flashcard front, answer form, and feedback."""
    st.session_state["session_active"] = True
    feedback = st.session_state.pop("feedback", None)
    if feedback:
        getattr(st, feedback[0], st.info)(feedback[1])

    card = controller.get_current_card()
    if card is None:
        controller.discard_active_session()
        st.success("🎉 All caught up!")
        return

    st.markdown(f"## Card: {card.front}")
    with st.form("quiz_form", clear_on_submit=True):
        st.text_input("Your Answer:", key="user_answer")
        col1, col2 = st.columns(2)
        submit = col1.form_submit_button("Submit", key="submit_button")
        skip = col2.form_submit_button("Skip", key="skip_button")
        if submit:
            _handle_submission(controller)
        elif skip:
            res = controller.process_input("skip")
            msg = f"Skipped. Answer: {res.correct_answer}"
            st.session_state["feedback"] = ("warning", msg)
            st.rerun()

    # Edge Cases: Clears active session on completion; queues skip feedback.
    # Security Vulnerabilities: Safe rendering without HTML injection.


def _render_resume_prompt(controller: SessionController) -> bool:
    """Check for active session and render resume/discard dialog."""
    if st.session_state.get("session_active") is True:
        return False

    active_sess = controller.engine.state.get("_active_session")
    if not active_sess or not isinstance(active_sess, dict):
        return False
    if active_sess.get("deck_key") != controller.deck_key:
        return False

    st.info("Found an active study session for this deck.")
    col1, col2 = st.columns(2)
    if col1.button("Resume Session", key="resume_session_btn"):
        controller.resume_active_session()
        st.session_state["session_active"] = True
        st.session_state["feedback"] = None
        st.rerun()
    if col2.button("Discard Session", key="discard_session_btn"):
        controller.discard_active_session()
        st.session_state["session_active"] = True
        st.session_state["feedback"] = None
        st.rerun()
    return True

    # Edge Cases: Skips prompt when session_active is True; clears feedback.
    # Security Vulnerabilities: None.


def main() -> None:
    """Streamlit application root coordinator."""
    st.set_page_config(page_title="Flashcard Quizzer", layout="wide")
    data_dir, state_path = _get_config_paths()
    _check_state_integrity(state_path)

    deck_files = _discover_deck_options(data_dir, state_path)
    default_deck = deck_files[0] if deck_files else None

    selected_deck = st.sidebar.selectbox(
        "Choose a Deck",
        deck_files,
        index=0 if default_deck else None,
        key="deck_select",
    )
    selected_mode = st.sidebar.selectbox(
        "Study Mode",
        ["sequential", "random", "adaptive"],
        index=0,
        key="mode_select",
    )

    if not selected_deck:
        st.info("Please select or upload a deck to get started.")
        return

    deck_path = data_dir / selected_deck
    controller = _get_or_create_controller(
        deck_path, selected_mode, state_path
    )

    _render_sidebar(controller, data_dir, state_path)
    if not _render_resume_prompt(controller):
        _render_card_panel(controller)

    # Edge Cases: Guards against empty deck selections and missing files.
    # Security Vulnerabilities: None.


if __name__ == "__main__":
    main()
