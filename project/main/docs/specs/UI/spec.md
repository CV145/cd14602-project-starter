## Goal (What does success look like?)
Build two thin front-ends over the existing `QuizEngine`, each in its own file:

1. **`cli_frontend.py` (required for grading, kept minimal):** an argparse CLI started through `main.py` that meets every Phase 3 requirement in `instructions.md`. Success: `python main.py -m adaptive -f data/python_basics.json` plays a full game with green/red feedback. Typing `exit` or pressing Ctrl+C quits cleanly with no traceback. `--stats` prints lifetime accuracy and exits.
2. **`streamlit_frontend.py` (the main presentation):** a polished local web app started with `streamlit run streamlit_frontend.py`. Users pick or upload a deck, choose a mode, answer cards, and see live and lifetime stats. They can also see adaptive queue counts, set custom intervals, reset progress, and resume a session after a browser refresh.

Neither front-end contains quiz rules. A new UI-agnostic Facade, `utils/session_controller.py`, holds the rules both share: `exit`/`skip` commands, the adaptive 2-attempt flow, answer-versus-command collisions, deck resolution, and stats summaries. Rendering and input stay in the frontend files.

**Done when** the `instructions.md` Definition of Done is met: all tests pass (including `tests/test_integration.py::test_full_session`), coverage is above 80%, and `flake8` is clean.
## Constraints (What must the implementation respect?)

### 1. General
- Python 3.10+, PEP 8, and `flake8` clean. Every function is 40 lines or fewer, has a docstring, and ends with `Edge Cases:` / `Security Vulnerabilities:` comments.
- TDD (red → green → refactor), one function at a time. Tests use Arrange / Act / Assert.
- Single-threaded. Only one front-end runs at a time (see §9).
- New dependencies go in `requirements.txt`: `rich` (CLI colors and tables) and `streamlit` (web app).
- No raw Python tracebacks reach the user in either front-end. Every expected error becomes a friendly message.
- Design patterns: the existing **Strategy** + **Factory** stay unchanged in role. **Facade** (`SessionController`) is added.

### 2. Architecture and file layout
| File | Responsibility |
|---|---|
| `main.py` | Entry point only: `sys.exit(cli_frontend.main(sys.argv[1:]))`. |
| `cli_frontend.py` (project root) | argparse, `input()`, `rich` rendering. No quiz rules. `main(argv) -> int` returns the exit code. |
| `streamlit_frontend.py` (project root) | Streamlit widgets, `st.session_state`, rendering. No quiz rules. |
| `utils/session_controller.py` | UI-agnostic Facade over `QuizEngine` / `QuizModeFactory` / `load_flashcard_data`. It handles deck resolution, latest-deck lookup, command parsing, the attempt flow, collision handling, stats summaries, interval settings, and active-session save/restore. |
| `utils/quiz_engine.py` | Existing engine plus the changes listed in §8. |

Both front-ends call **only** `SessionController`. Neither imports strategies directly.

### 3. `quiz_state.json` schema (single shared file)
All decks live in one file. The default path is `data/quiz_state.json`.
```json
{
  "_active_session": { "...": "see §6.6" },
  "python_basics": {
    "_settings": { "intervals": { "5min": 300, "10min": 600, "15min": 900 } },
    "What is a list?": { "correct": 3, "incorrect": 1, "last_seen": 1791288000.0 }
  },
  "upload:my_deck.json": {
    "Term": { "correct": 1, "incorrect": 0, "last_seen": 1791289000.0 }
  }
}
```
- **Deck key:** the file stem for decks in `data/` (`data/python_basics.json` → `python_basics`). Uploaded decks use `upload:<sanitized basename>`.
- **Reserved keys:** exactly `_active_session` (top level) and `_settings` (inside a deck). Stats, accuracy, and latest-deck code always skip them. A deck that has a card whose front is exactly `_settings` is rejected at load time with a friendly error.
- **`last_seen`:** epoch seconds, written whenever a card's final outcome is recorded.
- A missing file is created silently as `{}`. A corrupt file is a startup error (§7).
- Duplicate card fronts within a deck share one stats entry. A yellow warning lists them at load time.

