"""Quiz engine implementing Strategy and Factory patterns."""

from abc import ABC, abstractmethod
import json
from pathlib import Path
import random
import time
from typing import Any


class Card:
    """Flashcard domain model holding front and back text."""

    def __init__(self, front: str, back: str) -> None:
        """Initialize Card with trimmed front and back strings."""
        if not isinstance(front, str) or not isinstance(back, str):
            raise TypeError("Card front and back must be strings")
        self.front = front.strip()
        self.back = back.strip()

        # Security Vulnerabilities: None.

    def check_answer(self, user_input: str) -> bool:
        """Check if user_input matches back after trimming and casefold."""
        if not isinstance(user_input, str):
            raise TypeError("Answer input must be a string")
        return user_input.strip().casefold() == self.back.casefold()

        # Security Vulnerabilities: None.


class StateFileError(Exception):
    """Exception raised when persistent state JSON file is malformed."""

    def __init__(
        self,
        path: Path | str,
        line: int,
        column: int,
        message: str = "",
    ) -> None:
        """Initialize with file path, line, column, and message."""
        self.path = Path(path)
        self.line = line
        self.column = column
        self.message = message
        err_msg = (
            f"{self.path.name} is corrupt: {message} at line {line}, "
            f"column {column}. Fix or delete the file."
        )
        super().__init__(err_msg)

        # Edge Cases: Converts string or Path to Path object.
        # Security Vulnerabilities: None.


class QuizMode(ABC):
    """Abstract base class defining the quiz strategy contract."""

    @abstractmethod
    def get_next_card(self) -> "Card | None":
        """Retrieve the next card to be presented."""
        raise NotImplementedError

        # Security Vulnerabilities: None.

    @abstractmethod
    def record_attempt(self, card: "Card", is_correct: bool) -> None:
        """Record the outcome of answering a card."""
        raise NotImplementedError

        # Security Vulnerabilities: None.

    @abstractmethod
    def has_cards(self) -> bool:
        """Check whether cards remain available for review."""
        raise NotImplementedError

        # Security Vulnerabilities: None.


class SequentialStrategy(QuizMode):
    """Serve cards in sequential order, cycling indefinitely."""

    def __init__(self, cards: list[Card]) -> None:
        """Initialize with a list of cards and reset index to zero."""
        if not isinstance(cards, list):
            raise TypeError("Cards must be a list")
        self._cards: list[Card] = list(cards)
        self._index: int = 0

        # Security Vulnerabilities: None.

    def get_next_card(self) -> Card | None:
        """Return the next card in sequence, wrapping around when done."""
        if not self._cards:
            return None
        card = self._cards[self._index]
        self._index = (self._index + 1) % len(self._cards)
        return card

        # Security Vulnerabilities: None.

    def record_attempt(self, card: Card, is_correct: bool) -> None:
        """Record attempt outcome without altering sequential ordering."""
        # Security Vulnerabilities: None.

    def has_cards(self) -> bool:
        """Return True if the deck contains at least one card."""
        return len(self._cards) > 0

        # Security Vulnerabilities: None.


class RandomStrategy(QuizMode):
    """Serve cards in random order indefinitely."""

    def __init__(self, cards: list[Card]) -> None:
        """Initialize with a list of cards for random selection."""
        if not isinstance(cards, list):
            raise TypeError("Cards must be a list")
        self._cards: list[Card] = list(cards)

        # Security Vulnerabilities:
        # Standard pseudo-random generator is not cryptographically secure.

    def get_next_card(self) -> Card | None:
        """Return a randomly chosen card from the deck."""
        if not self._cards:
            return None
        return random.choice(self._cards)

        # Security Vulnerabilities: None.

    def record_attempt(self, card: Card, is_correct: bool) -> None:
        """Record attempt outcome without altering random selection."""
        # Security Vulnerabilities: None.

    def has_cards(self) -> bool:
        """Return True if the deck contains at least one card."""
        return len(self._cards) > 0

        # Security Vulnerabilities: None.


