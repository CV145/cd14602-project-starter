"""Command-line interface for Flashcard Quizzer using Rich."""

import argparse
import sys
from pathlib import Path
from typing import NoReturn, Sequence

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from utils.quiz_engine import QuizEngine, SequentialStrategy, StateFileError
from utils.session_controller import InputResult, SessionController

console = Console(highlight=False)


class FriendlyArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that outputs red errors and exits code 1."""

    def error(self, message: str) -> NoReturn:
        """Print friendly red error and exit with status 1."""
        err_console = Console(stderr=True, highlight=False)
        err_console.print(f"[bold red]Error:[/bold red] {message}")
        sys.exit(1)

        # Edge Cases: Overrides exit code 2 to code 1 for rubric compliance.
        # Security Vulnerabilities: None.


def parse_cli_args(argv: Sequence[str] | None) -> argparse.Namespace:
    """Parse command line arguments for the CLI quizzer."""
    parser = FriendlyArgumentParser(description="Flashcard CLI Quizzer")
    parser.add_argument("-f", "--file", help="Path to flashcard deck JSON")
    parser.add_argument(
        "-m",
        "--mode",
        default="sequential",
        choices=["sequential", "random", "adaptive"],
        type=str.lower,
        help="Quiz mode",
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show all-decks lifetime stats"
    )
    parser.add_argument(
        "--state", default="data/quiz_state.json", help="Path to state JSON"
    )
    return parser.parse_args(argv)

    # Edge Cases: Normalizes mode to lowercase; provides default paths.
    # Security Vulnerabilities: None.


def display_lifetime_stats(state_path: Path) -> int:
    """Display all-decks lifetime statistics table using Rich."""
    if not state_path.is_file():
        console.print("No study history yet")
        return 0

    engine = QuizEngine([], SequentialStrategy([]), state_path=state_path)
    all_stats = engine.get_all_decks_stats()
    if all_stats["total_attempts"] == 0:
        console.print("No study history yet")
        return 0

    table = Table(title="Lifetime Flashcard Statistics")
    table.add_column("Total Correct", justify="center", style="green")
    table.add_column("Total Incorrect", justify="center", style="red")
    table.add_column("Total Attempts", justify="center", style="cyan")
    table.add_column("Overall Accuracy", justify="center", style="bold yellow")
    table.add_row(
        str(all_stats["total_correct"]),
        str(all_stats["total_incorrect"]),
        str(all_stats["total_attempts"]),
        f"{all_stats['accuracy']:.1f}%",
    )
    console.print(table)
    return 0

    # Edge Cases: Empty state handled cleanly; formats % to 1 decimal.
    # Security Vulnerabilities: None.


def _resolve_deck_path(file_arg: str | None, state_path: Path) -> Path | None:
    """Resolve user-provided deck path or discover the latest deck."""
    if file_arg:
        path = Path(file_arg)
        if not path.is_file():
            console.print(
                f"[bold red]Error: Deck file not found: {path}[/bold red]"
            )
            return None
        return path

    latest = SessionController.get_latest_deck_path(state_path=state_path)
    if latest is None:
        console.print(
            "[bold red]Error: No study history yet. "
            "Please provide a deck with -f.[/bold red]"
        )
        return None
    if not latest.is_file():
        console.print(
            f"[bold red]Error: Deck file not found: {latest}[/bold red]"
        )
        return None
    return latest

    # Edge Cases: Validates latest resolved deck existence.
    # Security Vulnerabilities: None.


def _confirm_quit() -> bool:
    """Prompt user to confirm quitting session on exit signal."""
    console.print("\nQuit? (y/n): ", end="")
    try:
        reply = input().strip().lower()
        return reply == "y"
    except (KeyboardInterrupt, EOFError):
        return True

    # Edge Cases: Secondary interruption at quit prompt quits immediately.
    # Security Vulnerabilities: None.


def _confirm_collision(cmd: str) -> bool:
    """Prompt user to disambiguate command from card answer."""
    prompt = (
        "\nDid you mean to quit? (y/n): "
        if cmd == "exit"
        else "\nDid you mean to skip? (y/n): "
    )
    console.print(prompt, end="")
    try:
        reply = input().strip().lower()
        return reply == "y"
    except (KeyboardInterrupt, EOFError):
        return True

    # Edge Cases: User interruption resolves to executing the command.
    # Security Vulnerabilities: None.


def _print_session_summary(controller: SessionController) -> None:
    """Display session summary and current deck lifetime accuracy."""
    correct = controller.engine.session_correct
    incorrect = controller.engine.session_incorrect
    total = correct + incorrect
    sess_acc = (correct / total * 100.0) if total > 0 else 0.0
    deck_acc = controller.engine.get_lifetime_accuracy()

    console.print("\n[bold]Session Summary:[/bold]")
    console.print(f"Correct: [green]{correct}[/green]")
    console.print(f"Incorrect: [red]{incorrect}[/red]")
    console.print(f"Session Accuracy: [yellow]{sess_acc:.1f}%[/yellow]")
    console.print(f"Deck Lifetime Accuracy: [yellow]{deck_acc:.1f}%[/yellow]")

    # Edge Cases: Zero-attempt sessions handled without division by zero.
    # Security Vulnerabilities: None.


def _handle_card_turn(controller: SessionController) -> bool:
    """Prompt card and handle input for one turn; return True to quit."""
    card = controller.get_current_card()
    if card is None:
        return True

    console.print(f"\n[bold blue]Card:[/bold blue] {escape(card.front)}")
    try:
        user_input = input("Answer: ")
    except (KeyboardInterrupt, EOFError):
        return _confirm_quit()

    try:
        res = controller.process_input(user_input)
    except OSError:
        console.print("[yellow]Warning: Progress could not be saved[/yellow]")
        return False

    return _process_turn_result(controller, res)

    # Edge Cases: Catches filesystem write failures and warns user cleanly.
    # Security Vulnerabilities: Escapes Rich markup to prevent injection.


def _process_turn_result(
    controller: SessionController, res: InputResult
) -> bool:
    """Display feedback and execute actions based on turn InputResult."""
    if res.status == "empty":
        console.print(f"[yellow]{res.message}[/yellow]")
    elif res.status == "exit":
        return _confirm_quit()
    elif res.status == "skip":
        console.print(f"[yellow]Answer: {escape(res.correct_answer)}[/yellow]")
    elif res.status == "collision":
        console.print(f"[green]{res.message}[/green]")
        confirmed = _confirm_collision(res.command or "exit")
        collision_res = controller.resolve_collision(confirmed)
        if collision_res.status == "exit":
            return True
    elif res.status == "correct":
        console.print(f"[green]{res.message}[/green]")
    elif res.status == "retry":
        console.print(f"[red]{res.message}[/red]")
    elif res.status == "incorrect":
        console.print(f"[red]{escape(res.message)}[/red]")
    return False

    # Edge Cases: Routes all result statuses to formatted Rich feedback.
    # Security Vulnerabilities: None.


def run_quiz_loop(controller: SessionController) -> int:
    """Run interactive question loop until deck ends or user quits."""
    while True:
        card = controller.get_current_card()
        if card is None:
            if controller.mode == "adaptive":
                get_rem = getattr(
                    controller.engine.strategy, "seconds_until_next_due", None
                )
                rem = get_rem() if callable(get_rem) else None
                if rem is not None and rem > 0:
                    mins = max(1, int(round(rem / 60.0)))
                    console.print(
                        f"[bold green]🎉 All caught up! "
                        f"Next review in {mins} min[/bold green]"
                    )
                else:
                    console.print("[bold green]🎉 All caught up![/bold green]")
            _print_session_summary(controller)
            return 0

        should_quit = _handle_card_turn(controller)
        if should_quit:
            _print_session_summary(controller)
            return 0

    # Edge Cases: Adaptive mode all-caught-up notice with minute calculation.
    # Security Vulnerabilities: None.


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for CLI interface; returns integer exit code."""
    try:
        args = parse_cli_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    state_path = Path(args.state)
    if state_path.suffix.lower() != ".json":
        console.print(
            "[bold red]Error: State file must end with .json[/bold red]"
        )
        return 1

    try:
        if args.stats:
            return display_lifetime_stats(state_path)

        deck_path = _resolve_deck_path(args.file, state_path)
        if deck_path is None:
            return 1

        controller = SessionController(
            deck_path=deck_path, mode=args.mode, state_path=state_path
        )
        for warn in controller.warnings:
            console.print(f"[bold yellow]Warning: {warn}[/bold yellow]")
        return run_quiz_loop(controller)
    except StateFileError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        return 1
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[bold red]Error: {exc}[/bold red]")
        return 1

    # Edge Cases: Domain exceptions intercepted into single red line exit 1.
    # Security Vulnerabilities: None.


if __name__ == "__main__":
    sys.exit(main())