### 4. CLI (`cli_frontend.py`): minimal, rubric-compliant
**Flags**
| Flag | Rule |
|---|---|
| `-f`, `--file PATH` | Optional. Must end in `.json`, be an existing regular file, and be ≤ 1 MB. If omitted, the **latest deck** is used: the non-upload deck key holding the card with the greatest `last_seen`, resolved to `data/<key>.json`. If there is no history, error "No study history yet. Please provide a deck with -f." If the resolved file is gone, error naming the missing path. |
| `-m`, `--mode {sequential,random,adaptive}` | Optional. Defaults to `sequential`. Case-insensitive. |
| `--stats` | Prints lifetime stats **across all decks combined** (including `upload:` decks): total correct, total attempts, accuracy % (1 decimal), as a `rich` table. Then exits 0. `-f` and `-m` are ignored. With no history it prints "No study history yet" and exits 0. |
| `--state PATH` | Optional. Defaults to `data/quiz_state.json`. Must end in `.json`. Used by tests and by advanced users. |

**Per-card flow**
- Show the card front, then prompt for an answer. Grading is case-insensitive after trimming whitespace (existing `Card.check_answer`).
- **Sequential / random:** one attempt. A correct answer prints green `✔ Correct`. A wrong one prints red `✘ Incorrect: <answer>`.
- **Adaptive:** two attempts. The first miss prints red `✘ Incorrect, try again (1 attempt left)`. A miss on the second try prints red with the correct answer. Only the **final outcome** counts toward stats (one correct or one incorrect per card). The **fail count** (0 / 1 / 2) decides the queue: 15min / 10min / 5min.
- **Empty or whitespace-only input:** yellow "Please type an answer (or 'exit' / 'skip')". The same prompt repeats. No attempt is used and nothing is recorded.
- **`skip`** (case-insensitive, trimmed): reveals the answer in yellow and records 1 incorrect. In adaptive mode it counts as Difficult (fail count 2 → 5min queue).
- **`exit`** (case-insensitive, trimmed) or **Ctrl+C / Ctrl+D** at the answer prompt asks "Quit? (y/n)":
  - `y` quits gracefully.
  - `n` returns to the same card with the same attempt number.
  - Ctrl+C or Ctrl+D at the confirmation prompt quits immediately, still gracefully.
- **Command/answer collision:** if the card's answer is literally `exit` or `skip` and the user types it, the input is **graded first** and the green feedback is shown, but recording waits. The CLI then asks "Did you mean to quit?" or "Did you mean to skip?" (y/n). `y` drops the grade and runs the command. `n` records the correct answer.
- **Graceful quit:** state is already saved (it is persisted after every recorded outcome). A card mid-retry is **not** recorded. The CLI prints the end-of-session summary and exits 0.
- **End-of-session summary** (printed on every session end): session correct, incorrect, and accuracy %, plus the **current deck's lifetime accuracy %** (1 decimal).
- **Session end without quitting:** sequential and random run forever (cycling or reshuffling). Adaptive ends when no card is due. It prints `🎉 All caught up! Next review in <N min>`, then the summary, and exits 0.
- Card text is printed with Rich markup escaped (`rich.markup.escape`).
- The CLI ignores `_active_session` but must keep it intact when it saves.

### 5. CLI error handling
- **Every** error prints one friendly red line, with no traceback, and exits with code **1**. This includes argparse usage errors such as an invalid `-m`: override `ArgumentParser.error` so it exits 1 instead of 2.
- Errors covered:
  - missing, non-`.json`, non-regular, or oversized file
  - malformed JSON or missing/empty fields (existing loader messages)
  - an **empty deck** (the loader allows `[]`; the controller rejects it)
  - a `_settings` card front
  - no `-f` and no history
  - a resolved latest-deck file that has gone missing
  - a `--state` path that doesn't end in `.json`
  - a corrupt state file