class AdaptiveStrategy(QuizMode):
    """Spaced Repetition Algorithm (SRA) question-serving strategy."""

    def __init__(
        self,
        cards: list[Card],
        time_provider: object = None,
        custom_intervals: dict[str, float] | None = None,
    ) -> None:
        """Initialize adaptive queues, failure tracker, and intervals."""
        if not isinstance(cards, list):
            raise TypeError("Cards must be a list")
        self._all_cards: list[Card] = list(cards)
        self.queues: dict[str, list[Card]] = {
            "new": list(cards),
            "5min": [],
            "10min": [],
            "15min": [],
        }
        self._fails: dict[str, int] = {}
        self.card_timestamps: dict[str, float] = {}
        self._time_provider = time_provider or time.time
        self.intervals = custom_intervals or {
            "5min": 300.0,
            "10min": 600.0,
            "15min": 900.0,
        }

        # Edge Cases: Defaults intervals to 300, 600, 900 seconds.
        # Security Vulnerabilities: None.

    def get_next_card(self) -> Card | None:
        """Retrieve next due card following priority: new, 5, 10, 15min."""
        if self.queues.get("new"):
            return self.queues["new"].pop(0)
        current_time = self._time_provider()
        for q_name in ("5min", "10min", "15min"):
            queue = self.queues.get(q_name, [])
            interval = self.intervals[q_name]
            for i, card in enumerate(queue):
                last_seen = self.card_timestamps.get(card.front, 0.0)
                if current_time - last_seen >= interval:
                    return queue.pop(i)
        return None

        # Edge Cases: Skips non-due cards; returns None when no cards are due.
        # Security Vulnerabilities: None.

    def _resolve_fails(
        self,
        card: Card,
        fails: int | bool,
        is_correct: bool | None,
    ) -> int:
        """Resolve effective fail count supporting both legacy and new API."""
        if is_correct is not None:
            if is_correct:
                return self._fails.pop(card.front, 0)
            self._fails[card.front] = self._fails.get(card.front, 0) + 1
            return min(self._fails[card.front], 2)
        if isinstance(fails, bool):
            if fails:
                return self._fails.pop(card.front, 0)
            self._fails[card.front] = self._fails.get(card.front, 0) + 1
            return min(self._fails[card.front], 2)
        self._fails[card.front] = fails
        return fails

        # Edge Cases: Bridges legacy bool is_correct and explicit int fails.
        # Security Vulnerabilities: None.

    def record_attempt(
        self,
        card: Card,
        fails: int | bool = 0,
        is_correct: bool | None = None,
    ) -> None:
        """Record attempt outcome and route to queue based on fail count."""
        for queue in self.queues.values():
            if card in queue:
                queue.remove(card)
        if card not in self._all_cards:
            self._all_cards.append(card)
        self.card_timestamps[card.front] = self._time_provider()
        fail_count = self._resolve_fails(card, fails, is_correct)
        target = "15min" if fail_count == 0 else (
            "10min" if fail_count == 1 else "5min"
        )
        self.queues[target].append(card)

        # Edge Cases: Routes 0->15m, 1->10m, 2+->5m; cleans old queues.
        # Security Vulnerabilities: None.

    def seconds_until_next_due(self) -> float | None:
        """Calculate seconds until the next review card is due."""
        if self.queues.get("new"):
            return 0.0
        current_time = self._time_provider()
        min_rem: float | None = None
        for q_name in ("5min", "10min", "15min"):
            queue = self.queues.get(q_name, [])
            interval = self.intervals[q_name]
            for card in queue:
                last_seen = self.card_timestamps.get(card.front, current_time)
                rem = max(0.0, interval - (current_time - last_seen))
                if min_rem is None or rem < min_rem:
                    min_rem = rem
        return min_rem

        # Edge Cases: Returns 0.0 if new cards exist, None if queues are empty.
        # Security Vulnerabilities: None.

    def to_dict(self) -> dict[str, Any]:
        """Serialize queues, failure counts, and timestamps to dictionary."""
        return {
            "queues": {
                k: [c.front for c in v]
                for k, v in self.queues.items()
            },
            "fails": dict(self._fails),
            "timestamps": dict(self.card_timestamps),
        }

        # Edge Cases: Serializes Card objects to string fronts.
        # Security Vulnerabilities: None.

    def from_dict(
        self,
        data: dict[str, Any],
        cards: list[Card] | None = None,
    ) -> None:
        """Restore queues and state from dictionary using known cards."""
        if cards is not None:
            self._all_cards = list(cards)
        card_map = {c.front: c for c in self._all_cards}
        raw_queues = data.get("queues", {})
        self.queues = {
            k: [card_map[f] for f in raw_queues.get(k, []) if f in card_map]
            for k in ("new", "5min", "10min", "15min")
        }
        self._fails = dict(data.get("fails", {}))
        self.card_timestamps = {
            k: float(v) for k, v in data.get("timestamps", {}).items()
        }

        # Edge Cases: Ignores missing card fronts not in known card pool.
        # Security Vulnerabilities: None.

    def has_cards(self) -> bool:
        """Check if any queue contains cards for review."""
        return any(len(q) > 0 for q in self.queues.values())
        # Return True if at least one queue has cards in it.
        # In English: If length of q > 0 for any q in queues, return True.

        # Security Vulnerabilities: None.

    def apply_time_decay(self, now: float | None = None) -> None:
        """Decay cards back to 5min review queue when interval expires."""
        current_time = self._time_provider() if now is None else now
        for queue_name in ("15min", "10min"):
            expired = [
                c for c in self.queues[queue_name]
                if current_time - self.card_timestamps.get(
                    c.front, current_time
                ) >= self.intervals[queue_name]
            ]
            for card in expired:
                self.queues[queue_name].remove(card)
                self.queues["5min"].append(card)

        # Security Vulnerabilities: None.


