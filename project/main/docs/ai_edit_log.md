# AI Edit Log

**Instructions:** Use this document to track all your interactions with AI assistants during the project. This log will help you reflect on your AI collaboration process and demonstrate your learning journey.

## How to Use This Log

For each AI interaction, create a new entry with the following structure:

### Entry Template

```
## [Date] - [Brief Description]

**Context:** What were you trying to accomplish?
**AI Tool Used:** Claude/ChatGPT/Copilot/etc.
**Prompt/Request:** What exactly did you ask the AI?
**AI Response:** Summary of what the AI generated (don't copy entire code blocks)
**Changes Made:** What modifications did you make to the AI's suggestions?
**Reasoning:** Why did you make those changes?
**Outcome:** What was the final result?
**Lessons Learned:** What did you learn from this interaction?
```

---

### 2026-10-5 - Building a spec.md for loading_data

Context: Following new practices outlined in the upcoming book 'AI-Native Software Engineering', I requested a specification file outlining exactly what needs to be built for loading data
AI Tool Used: Gemma 3 4b
Prompt: I need help building a spec.md for the first step: building a system to load and validate flashcard data. Please begin the interview and tell me where in the project workspace I should store spec.md
AI Response: Through a few back and forth interactions, we built the file docs/specs/loading_data/spec.md
Changes Made: Any ambiguities outlined by Gemini 3.8 Flash
Reasoning: Gemma 3 was a smaller local model that didn't have full context of the project workspace
Outcome: The final specification in spec.md
Lessons Learned: Local AI is helpful but doesn't have a context window large enough to identify inconsistencies

### 2026-10-05 - Implementing Data Loading & Validation with TDD and Strict Function Limits

**Context:** Implementing the flashcard loading, normalization, and validation feature (`load_flashcard_data`) and associated unit tests per `tasks.md` and `spec.md`.

**AI Tool Used:** Gemini 3.8 Flash

**Prompt/Request:** Read spec.md, plan.md, and tasks.md carefully before starting.

Implement every task in tasks.md, respecting the dependencies you find in the file. For each task: implement the change, verify the done check is met, and mark the task complete in tasks.md.

Where two tasks are independent of each other, dispatch them to separate subagents.

Do not modify spec.md or plan.md. If you hit a blocker you cannot resolve, stop and report what you tried.

As you implement each task, maintain an implementation_notes.md file in the project directory. Record: any unexpected behavior you encountered in the existing code, decisions you made that weren’t covered by the plan, assumptions you’re working under, and anything that surprised you or that a future reader might find nonobvious. Keep each entry short, a sentence or two, with a timestamp or task reference.

**AI Response:** Generated unit test cases first (valid arrays/objects, bad syntax, missing keys, invalid types), implemented `load_flashcard_data`, and then refactored it from 54 lines down to 35 lines while preserving all validation logic and passing all 20 tests.

**Changes Made:** Required tests to be written first one at a time, simplified regex error matching in tests to readable string matches, and mandated refactoring to keep the function under 40 lines.

**Reasoning:** Incremental TDD with human approval prevents runaway code generation and hallucinated edge cases. Enforcing a strict 40-line limit guarantees maintainability, readability, and modular design.

**Outcome:** Successfully built a compact 35-line `load_flashcard_data` function that normalizes formats, validates inputs, documents security considerations, and passes the entire 20-test test suite with 0 failures.

**Lessons Learned:** Setting strict constraints (TDD cadence, <40 line limits, and review checkpoints) keeps AI-generated code concise, clean, and bug-free instead of sprawling and hard to maintain.

---

### 2026-10-06 - Implementing Quiz Engine with Strategy & Factory Patterns

**Context:** Implementing the core quiz engine architecture (`Card`, `QuizMode` ABC, `SequentialStrategy`, `RandomStrategy`, `AdaptiveStrategy`, `QuizModeFactory`, and `QuizEngine`) and accompanying unit test suites per `spec.md`, `plan.md`, and `tasks.md`.

**AI Tool Used:** Gemini 3.8 Flash

**Prompt/Request:** Read spec.md, plan.md, and tasks.md in quiz_engine directory carefully before starting. Implement every task in tasks.md, respecting the dependencies you find in the file. For each task: implement the change, verify the done check is met, and mark the task complete in tasks.md. Where two tasks are independent of each other, dispatch them to separate subagents. Do not modify spec.md or plan.md. If you hit a blocker you cannot resolve, stop and report what you tried.

**AI Response:** Incrementally generated unit tests and classes across Tasks 0-10, presenting one function at a time for review and verification before applying changes.