- **Corrupt `quiz_state.json`:** refuse to start. The message names the file and the exact location from `JSONDecodeError`, for example: `quiz_state.json is corrupt: Expecting ',' delimiter at line 12, column 5. Fix or delete the file.` The file is never overwritten.
- **State write failure** (`OSError`): yellow warning "Progress could not be saved", and the session continues. No silent swallowing.

### 6. Streamlit (`streamlit_frontend.py`): main presentation
6.1 **Sidebar: deck and mode**
- A dropdown of every `*.json` in `data/` except the active state file, preselected to the latest deck.
- A file uploader (`.json` only, ≤ 1 MB, ≤ 1,000 cards), validated with the same loader and controller rules. Uploaded cards are kept in memory. Their stats persist under `upload:<sanitized basename>`, where sanitizing keeps only the basename and strips path separators.
- A mode dropdown (sequential / random / adaptive), defaulting to sequential.
- Changing deck or mode **mid-session** asks "End current session?". Confirming ends the session (stats are already saved) and starts a new one. Cancelling restores the previous selection.

6.2 **Card interaction**
- The card front appears in a styled card.
- A form holds a text input, a **Submit** button (Enter submits), and a **Skip** button.
- Feedback is `st.success` (green) or `st.error` (red), followed by a **Next card** button.
- Grading rules match the CLI (§4): adaptive gets 2 attempts, final outcome only, Skip = incorrect / Difficult.
- Typed text is **always graded as an answer**. Commands are buttons (Skip, End session), so collisions can't happen in Streamlit.
- Empty submissions show a warning and use no attempt.

6.3 **Sidebar: stats and controls**
- Live session scoreboard: correct, incorrect, accuracy %.
- Lifetime panel for the selected deck: accuracy %, plus a "weakest cards" table showing the top 5 by incorrect count (ties broken alphabetically by front).
- Adaptive queue view: card counts in new / 5min / 10min / 15min.
- **Custom intervals** (adaptive): one selector per queue with options 5 min, 10 min, 15 min, 30 min, 1 h, 24 h, 1 week. Defaults are 5/10/15 min. Values are saved to `<deck>._settings.intervals` and take effect at the **next** session start; mid-session changes show "applies after restart". The CLI reads the same saved values.
- **Reset progress** (with confirmation): deletes the selected deck's card stats, keeps `_settings`, and clears `_active_session` if it belongs to that deck.

