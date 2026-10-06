"""Session controller facade managing quiz rules, flows, and state."""

from collections import Counter
import json
from pathlib import Path
from typing import Any

from dataclasses import dataclass

from utils.file_handler import load_flashcard_data
from utils.quiz_engine import (
    AdaptiveStrategy,
    Card,
    QuizEngine,
    QuizModeFactory,
)


@dataclass
class InputResult:
    """Result of processing user input in SessionController."""

    status: str
    message: str = ""
    command: str | None = None
    correct_answer: str = ""
    attempt: int = 1
    seconds_until_due: float | None = None


class SessionController:
    """UI-agnostic Facade orchestrating quiz sessions and persistence."""

    def __init__(
        self,
        deck_path: Path | str,
        mode: str = "sequential",
        state_path: Path | str = "data/quiz_state.json",
        custom_intervals: dict[str, float] | None = None,
    ) -> None:
        """Initialize session controller with validated deck and engine."""
        self.deck_path = Path(deck_path)
        self.state_path = Path(state_path)
        self.mode = mode.strip().lower()
        self.cards, self.warnings = self.validate_and_load_deck(
            self.deck_path, self.state_path
        )
        self.deck_key = self._resolve_deck_key(self.deck_path)
        intervals = custom_intervals or self._load_saved_intervals()
        strategy = QuizModeFactory.create_mode(
            self.mode, self.cards, custom_intervals=intervals
        )
        self.engine = QuizEngine(
            cards=self.cards,
            strategy=strategy,
            deck_name=self.deck_key,
            state_path=self.state_path,
        )
        self.current_attempt: int = 1
        self._pending_collision: str | None = None

        # Edge Cases: Normalizes mode name and resolves deck keys.
        # Security Vulnerabilities: None.

    def _load_saved_intervals(self) -> dict[str, float] | None:
        """Load stored intervals for deck from state file if present."""
        if not self.state_path.is_file():
            return None
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                st = json.load(f)
            return (
                st.get(self.deck_key, {})
                .get("_settings", {})
                .get("intervals")
            )
        except (json.JSONDecodeError, OSError):
            return None

        # Edge Cases: Returns None on missing file or JSON error.
        # Security Vulnerabilities: None.

    @staticmethod
    def _resolve_deck_key(deck_path: Path | str) -> str:
        """Resolve persistent state deck key from deck path."""
        p = Path(deck_path)
        if str(deck_path).startswith("upload:"):
            clean_name = Path(str(deck_path).replace("upload:", "")).name
            return f"upload:{clean_name}"
        return p.stem

        # Edge Cases: Strips directory traversal components for upload decks.
        # Security Vulnerabilities: Prevents path traversal in deck keys.

    @classmethod
    def validate_and_load_deck(
        cls,
        deck_path: Path | str,
        state_path: Path | str = "data/quiz_state.json",
    ) -> tuple[list[Card], list[str]]:
        """Validate and load deck contents, returning Cards and warnings."""
        path_str = str(deck_path)
        actual_path = Path(
            path_str[7:] if path_str.startswith("upload:") else path_str
        )
        if not actual_path.is_file():
            raise FileNotFoundError(f"Deck file not found: {deck_path}")
        if actual_path.suffix.lower() != ".json":
            raise ValueError(
                f"Deck file must have .json extension: {actual_path.name}"
            )
        if actual_path.stat().st_size > 1024 * 1024:
            raise ValueError("File size exceeds 1 MB limit")

        raw_cards = load_flashcard_data(actual_path)
        if not raw_cards:
            raise ValueError("Deck is empty: must contain at least 1 card")

        fronts = [c["front"] for c in raw_cards]
        if any(f == "_settings" for f in fronts):
            raise ValueError("Card front cannot be '_settings'")

        warnings = cls._extract_duplicate_warnings(fronts)
        cards = [Card(c["front"], c["back"]) for c in raw_cards]
        return cards, warnings

        # Edge Cases: Validates existence, size <= 1MB, .json, and non-empty.
        # Security Vulnerabilities: Enforces 1MB size limit against DoS.

    @staticmethod
    def _extract_duplicate_warnings(fronts: list[str]) -> list[str]:
        """Detect duplicate card fronts and build warning descriptions."""
        counts = Counter(fronts)
        warnings: list[str] = []
        for front, count in counts.items():
            if count > 1:
                warnings.append(
                    f"Duplicate card front '{front}' appears {count} times"
                )
        return warnings

        # Edge Cases: Multiple duplicate fronts each recorded in warnings.
        # Security Vulnerabilities: None.

    @staticmethod
    def get_latest_deck_path(
        state_path: Path | str = "data/quiz_state.json",
        data_dir: Path | str = "data",
    ) -> Path | None:
        """Find the non-upload deck with the latest study timestamp."""
        path = Path(state_path)
        if not path.is_file():
            return None
        try:
            with open(path, "r", encoding="utf-8") as file:
                state_data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return None

        best_deck, max_ts = SessionController._find_max_last_seen(state_data)
        if best_deck is None:
            return None
        return Path(data_dir) / f"{best_deck}.json"

        # Edge Cases: Returns None on missing/empty state, or only uploads.
        # Security Vulnerabilities: None.

    @staticmethod
    def _find_max_last_seen(
        state_data: dict[str, Any],
    ) -> tuple[str | None, float]:
        """Scan state data for non-upload deck with greatest last_seen."""
        best_deck: str | None = None
        max_ts: float = -1.0
        for deck_key, deck_val in state_data.items():
            if deck_key == "_active_session" or deck_key.startswith("upload:"):
                continue
            if not isinstance(deck_val, dict):
                continue
            for front, card_data in deck_val.items():
                if front == "_settings" or not isinstance(card_data, dict):
                    continue
                ts = card_data.get("last_seen", -1.0)
                if ts > max_ts:
                    max_ts = ts
                    best_deck = deck_key
        return best_deck, max_ts

        # Edge Cases: Skips _active_session, _settings, and upload: prefixes.
        # Security Vulnerabilities: None.

    def get_current_card(self) -> Card | None:
        """Retrieve the current active card from the quiz engine."""
        if self.engine._current_card is None:
            self.engine._current_card = self.engine.strategy.get_next_card()
        return self.engine._current_card

        # Edge Cases: Initializes current card if uninitialized.
        # Security Vulnerabilities: None.

    def process_input(self, raw_input: str) -> InputResult:
        """Process user input: commands, attempts, collisions, and grading."""
        cleaned = raw_input.strip()
        if not cleaned:
            return InputResult(
                status="empty",
                message="Please type an answer (or 'exit' / 'skip')",
                attempt=self.current_attempt,
            )

        card = self.get_current_card()
        if card is None:
            return InputResult(status="done")

        cmd = cleaned.casefold()
        if cmd in ("exit", "skip"):
            if card.check_answer(cleaned):
                self._pending_collision = cmd
                return InputResult(
                    status="collision",
                    command=cmd,
                    message="✔ Correct",
                    correct_answer=card.back,
                    attempt=self.current_attempt,
                )
            if cmd == "exit":
                return InputResult(status="exit")
            return self._handle_skip(card)

        return self._handle_answer(card, cleaned)

        # Edge Cases: Disambiguates exit/skip answers from commands.
        # Security Vulnerabilities: None.

    def _handle_skip(self, card: Card) -> InputResult:
        """Handle skip command recording 1 incorrect and advancing card."""
        correct_answer = card.back
        fails = 2 if self.mode == "adaptive" else 1
        self.engine.record_result(is_correct=False, fails=fails)
        self.current_attempt = 1
        self._save_active_session()
        return InputResult(
            status="skip",
            message=f"Answer: {correct_answer}",
            correct_answer=correct_answer,
            attempt=1,
        )

        # Edge Cases: Routes adaptive skips directly to Difficult (fails 2).
        # Security Vulnerabilities: None.

    def _handle_answer(self, card: Card, answer: str) -> InputResult:
        """Evaluate submitted answer across modes and attempt counts."""
        is_correct = self.engine.grade_current_card(answer)
        if is_correct:
            fails = 0 if self.current_attempt == 1 else 1
            self.engine.record_result(is_correct=True, fails=fails)
            self.current_attempt = 1
            self._save_active_session()
            return InputResult(
                status="correct", message="✔ Correct", attempt=1
            )

        if self.mode == "adaptive" and self.current_attempt == 1:
            self.current_attempt = 2
            return InputResult(
                status="retry",
                message="✘ Incorrect, try again (1 attempt left)",
                attempt=2,
            )

        fails = 2 if self.mode == "adaptive" else 1
        self.engine.record_result(is_correct=False, fails=fails)
        self.current_attempt = 1
        self._save_active_session()
        return InputResult(
            status="incorrect",
            message=f"✘ Incorrect: {card.back}",
            correct_answer=card.back,
            attempt=1,
        )

        # Edge Cases: Multi-attempt retry on first adaptive failure.
        # Security Vulnerabilities: None.

    def resolve_collision(self, confirmed: bool) -> InputResult:
        """Resolve command vs answer collision after user confirmation."""
        cmd = self._pending_collision
        self._pending_collision = None
        card = self.get_current_card()
        if confirmed:
            if cmd == "exit":
                return InputResult(status="exit")
            return self._handle_skip(card)

        fails = 0 if self.current_attempt == 1 else 1
        self.engine.record_result(is_correct=True, fails=fails)
        self.current_attempt = 1
        self._save_active_session()
        return InputResult(status="correct", message="✔ Correct", attempt=1)

        # Edge Cases: Confirmed quit drops grade; declined confirms answer.
        # Security Vulnerabilities: None.

    def _save_active_session(self) -> None:
        """Persist current session progress into _active_session in state."""
        curr = self.get_current_card()
        curr_front = curr.front if curr else None
        is_upload = self.deck_key.startswith("upload:")
        cards_dump = (
            [{"front": c.front, "back": c.back} for c in self.cards]
            if is_upload
            else None
        )
        sess_data: dict[str, Any] = {
            "deck_key": self.deck_key,
            "source": str(self.deck_path),
            "cards": cards_dump,
            "mode": self.mode,
            "session_correct": self.engine.session_correct,
            "session_incorrect": self.engine.session_incorrect,
            "current_front": curr_front,
            "attempt": self.current_attempt,
        }
        if isinstance(self.engine.strategy, AdaptiveStrategy):
            sess_data.update(self.engine.strategy.to_dict())
        self.engine.state["_active_session"] = sess_data
        self.engine._save_state()

        # Edge Cases: Serializes in-memory cards for uploaded decks.
        # Security Vulnerabilities: None.

    def discard_active_session(self) -> None:
        """Discard active session state from state file."""
        if "_active_session" in self.engine.state:
            del self.engine.state["_active_session"]
            self.engine._save_state()

        # Edge Cases: Safe deletion when _active_session key exists.
        # Security Vulnerabilities: None.

    def resume_active_session(self) -> bool:
        """Restore active session state if matching deck and valid target."""
        sess = self.engine.state.get("_active_session")
        if not sess or not isinstance(sess, dict):
            return False
        if sess.get("deck_key") != self.deck_key:
            return False

        target_front = sess.get("current_front")
        all_fronts = [c.front for c in self.cards]
        if target_front is not None and target_front not in all_fronts:
            self.discard_active_session()
            return False

        self.engine.session_correct = int(sess.get("session_correct", 0))
        self.engine.session_incorrect = int(sess.get("session_incorrect", 0))
        self.current_attempt = int(sess.get("attempt", 1))

        if self.mode == "adaptive" and isinstance(
            self.engine.strategy, AdaptiveStrategy
        ):
            self.engine.strategy.from_dict(sess, cards=self.cards)
            self.engine._current_card = None
        else:
            self._restore_current_card(target_front)

        return True

        # Edge Cases: Restores attempt counts and queues; ignores missing.
        # Security Vulnerabilities: None.

    def _restore_current_card(self, target_front: str | None) -> None:
        """Position engine current card to the saved target front."""
        if target_front is None:
            return
        if self.mode == "sequential":
            strat = self.engine.strategy
            for _ in range(len(self.cards)):
                card = strat.get_next_card()
                if card and card.front == target_front:
                    self.engine._current_card = card
                    break
        elif self.mode == "random":
            for card in self.cards:
                if card.front == target_front:
                    self.engine._current_card = card
                    break

        # Edge Cases: Matches target card front in sequential or random mode.
        # Security Vulnerabilities: None.

    def set_custom_intervals(self, intervals: dict[str, float]) -> None:
        """Save custom review intervals under deck settings."""
        deck_data = self.engine.state.setdefault(self.deck_key, {})
        settings = deck_data.setdefault("_settings", {})
        settings["intervals"] = dict(intervals)
        self.engine._save_state()

        # Edge Cases: Overwrites intervals dictionary under _settings.
        # Security Vulnerabilities: None.

    def get_custom_intervals(self) -> dict[str, float]:
        """Retrieve custom review intervals from deck settings or defaults."""
        default_intervals = {"5min": 300.0, "10min": 600.0, "15min": 900.0}
        deck_data = self.engine.state.get(self.deck_key, {})
        settings = deck_data.get("_settings", {})
        return dict(settings.get("intervals", default_intervals))

        # Edge Cases: Falls back to default intervals if not configured.
        # Security Vulnerabilities: None.

    def reset_deck_progress(self) -> None:
        """Purge deck card statistics and matching active session."""
        deck_data = self.engine.state.setdefault(self.deck_key, {})
        settings = deck_data.get("_settings")
        self.engine.state[self.deck_key] = (
            {"_settings": settings} if settings is not None else {}
        )
        active_sess = self.engine.state.get("_active_session")
        if active_sess and active_sess.get("deck_key") == self.deck_key:
            del self.engine.state["_active_session"]
        self.engine._save_state()

        # Edge Cases: Retains _settings while clearing card performance stats.
        # Security Vulnerabilities: None.