**Changes Made:** Rejected overloaded test functions that tested too many behaviors at once and made the AI split them into independent, single-responsibility tests (e.g., separating priority order, attempt transitions, time decay, and factory dispatch). Also instructed the AI to identify and document edge cases in addition to security vulnerabilities at the end of each function.

**Reasoning:** Testing multiple assertions in one function makes it harder to diagnose what broke. Enforcing single-responsibility unit tests keeps test failures clear and isolated, and requiring explicit edge-case analysis guarantees robust input handling and division-by-zero prevention.

**Outcome:** Successfully implemented the full quiz engine in `utils/quiz_engine.py` and comprehensive test suites in `tests/test_quiz_modes.py` and `tests/test_quiz_engine.py`. Achieved 87% code coverage on `quiz_engine.py`, passed all 35 tests across the project, zero flake8 lint warnings, and strictly kept every function under 40 lines.

**Lessons Learned:** Actively steering the AI to keep tests focused and granular prevents bloated test suites. Enforcing a strict one-function review cycle with edge-case checks ensures the code stays maintainable and well-tested.


---

### 2026-10-06 - Drafting UI Feature Specification (CLI & Streamlit)

**Context:** Designing and drafting `docs/specs/UI/spec.md` to cover both a minimal rubric-compliant CLI (`cli_frontend.py`) and a polished Streamlit web application (`streamlit_frontend.py`).

**AI Tool Used:** Claude 5.5 Opus / Antigravity Agent

**Prompt/Request:** I want to build the CLI user interface for the application. But I also want to include a streamlit web app as well.

Before writing anything, ask me as many questions as you need to write a complete spec.md: goal, context, constraints, acceptance criteria, and non-goals. Cover trade-offs, edge cases, failure modes, and concurrency where relevant. Do not write the spec until I tell you to. Ask me one question at a time.

When I am done answering, draft the spec.md in the standard format.

**AI Response:** Conducted a comprehensive, 39-question interactive interview covering front-end relationships, execution flags, adaptive 2-attempt flow, input validation, skip/exit command handling, corrupt state error reporting, Streamlit session persistence across refreshes, custom intervals, Facade architecture (`session_controller.py`), testing strategy, and explicit non-goals. Drafted the complete `spec.md` once instructed.

**Changes Made:** Explicitly specified command collision semantics (grading typed `exit`/`skip` as answers first before asking if command intent was meant), required strict refusal to start on corrupt `quiz_state.json` with line/column details, defined state persistence for uploaded decks in Streamlit, and architected a shared `SessionController` Facade so neither frontend contains core quiz logic.

**Reasoning:** Asking detailed questions one at a time before drafting prevented unwarranted assumptions about user interaction models and edge case behaviors. Structuring shared logic into a Facade enforces clean architecture and keeps both UI layers thin and maintainable.

**Outcome:** Successfully generated a thorough, comprehensive `spec.md` in `docs/specs/UI/` outlining goals, constraints, file architecture, `quiz_state.json` schema updates, failure modes, edge cases, acceptance criteria, and explicit non-goals.

**Lessons Learned:** Using an interactive Q&A discovery workflow before generating specifications ensures all edge cases (concurrency, session recovery, reserved keys, command collisions) are explicitly agreed upon before any code is written.

---

### 2026-10-06 - Generating Task Breakdown for Streamlit Frontend Bug Fix