6.4 **Session lifecycle**
- **End session** opens a summary screen (session stats plus the deck's lifetime stats) with a **Start new session** button.
- Adaptive "All caught up" shows a celebratory message with the next due time and the summary.

6.5 **State path**
- Always `data/quiz_state.json`, unless `st.session_state["state_path"]` is preset (used by `AppTest`).

6.6 **Resume after refresh**
- After every recorded outcome, the controller writes `_active_session`:
```json
{ "deck_key": "python_basics", "source": "data/python_basics.json",
  "cards": null, "mode": "adaptive", "session_correct": 2,
  "session_incorrect": 1, "current_front": "What is a list?",
  "attempt": 1, "queues": { "new": [], "5min": [], "10min": [], "15min": [] },
  "fails": {}, "timestamps": {} }
```
  - `cards` holds the full card list for uploaded decks (so they can always be resumed) and is `null` for `data/` decks.
  - `queues`, `fails`, and `timestamps` are filled in only for adaptive mode.
- On a fresh load with `_active_session` present, prompt "Resume session?" with **Resume** and **Discard**.
  - Sequential resumes at `current_front`.
  - Random resumes `current_front`, then reshuffles.
  - Adaptive restores the queues.
- If the source file is missing or `current_front` is no longer in the deck, discard it and show a yellow notice.
- `_active_session` is cleared on End session, Discard, Reset progress for that deck, or adaptive "All caught up".

6.7 **Errors and security**
- Every error appears as `st.error`, never as a traceback.
- A corrupt state file shows the same line/column message as the CLI and then calls `st.stop()`.
- Card text is never rendered with `unsafe_allow_html`. Static theme CSS is the only HTML allowed.

### 7. Edge cases and failure modes (both front-ends unless noted)
| Case | Behavior |
|---|---|
| State file missing | Created silently as `{}`. |
| State file corrupt | Refuse to start, with a file + line/column message. Never overwritten. |
| State write fails | Yellow warning, and the session continues. |
| Deck file missing / bad JSON / missing field / empty / >1 MB / non-`.json` | Friendly error. CLI exits 1, Streamlit shows `st.error`. |
| `-f` omitted, no history | CLI error, exit 1. |
| `-f` omitted, latest deck file deleted | CLI error naming the path, exit 1. |
| Only `upload:` decks in history | Treated as "no history" for latest-deck lookup. Still counted by `--stats`. |
| Duplicate fronts in a deck | Load with a yellow warning. Stats are shared. |
| Card front `_settings` | Deck rejected. |
| Answer is literally `exit` / `skip` (CLI) | Grade first, then confirm the intent. |
| Empty input | Re-prompt. No attempt used. |
| Quit mid-adaptive-retry | Card not recorded. |
| Ctrl+C at the quit confirmation | Immediate graceful quit. |
| Ctrl+D (EOF) at the answer prompt | Same as Ctrl+C. |
| Adaptive: no card due | "All caught up", next due time, summary. |
| Refresh mid-session (Streamlit) | "Resume session?" |
| Resume target gone | Discard, with a yellow notice. |
| Upload with path components in its name | Basename only is kept. |
| Card text containing Rich/HTML markup | Escaped / rendered as plain text. |

### 8. Required engine changes (must land first, TDD in `tests/test_quiz_engine.py`)
1. `QuizEngine._init_state`: on `JSONDecodeError`, raise a custom `StateFileError` carrying the path, line, and column instead of returning `{}`.
2. Grading without advancing: add `grade_current_card(answer) -> bool` (no side effects) and `record_result(is_correct: bool, fails: int)`. `record_result` updates final-outcome stats, writes `last_seen`, calls the strategy, saves, and advances. `answer_current_card` stays as a one-attempt wrapper.
3. `AdaptiveStrategy` takes the fail count (0 → 15min, 1 → 10min, 2 → 5min) instead of counting fails internally across calls.
4. `AdaptiveStrategy` due-time:
   - `get_next_card` returns only due cards. A card is due if it is new, or if its queue interval has elapsed since `last_seen`. Priority stays new → 5 → 10 → 15.
   - Add `seconds_until_next_due() -> float | None`.
5. `AdaptiveStrategy.to_dict()` / `from_dict()` for resume. Intervals load from `_settings`.
6. Stats helpers skip reserved keys. Add an all-decks lifetime accuracy helper for `--stats`.
7. `_save_state` raises (or returns a failure flag) on `OSError` instead of silently passing, so the front-ends can warn.

### 9. Concurrency
- Single-threaded, single local user. **Only one front-end runs at a time.** Running the CLI and Streamlit together, or opening multiple Streamlit tabs, is unsupported (last writer wins). This is documented in the README.
- No file locks and no merge-on-save.
- Streamlit reruns the script on every interaction, so all session objects (controller, engine, strategy) live in `st.session_state` and are never rebuilt on a rerun.

## Acceptance Criteria (How will you verify it’s done?)
**Definition of Done (`instructions.md`)**
- [ ] `python main.py -m adaptive -f data/python_basics.json` plays a full game, with green/red feedback and a graceful `exit` / Ctrl+C.
- [ ] `python -m pytest tests/` passes. `python -m pytest --cov=. --cov-report=html` shows **> 80%** coverage.
- [ ] `flake8` reports no errors.
- [ ] Strategy + Factory are still visible in `quiz_engine.py`. The Facade is in `session_controller.py`.

**`tests/test_integration.py`**
- [ ] `test_full_session`: calls `cli_frontend.main(["-m", "sequential", "-f", <tmp 3-card deck>, "--state", <tmp state>])` with scripted inputs: correct, wrong, correct, `exit`, `y`. It asserts that the printed summary shows **2 correct, 1 incorrect, 66.7%**, that the tmp state file holds matching per-card counts and `last_seen` values, and that the return code is 0.

**`tests/test_session_controller.py`** (unit)
- [ ] Latest-deck lookup: picks the greatest `last_seen`, ignores `upload:` and reserved keys, returns None with no history.
- [ ] Command parsing: `exit` / `skip` are case-insensitive and trimmed. Empty input is rejected.
- [ ] Adaptive attempt flow: right first time → fails 0; wrong then right → fails 1, 1 correct; wrong twice → fails 2, 1 incorrect; skip → fails 2, 1 incorrect.
- [ ] Collision: an answer of `exit` is graded correct, the result is held until confirmed, and both the y and n paths are covered.
- [ ] Rejects an empty deck, a `_settings` front, a non-`.json` path, and files over 1 MB. Warns on duplicate fronts.
- [ ] All-decks stats: correct / attempts / accuracy %, and no-history handling.
- [ ] Interval settings save/load, and the default is 5/10/15.
- [ ] `_active_session` save, restore, discard when the deck or card is gone, and resume of an uploaded deck from stored cards.
- [ ] Reset progress keeps `_settings` and clears a matching `_active_session`.

**`tests/test_cli_frontend.py`**
- [ ] Every error path returns 1 with a friendly message and no traceback, including an invalid `-m`.
- [ ] `--stats` prints the all-decks table and returns 0. With no history it prints "No study history yet" and returns 0.
- [ ] `-m` defaults to sequential. `-f` falls back to the latest deck.
- [ ] Ctrl+C (`KeyboardInterrupt`) and EOF at the answer prompt and at the confirmation prompt are handled. `n` returns to the same card.
- [ ] Quitting mid-retry records nothing for that card.
- [ ] The corrupt state message includes the line and column, and the file is unchanged afterwards.
- [ ] Output contains no color codes when captured (Rich detects non-TTY output).

**`tests/test_streamlit_frontend.py`** (`streamlit.testing.v1.AppTest`, state path preset in session state)
- [ ] Renders the deck list, which excludes the state file.
- [ ] Submit correct → success banner, and the scoreboard updates. Submit wrong → error banner.
- [ ] Adaptive: first miss shows the retry message. Skip records an incorrect answer.
- [ ] End session → summary screen. Start new session resets the session counts.
- [ ] Changing the deck mid-session asks for confirmation. Cancel reverts.
- [ ] Resume prompt appears when `_active_session` exists. Discard clears it.
- [ ] An invalid upload shows `st.error`. A valid upload persists stats under `upload:<name>`.
- [ ] Reset progress (confirmed) clears that deck's stats.
- [ ] A corrupt state file shows the error and stops.

**`tests/test_quiz_engine.py`**: new tests for every item in §8. Existing tests keep passing, or are updated with a note in `ai_edit_log.md`.

**Docs**: `README.md` gains CLI usage (all flags, commands, exit codes), the `streamlit run streamlit_frontend.py` instructions, and the one-front-end-at-a-time note.

## Out of Scope (What should the agent not touch?)
- Concurrent use (CLI + Streamlit together, or multiple browser tabs). No file locking or merge logic.
- User accounts, authentication, multi-user profiles.
- Cloud deployment or hosting. Local `streamlit run` only.
- Creating or editing decks in either UI.
- Fuzzy or partial answer matching. Only exact match after trim + case-fold.
- Internationalization / localization.
- Mobile-specific layout tuning beyond Streamlit defaults.
- Audio or images on cards.
- CLI resume of `_active_session`, and a CLI flag for custom intervals.
- Changing the Phase 1 loader's accepted JSON formats, or the Strategy/Factory class structure, beyond the changes listed in Constraints §8.