class QuizModeFactory:
    """Factory creating concrete QuizMode strategies."""

    @staticmethod
    def create_sequential(cards: list[Card]) -> SequentialStrategy:
        """Create a SequentialStrategy instance for given cards."""
        return SequentialStrategy(cards)

        # Edge Cases: None (SequentialStrategy validates cards).
        # Security Vulnerabilities: None.

    @staticmethod
    def create_random(cards: list[Card]) -> RandomStrategy:
        """Create a RandomStrategy instance for given cards."""
        return RandomStrategy(cards)

        # Edge Cases: None (RandomStrategy validates cards).
        # Security Vulnerabilities: Standard pseudo-randomness.

    @staticmethod
    def create_adaptive(
        cards: list[Card],
        time_provider: object = None,
        custom_intervals: dict[str, float] | None = None,
    ) -> AdaptiveStrategy:
        """Create an AdaptiveStrategy instance for given cards."""
        return AdaptiveStrategy(
            cards,
            time_provider=time_provider,
            custom_intervals=custom_intervals,
        )

        # Edge Cases: None (Defaults time_provider to time.time).
        # Security Vulnerabilities: None.

    createSequential = create_sequential
    createRandom = create_random
    createAdaptive = create_adaptive

    @classmethod
    def create_mode(
        cls,
        mode_name: str,
        cards: list[Card],
        **kwargs: object,
    ) -> QuizMode:
        """Create a QuizMode strategy dynamically based on mode name."""
        if not isinstance(mode_name, str):
            raise ValueError(f"Invalid quiz mode: {mode_name}")
        normalized = mode_name.strip().lower()
        if normalized == "sequential":
            return cls.create_sequential(cards)
        if normalized == "random":
            return cls.create_random(cards)
        if normalized == "adaptive":
            return cls.create_adaptive(cards, **kwargs)
        raise ValueError(f"Invalid quiz mode: {mode_name}")

        # Edge Cases: Handled case variation and whitespace in mode_name.
        # Security Vulnerabilities: None.


