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

        # Security Vulnerabilities: None.

    def get_next_card(self) -> Card | None:
        """Retrieve next card following priority order: new, 5, 10, 15min."""
        for queue_name in ("new", "5min", "10min", "15min"):
            queue = self.queues.get(queue_name, [])
            if queue:
                return queue.pop(0)
        return None

        # Security Vulnerabilities: None.

    def record_attempt(self, card: Card, is_correct: bool) -> None:
        """Record attempt outcome and transition card between queues."""
        for queue in self.queues.values():
            if card in queue:
                queue.remove(card)
        self.card_timestamps[card.front] = self._time_provider()
        if not is_correct:
            self._fails[card.front] = self._fails.get(card.front, 0) + 1
            self.queues["5min"].append(card)
        else:
            fails = self._fails.pop(card.front, 0)
            if fails == 0:
                target = "15min"
            elif fails == 1:
                target = "10min"
            else:
                target = "5min"
            self.queues[target].append(card)

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
        except (json.JSONDecodeError, OSError):
            return {}

        # Edge Cases: Missing parent directories created; corrupt JSON -> {}.
        # Security Vulnerabilities: Path traversal if unvalidated path given.

    def _save_state(self) -> None:
        """Persist updated quiz state to state_path."""
        try:
            with open(self.state_path, "w", encoding="utf-8") as file:
                json.dump(self.state, file, indent=2)
        except OSError:
            pass

        # Edge Cases: Handled OS filesystem write failures silently.
        # Security Vulnerabilities: None.

    def answer_current_card(self, user_input: str) -> bool:
        """Evaluate answer, update session and lifetime metrics, advance."""
        if self._current_card is None:
            self._current_card = self.strategy.get_next_card()
        if self._current_card is None:
            return False
        is_correct = self._current_card.check_answer(user_input)
        if is_correct:
            self.session_correct += 1
        else:
            self.session_incorrect += 1
        self.strategy.record_attempt(self._current_card, is_correct)
        deck_stats = self.state.setdefault(self.deck_name, {})
        stats = deck_stats.setdefault(
            self._current_card.front, {"correct": 0, "incorrect": 0}
        )
        stats["correct" if is_correct else "incorrect"] += 1
        self._save_state()
        self._current_card = self.strategy.get_next_card()
        return is_correct

        # Edge Cases: None cards remaining returns False safely.
        # Security Vulnerabilities: None.

    def get_lifetime_accuracy(self) -> float:
        """Calculate lifetime accuracy percentage across all card attempts."""
        deck_stats = self.state.get(self.deck_name, {})
        total_correct = sum(
            stats.get("correct", 0) for stats in deck_stats.values()
        )
        total_incorrect = sum(
            stats.get("incorrect", 0) for stats in deck_stats.values()
        )
        total_attempts = total_correct + total_incorrect
        if total_attempts == 0:
            return 0.0
        return (total_correct / total_attempts) * 100.0

        # Edge Cases: Zero total attempts returns 0.0, avoiding division by 0.
        # Security Vulnerabilities: None.
