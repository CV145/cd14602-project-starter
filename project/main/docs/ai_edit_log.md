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

---

## Your Log Entries

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

As you work through the project, consider these questions:

1. **What types of tasks did AI help with most effectively?**
2. **Where did you need to make the most modifications to AI suggestions?**
3. **What patterns did you notice in AI strengths and weaknesses?**
4. **How did your prompting technique improve over time?**
5. **What would you do differently in future AI collaborations?**

## Summary Statistics

At the end of your project, fill out these statistics:

- **Total AI interactions:** \_\_\_
- **Lines of AI-generated code used:** Every single line was AI-generated.
- **Lines of AI-generated code modified:** 0
- **Most helpful AI interaction:** Writing the spec.md together.
- **Most challenging AI interaction:** \_\_\_
- **Biggest lesson learned:** \_\_\_

---

**Note:** This log is a required component of your final project report. Be thorough and honest in your documentation to demonstrate your learning process and AI collaboration skills.
