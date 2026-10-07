"""Unit tests for quiz modes and strategy pattern implementations."""

import pytest

from utils.quiz_engine import (
    AdaptiveStrategy,
    Card,
    QuizModeFactory,
    RandomStrategy,
    SequentialStrategy,
)


def test_card_initialization_and_trimming():
    """Test Card stores front/back and trims leading/trailing whitespace."""
    # Arrange
    front = "  What is Python?  "
    back = "  A programming language.  "

    # Act
    card = Card(front, back)

    # Assert
    assert card.front == "What is Python?"
    assert card.back == "A programming language."

    # Security Vulnerabilities: None.


def test_card_check_answer_case_insensitive_and_trimmed():
    """Test check_answer trims whitespace and matches case-insensitively."""
    # Arrange
    card = Card("What is Python?", "A programming language.")

    # Act
    exact_match = card.check_answer("a programming language.")
    padded_match = card.check_answer("  A PROGRAMMING LANGUAGE.  ")
    wrong_match = card.check_answer("A compiled language.")

    # Assert
    assert exact_match is True
    assert padded_match is True
    assert wrong_match is False

    # Security Vulnerabilities: None.


def test_sequential_strategy_serves_in_order_and_wraps():
    """Test SequentialStrategy serves cards in order and cycles on end."""
    # Arrange
    card1 = Card("Front 1", "Back 1")
    card2 = Card("Front 2", "Back 2")
    strategy = SequentialStrategy([card1, card2])

    # Act
    served_1 = strategy.get_next_card()
    served_2 = strategy.get_next_card()
    served_3 = strategy.get_next_card()

    # Assert
    assert strategy.has_cards() is True
    assert served_1 == card1
    assert served_2 == card2
    assert served_3 == card1

    # Security Vulnerabilities: None.


def test_random_strategy_serves_cards_from_deck():
    """Test RandomStrategy serves cards non-deterministically from deck."""
    # Arrange
    cards = [Card(f"F{i}", f"B{i}") for i in range(5)]
    strategy = RandomStrategy(cards)

    # Act
    served = [strategy.get_next_card() for _ in range(25)]

    # Assert
    assert strategy.has_cards() is True
    assert all(c in cards for c in served)
    assert len(set(served)) > 1

    # Security Vulnerabilities: None.


def test_adaptive_priority_order():
    """Test AdaptiveStrategy serves cards in queue priority order."""
    # Arrange
    c_new = Card("NewFront", "NewBack")
    c_5min = Card("5Front", "5Back")
    strat = AdaptiveStrategy([c_new])
    strat.queues["5min"].append(c_5min)

    # Act
    first_served = strat.get_next_card()
    second_served = strat.get_next_card()

    # Assert
    assert first_served == c_new
    assert second_served == c_5min

    # Security Vulnerabilities: None.


def test_adaptive_attempt_transitions():
    """Test transitions: 0 fails->15min, 1 fail->10min, 2 fails->5min."""
    # Arrange
    c1, c2, c3 = Card("F1", "B1"), Card("F2", "B2"), Card("F3", "B3")
    strat = AdaptiveStrategy([])
    strat.queues["5min"].extend([c1, c2, c3])

    # Act
    strat.record_attempt(c1, is_correct=True)
    strat.record_attempt(c2, is_correct=False)
    strat.record_attempt(c2, is_correct=True)
    strat.record_attempt(c3, is_correct=False)
    strat.record_attempt(c3, is_correct=False)

    # Assert
    assert c1 in strat.queues["15min"]
    assert c2 in strat.queues["10min"]
    assert c3 in strat.queues["5min"]

    # Security Vulnerabilities: None.


def test_adaptive_time_decay():
    """Test cards decay to higher-priority queues as time elapses."""
    # Arrange
    card = Card("DecayFront", "DecayBack")
    start_time = 1000.0
    strat = AdaptiveStrategy([], time_provider=lambda: start_time)
    strat.queues["15min"].append(card)
    strat.card_timestamps[card.front] = start_time

    # Act
    strat.apply_time_decay(now=start_time + 950.0)

    # Assert
    assert card in strat.queues["5min"]
    assert card not in strat.queues["15min"]

    # Security Vulnerabilities: None.


def test_quiz_mode_factory_dedicated_methods():
    """Test QuizModeFactory dedicated factory methods instantiate modes."""
    # Arrange
    cards = [Card("F", "B")]

    # Act
    seq = QuizModeFactory.create_sequential(cards)
    rand = QuizModeFactory.create_random(cards)
    adapt = QuizModeFactory.create_adaptive(cards)

    # Assert
    assert isinstance(seq, SequentialStrategy)
    assert isinstance(rand, RandomStrategy)
    assert isinstance(adapt, AdaptiveStrategy)

    # Security Vulnerabilities: None.


def test_quiz_mode_factory_camel_case_aliases():
    """Test QuizModeFactory camelCase aliases instantiate modes."""
    # Arrange
    cards = [Card("F", "B")]

    # Act
    seq = QuizModeFactory.createSequential(cards)
    rand = QuizModeFactory.createRandom(cards)
    adapt = QuizModeFactory.createAdaptive(cards)

    # Assert
    assert isinstance(seq, SequentialStrategy)
    assert isinstance(rand, RandomStrategy)
    assert isinstance(adapt, AdaptiveStrategy)

    # Security Vulnerabilities: None.


def test_quiz_mode_factory_create_mode_valid_strings():
    """Test QuizModeFactory.create_mode dynamically creates strategies."""
    # Arrange
    cards = [Card("F", "B")]

    # Act
    seq = QuizModeFactory.create_mode("sequential", cards)
    rand = QuizModeFactory.create_mode("random", cards)
    adapt = QuizModeFactory.create_mode("adaptive", cards)

    # Assert
    assert isinstance(seq, SequentialStrategy)
    assert isinstance(rand, RandomStrategy)
    assert isinstance(adapt, AdaptiveStrategy)

    # Security Vulnerabilities: None.


def test_quiz_mode_factory_invalid_mode_raises():
    """Test QuizModeFactory.create_mode raises ValueError on unknown mode."""
    # Arrange
    cards = [Card("F", "B")]

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid quiz mode"):
        QuizModeFactory.create_mode("unknown_mode", cards)

    # Security Vulnerabilities: None.