**Context:** Translating the bug fix plan ([`plan.md`](file:///Users/carlosvaleriano/Desktop/Upwork%20Portfolio/flashcard_quizzer/cd14602-project-starter/project/main/docs/specs/bug_fixes/streamlit_frontend/plan.md)) for card advance desynchronization and session resumption loops into an actionable, TDD-sequenced [`tasks.md`](file:///Users/carlosvaleriano/Desktop/Upwork%20Portfolio/flashcard_quizzer/cd14602-project-starter/project/main/docs/specs/bug_fixes/streamlit_frontend/tasks.md).

**AI Tool Used:** Gemini 3.8 Flash / Antigravity Agent

**Prompt/Request:** Read spec.md and generate a tasks.md. Break the work into tasks where each task: (1) corresponds to a specific, named change, (2) has an explicit done check that can be verified without reading the full plan, and (3) is ordered so that no task depends on one listed after it.

**AI Response:** Generated an 8-task breakdown in [`tasks.md`](file:///Users/carlosvaleriano/Desktop/Upwork%20Portfolio/flashcard_quizzer/cd14602-project-starter/project/main/docs/specs/bug_fixes/streamlit_frontend/tasks.md) following TDD sequencing: authoring failing UI tests with `AppTest`, implementing controller caching (`_get_or_create_controller`), guarding session resume prompts, persisting submission feedback across reruns, updating card panel rendering with `clear_on_submit`, resetting state on deck progress reset, and running verification.

**Changes Made:** Structured each task with self-contained, verifiable done checks that do not require reading the plan, ordered tasks topologically by dependency, and linked file paths and symbols with clickable markdown links.

**Reasoning:** Formulating explicit, testable done checks and isolating state management tasks ensures implementation can proceed incrementally via red-green-refactor without regressions.

**Outcome:** Created [`docs/specs/bug_fixes/streamlit_frontend/tasks.md`](file:///Users/carlosvaleriano/Desktop/Upwork%20Portfolio/flashcard_quizzer/cd14602-project-starter/project/main/docs/specs/bug_fixes/streamlit_frontend/tasks.md) containing 8 clearly sequenced tasks ready for TDD execution.

**Lessons Learned:** Defining clear done checks with exact assertion targets and CLI commands makes test-driven bug fixes straightforward to implement and verify step-by-step.

---

## Tips for Effective AI Collaboration

### 1. Be Specific in Your Requests

- ❌ "Write a function"
- ✅ "Write a function that validates email addresses using regex, returns a boolean, and includes proper error handling"

### 2. Provide Context

- Include relevant code snippets
- Explain the larger goal
- Mention any constraints or requirements

### 3. Review and Understand

- Never copy AI code without understanding it
- Ask for explanations of complex logic
- Test the code before accepting it

### 4. Iterate and Refine

- Use follow-up questions to improve the code
- Ask for alternative implementations
- Request code reviews and suggestions

### 5. Document Your Process

- Keep detailed notes in this log
- Explain your decision-making process
- Track what works and what doesn't

## Common AI Collaboration Patterns

### Code Generation

- Initial implementation of classes/functions
- Boilerplate code creation
- Test case generation

### Code Review

- Ask AI to review your code for issues
- Request suggestions for improvements
- Get feedback on code structure

### Problem Solving

- Debugging help
- Algorithm suggestions
- Architecture advice

### Learning and Explanation

- Ask for explanations of complex concepts
- Request examples of design patterns
- Get guidance on best practices

## Reflection Questions

1. **What types of tasks did AI help with most effectively?**  
   AI excelled at rapid test suite generation, domain model scaffolding (`Card`, `InputResult`), structuring design pattern boilerplate (Strategy, Factory, and Facade), and conducting interactive requirement discovery interviews to build thorough specification documents (`spec.md`).

2. **Where did you need to make the most modifications to AI suggestions?**  
   Modifications were most critical when AI generated overloaded test functions with multiple assertions, attempted overly lengthy functions exceeding 40 lines, or struggled with state persistence subtleties. Human steering was vital to enforce single-responsibility tests and tight function length limits.

3. **What patterns did you notice in AI strengths and weaknesses?**  
   *Strengths:* High velocity with standard patterns, extensive edge-case brainstorming for unit tests, and comprehensive markdown documentation.  
   *Weaknesses:* Complex reactive state management (such as Streamlit's script rerun cycles), cross-module type coherence, and a tendency toward verbose implementations unless explicitly restricted.

4. **How did your prompting technique improve over time?**  
   Shifted from conversational, open-ended prompts to strict contract-driven instructions: specifying upfront acceptance criteria, mandating a red-green-refactor TDD cadence, enforcing <40-line limits, and establishing single-function review gates.

5. **What would you do differently in future AI collaborations?**  
   Begin every subsystem with a structured specification and task breakdown (`spec.md` and `tasks.md`) prior to any code generation, and integrate strict automated type checking (`mypy`, `flake8`) from the initial commit.

## Summary Statistics

At the end of your project, fill out these statistics:

- **Total AI interactions:** 45+
- **Lines of AI-generated code used:** ~1,850 lines (across engine, controllers, frontends, and tests)
- **Lines of AI-generated code modified:** ~350 lines modified/refactored through code review and linting
- **Most helpful AI interaction:** Interactive discovery interview and specification drafting for `docs/specs/UI/spec.md`
- **Most challenging AI interaction:** Debugging Streamlit rerun lifecycle and session state persistence loops
- **Biggest lesson learned:** Enforcing strict constraints upfront (TDD red-green-refactor cadence, <40 line function limits, and single-function review cycles) prevents code sprawl and ensures high maintainability.

---

**Note:** This log is a required component of your final project report. Be thorough and honest in your documentation to demonstrate your learning process and AI collaboration skills.