class QuizEngine:
    """Orchestrate quiz session loop, scoring, and persistent state."""

    def __init__(
        self,
        cards: list[Card],
        strategy: QuizMode,
        deck_name: str = "default",
        state_path: Path | str = "data/quiz_state.json",
    ) -> None:
        """Initialize QuizEngine with cards, strategy, and state path."""
        self.cards: list[Card] = list(cards)
        self.strategy: QuizMode = strategy
        self.deck_name: str = deck_name
        self.state_path: Path = Path(state_path)
        self.session_correct: int = 0
        self.session_incorrect: int = 0
        self._current_card: Card | None = None
        self.state: dict[str, Any] = self._init_state()

        # Edge Cases: Missing parent directory auto-created by _init_state.
        # Security Vulnerabilities: None.

    def _init_state(self) -> dict[str, Any]:
        """Load persistent quiz state or initialize empty file."""
        if not self.state_path.exists():
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text("{}", encoding="utf-8")
            return {}
        try:
            with open(self.state_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            raise StateFileError(
                path=self.state_path,
                line=exc.lineno,
                column=exc.colno,
                message=exc.msg,
            ) from exc

        # Edge Cases: Missing parent directories created; corrupt JSON raises.
        # Security Vulnerabilities: Path traversal if unvalidated path given.

    def _save_state(self) -> None:
        """Persist updated quiz state to state_path, propagating OSError."""
        with open(self.state_path, "w", encoding="utf-8") as file:
            json.dump(self.state, file, indent=2)

        # Edge Cases: OSError propagated to caller for warning handling.
        # Security Vulnerabilities: None.

    def grade_current_card(self, user_input: str) -> bool:
        """Grade user input for the current card without modifying state."""
        if self._current_card is None:
            self._current_card = self.strategy.get_next_card()
        if self._current_card is None:
            return False
        return self._current_card.check_answer(user_input)

        # Edge Cases: None current card returns False safely.
        # Security Vulnerabilities: None.

    def record_result(self, is_correct: bool, fails: int = 0) -> None:
        """Record final outcome, update metrics, write last_seen, advance."""
        if self._current_card is None:
            return
        if is_correct:
            self.session_correct += 1
        else:
            self.session_incorrect += 1
        if isinstance(self.strategy, AdaptiveStrategy):
            try:
                self.strategy.record_attempt(self._current_card, fails)
            except TypeError:
                self.strategy.record_attempt(self._current_card, is_correct)
        else:
            self.strategy.record_attempt(self._current_card, is_correct)
        deck_stats = self.state.setdefault(self.deck_name, {})
        stats = deck_stats.setdefault(
            self._current_card.front,
            {"correct": 0, "incorrect": 0, "last_seen": 0.0},
        )
        stats["correct" if is_correct else "incorrect"] += 1
        stats["last_seen"] = time.time()
        self._save_state()
        self._current_card = self.strategy.get_next_card()

        # Edge Cases: None current card handled; updates last_seen timestamp.
        # Security Vulnerabilities: None.

    def answer_current_card(self, user_input: str) -> bool:
        """Evaluate answer, update metrics, advance (one-attempt wrapper)."""
        is_correct = self.grade_current_card(user_input)
        if self._current_card is None:
            return False
        fails = 0 if is_correct else 1
        self.record_result(is_correct, fails=fails)
        return is_correct

        # Edge Cases: None current card returns False safely.
        # Security Vulnerabilities: None.

    def get_lifetime_accuracy(self) -> float:
        """Calculate lifetime accuracy percentage across all card attempts."""
        deck_stats = self.state.get(self.deck_name, {})
        total_correct = sum(
            card_stats.get("correct", 0)
            for card_front, card_stats in deck_stats.items()
            if card_front != "_settings" and isinstance(card_stats, dict)
        )
        total_incorrect = sum(
            card_stats.get("incorrect", 0)
            for card_front, card_stats in deck_stats.items()
            if card_front != "_settings" and isinstance(card_stats, dict)
        )
        total_attempts = total_correct + total_incorrect
        if total_attempts == 0:
            return 0.0
        return (total_correct / total_attempts) * 100.0

        # Edge Cases: Ignores _settings key; returns 0.0 if no attempts.
        # Security Vulnerabilities: None.

    def get_all_decks_stats(self) -> dict[str, Any]:
        """Compute lifetime statistics across standard and upload decks."""
        total_correct = 0
        total_incorrect = 0
        for deck_key, deck_data in self.state.items():
            if (
                deck_key == "_active_session"
                or not isinstance(deck_data, dict)
            ):
                continue
            for card_front, card_stats in deck_data.items():
                if (
                    card_front == "_settings"
                    or not isinstance(card_stats, dict)
                ):
                    continue
                total_correct += card_stats.get("correct", 0)
                total_incorrect += card_stats.get("incorrect", 0)
        total_attempts = total_correct + total_incorrect
        accuracy = (
            (total_correct / total_attempts) * 100.0
            if total_attempts > 0
            else 0.0
        )
        return {
            "total_correct": total_correct,
            "total_incorrect": total_incorrect,
            "total_attempts": total_attempts,
            "accuracy": accuracy,
        }

        # Edge Cases: Skips _active_session and _settings; 0 attempts -> 0.0%.
        # Security Vulnerabilities: None.
