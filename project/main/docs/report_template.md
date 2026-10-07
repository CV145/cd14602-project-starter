# AI-Assisted Development Project Report

**Student Name:** Carlos Valeriano  
**Project Title:** CLI Flashcard Quizzer  
**Date:** 10/7/2026

## Executive Summary

Provide a brief overview of your project (2-3 paragraphs):
- What application did you build?
I built the CLI Flashcard Quizzer, an application designed to reinforce learning through active recall and flexible practice modes. It was built with Python and the project offers both a CLI and web app experience. The application parses and validates modular JSON flashcard decks.
- What were the main features and functionality?
The application features a data engine that validates, sanitizes, and normalizes question decks across different JSON schemas. Users can select from 3 different quiz modes using the Strategy pattern: Sequential, Random, and Adaptive. During a session, the engine delivers immediate answer evaluation and explanations which culminate in a lifetime score summary.
- How did you collaborate with AI throughout the development process?
I used spec-driven development and TDD. Instead of having AI generate monolithic blocks of code I used a human in the loop workflow: First I drafted the architectural specifications in a spec.md, then I asked AI to create an implementation plan with plan.md and then break that plan down into atomic tasks (tasks.md). The tasks had to be paired with red-green0refactor unit tests before implementation. Every function was kept below 40 lines to make them short and readable, while checking each one for edge cases and security vulnerabilities.

## Project Overview

### Problem Statement
The CLI Flashcard Quizzer is built to help reinforce memory retention through active recall and targeted repetition. 

### Solution Approach
To solve this, I designed a modular, decoupled architecture centered around three core layers: a robust file handling and validation engine (`file_handler.py`), a flexible card-selection engine using the Strategy Pattern (`quiz_engine.py` with Sequential, Random, and Adaptive strategies), and a session state coordinator (`session_controller.py`). This decoupled business logic supports both a CLI frontend (`cli_frontend.py`) and an interactive web frontend (`streamlit_frontend.py`). The technology stack utilizes Python 3.10+, pytest for strict test-driven development, and Streamlit for rapid web UI prototyping.


### Final Features
List the features you implemented:
- [x] Robust JSON flashcard deck loading, validation, and normalization across multiple schema formats
- [x] Pluggable Quiz Engine with Strategy Pattern (Sequential, Random, and Adaptive weighted review)
- [x] Interactive quiz session controller with immediate answer evaluation, hints, and session summary metrics
- [x] Dual-interface support featuring both a terminal-based CLI and a modern Streamlit web frontend


## AI Collaboration Experience

### AI Tools Used
List the AI tools/assistants you worked with:
- [ ] Claude
- [ ] GitHub Copilot
- [ ] ChatGPT
- [X] Other: Gemini 3.8 Flash and Gemma 3 4b

### Collaboration Workflow
My workflow followed a disciplined spec-driven development cycle. First, I structured requests by providing explicit architectural boundaries, utilizing `spec.md` for high-level design and diagrams, followed by `plan.md` and atomic `tasks.md` breakdowns rather than open-ended coding prompts. I tasked the AI with drafting test suites first (TDD Arrange-Act-Assert pattern) and implementing modular functions strictly capped at under 40 lines. To review and validate generated code, I executed automated pytest suites after every change and inspected functions individually for edge case handling and security vulnerabilities. When suggestions were too verbose or introduced regressions, I guided the AI through red-green refactoring to distill logic into readable, single-responsibility functions.


### Most Valuable AI Interactions

### Example 1 - Implementing Data Loading & Validation with TDD and Strict Function Limits

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

### Example 2 - Implementing Quiz Engine with Strategy & Factory Patterns

**Context:** Implementing the core quiz engine architecture (`Card`, `QuizMode` ABC, `SequentialStrategy`, `RandomStrategy`, `AdaptiveStrategy`, `QuizModeFactory`, and `QuizEngine`) and accompanying unit test suites per `spec.md`, `plan.md`, and `tasks.md`.

**AI Tool Used:** Gemini 3.8 Flash

**Prompt/Request:** Read spec.md, plan.md, and tasks.md in quiz_engine directory carefully before starting. Implement every task in tasks.md, respecting the dependencies you find in the file. For each task: implement the change, verify the done check is met, and mark the task complete in tasks.md. Where two tasks are independent of each other, dispatch them to separate subagents. Do not modify spec.md or plan.md. If you hit a blocker you cannot resolve, stop and report what you tried.

**AI Response:** Incrementally generated unit tests and classes across Tasks 0-10, presenting one function at a time for review and verification before applying changes.

**Changes Made:** Rejected overloaded test functions that tested too many behaviors at once and made the AI split them into independent, single-responsibility tests (e.g., separating priority order, attempt transitions, time decay, and factory dispatch). Also instructed the AI to identify and document edge cases in addition to security vulnerabilities at the end of each function.

**Reasoning:** Testing multiple assertions in one function makes it harder to diagnose what broke. Enforcing single-responsibility unit tests keeps test failures clear and isolated, and requiring explicit edge-case analysis guarantees robust input handling and division-by-zero prevention.

**Outcome:** Successfully implemented the full quiz engine in `utils/quiz_engine.py` and comprehensive test suites in `tests/test_quiz_modes.py` and `tests/test_quiz_engine.py`. Achieved 87% code coverage on `quiz_engine.py`, passed all 35 tests across the project, zero flake8 lint warnings, and strictly kept every function under 40 lines.

### Example 3 - Drafting UI Feature Specification (CLI & Streamlit)

**Context:** Designing and drafting `docs/specs/UI/spec.md` to cover both a minimal rubric-compliant CLI (`cli_frontend.py`) and a polished Streamlit web application (`streamlit_frontend.py`).

**AI Tool Used:** Claude 5.5 Opus / Antigravity Agent

**Prompt/Request:** I want to build the CLI user interface for the application. But I also want to include a streamlit web app as well.

Before writing anything, ask me as many questions as you need to write a complete spec.md: goal, context, constraints, acceptance criteria, and non-goals. Cover trade-offs, edge cases, failure modes, and concurrency where relevant. Do not write the spec until I tell you to. Ask me one question at a time.

When I am done answering, draft the spec.md in the standard format.

**AI Response:** Conducted a comprehensive, 39-question interactive interview covering front-end relationships, execution flags, adaptive 2-attempt flow, input validation, skip/exit command handling, corrupt state error reporting, Streamlit session persistence across refreshes, custom intervals, Facade architecture (`session_controller.py`), testing strategy, and explicit non-goals. Drafted the complete `spec.md` once instructed.

**Changes Made:** Explicitly specified command collision semantics (grading typed `exit`/`skip` as answers first before asking if command intent was meant), required strict refusal to start on corrupt `quiz_state.json` with line/column details, defined state persistence for uploaded decks in Streamlit, and architected a shared `SessionController` Facade so neither frontend contains core quiz logic.

**Reasoning:** Asking detailed questions one at a time before drafting prevented unwarranted assumptions about user interaction models and edge case behaviors. Structuring shared logic into a Facade enforces clean architecture and keeps both UI layers thin and maintainable.

**Outcome:** Successfully generated a thorough, comprehensive `spec.md` in `docs/specs/UI/` outlining goals, constraints, file architecture, `quiz_state.json` schema updates, failure modes, edge cases, acceptance criteria, and explicit non-goals.

### Challenges with AI Collaboration
The primary challenges centered around stateful lifecycle management and code conciseness. AI models frequently struggled with subtle UI state synchronization—such as managing Streamlit's reactive rerun model when advancing cards and resuming saved sessions—which caused state loops until resolved with targeted tests. Additionally, the AI tended to generate sprawling functions exceeding 50 lines and multi-assertion test blocks that coupled disparate behaviors. I had to intervene frequently to enforce strict single-responsibility tests and refactor code to adhere to the 40-line ceiling. A distinct pattern emerged: AI excels at generating boilerplate, scaffolding design patterns, and proposing type-hinted interfaces, but struggles with nuanced state machine edge cases and localized architectural context without strict human-in-the-loop constraints.


## Software Engineering Practices

### Code Quality Measures
Document the practices you implemented:
- [X] Code formatting (Black, isort)
- [X] Linting (flake8, mypy)
- [X] Type hints
- [X] Documentation/comments
- [X] Error handling

### Testing Strategy
I followed a strict Test-Driven Development (TDD) methodology adhering to the Arrange-Act-Assert pattern. Across the project, I implemented 95 automated tests spanning unit tests (validating JSON schemas, parsing edge cases, and quiz strategy algorithms), integration tests (validating end-to-end session state persistence), and UI tests (leveraging Streamlit's `AppTest` framework and CLI mock inputs). Code reliability was ensured through red-green-refactor cycles, asserting exact error messages, and guarding against edge cases like empty datasets or state corruption. In total, the test suite achieved 89% code coverage across the entire codebase, with core modules like `quiz_engine` and `session_controller` exceeding 90% coverage.


### Design Patterns Used
- **Strategy Pattern:** Implemented in `utils/quiz_engine.py` through the abstract base class `QuizMode` and concrete strategies (`SequentialStrategy`, `RandomStrategy`, and `AdaptiveStrategy`). This allows switching the card-ordering algorithm at runtime without coupling the client or session state to a specific traversal mechanism.
- **Factory Pattern:** Implemented in `utils/quiz_engine.py` via `QuizModeFactory.create()`. It centralizes and encapsulates strategy instantiation from user input flags or configuration strings, promoting the Open/Closed Principle.
- **Facade Pattern:** Implemented in `utils/session_controller.py` via `SessionController`. It provides a clean, unified high-level interface over file loading, strategy execution, answer evaluation, and JSON persistence, preventing both the CLI and Streamlit frontends from directly managing low-level quiz mechanics.


### Code Structure and Organization
The codebase is structured around a strict separation of concerns into distinct layers:
1. **Data Ingestion & Validation (`file_handler.py`):** Responsible solely for I/O operations, format normalization across varying JSON schemas, and data integrity checks.
2. **Domain Logic & Algorithms (`quiz_engine.py`):** Encapsulates the core `Card` domain entity and modular selection algorithms isolated from I/O.
3. **Session Coordination (`session_controller.py`):** Acts as an intermediary Facade managing session lifecycle, progress tracking, scoring, and persistence.
4. **Presentation Layer (`cli_frontend.py` & `streamlit_frontend.py`):** Lightweight frontends that consume the `SessionController` API without implementing business or scoring logic.

During development, major refactorings included decomposing a 54-line data loader down to a modular 35-line pipeline, and decoupling stateful card advancement logic from Streamlit rendering loops to eliminate session reset bugs.


## Technical Challenges and Solutions

### Challenge 1: Streamlit State Desynchronization and Card Advance Loops
**Problem:** Streamlit executes the entire script top-to-bottom on every user interaction. When submitting card answers, the widget state conflicted with session resumption prompts, causing cards to fail to advance cleanly or triggering infinite re-prompt loops.
**Solution:** Refactored the frontend lifecycle by caching the controller instance via `_get_or_create_controller`, decoupling answer submission from UI rendering, and leveraging form inputs with `clear_on_submit` while persisting evaluation feedback explicitly in `st.session_state`.
**AI Involvement:** Paired with AI to draft a dedicated bugfix specification, generate an 8-task TDD roadmap in `tasks.md`, author failing UI tests using `streamlit.testing.v1.AppTest`, and verify each state transition incrementally.
**Lessons Learned:** Reactive UI frameworks require strict isolation between ephemeral widget input state and persistent domain models. Writing automated UI regression tests with `AppTest` is essential to prevent rerun race conditions.


### Challenge 2: Inconsistent Flashcard JSON Schemas and Schema Normalization
**Problem:** User-supplied flashcard decks varied widely in structure—some arrived as raw top-level JSON arrays while others were wrapped in root objects with nested metadata keys, and many contained missing fields, invalid types, or corrupt JSON syntax.
**Solution:** Built a resilient ingestion and normalization pipeline in `file_handler.py` that validates file integrity, dynamically normalizes both top-level lists and nested object schemas into uniform `Card` objects, and raises clear, contextual exceptions for invalid payloads.
**AI Involvement:** Collaborated with AI using strict TDD, authoring 20 negative and positive test fixtures (handling missing keys, malformed syntax, and boundary conditions) before drafting the function, and guiding the AI through refactoring the parser down from 54 to 35 lines.
**Lessons Learned:** Validating and normalizing disparate data formats at the architectural boundary shields downstream business logic from unexpected exceptions and guarantees system predictability.


## Code Quality Analysis

### Metrics
Provide quantitative measures of your code quality:
- Lines of code: 1,716 lines (application source)
- Test coverage: 89% (95 passing tests across unit, integration, and UI test suites)
- Number of functions/classes: 91 functions, 13 classes
- Linting score: 100% clean (0 flake8 lint violations / PEP 8 compliant)


### Self-Assessment
Rate yourself (1-5, 5 being excellent) and provide justification:
- **Code Readability:** 4 - Functions were kept small and modular with consistent styling and docstrings
- **Code Maintainability:** 4 - Some files are very long, I'm wondering if there should be a limit to the size of files to make it easier to maintain
- **Test Quality:** 5 - Tests are comprehensize, if the code changes a test can cover it
- **Documentation:** 4 - Dcostrings aren't as comprehensive, but there are specs for different features written out. Though the spec for UI is way too long

## Learning Outcomes

### Technical Skills Developed
Throughout this project, I strengthened key software engineering competencies across multiple areas:
- **Programming Concepts:** Implemented object-oriented design patterns (Strategy, Factory, and Facade) to decouple algorithmic card selection and session orchestration from frontend interfaces, as well as dynamic weighted probability models for adaptive spaced learning.
- **Tools and Frameworks:** Mastered Python's `pytest` ecosystem including `pytest-cov`, and learned Streamlit along with its `streamlit.testing.v1.AppTest` harness for headless automated frontend testing.
- **Testing Practices:** Internalized strict Test-Driven Development (TDD) using the Arrange-Act-Assert structure, writing negative and boundary test assertions before implementation to achieve 89% overall test coverage.
- **Code Organization:** Enforced rigorous separation of concerns between I/O, domain logic, and presentation, while maintaining readability and single responsibility by enforcing a strict sub-40-line constraint per function.


### AI Collaboration Skills
Working extensively with AI highlighted how critical developer direction is in an AI-assisted workflow:
- **Effective Prompting Techniques:** Moving away from broad prompts in favor of spec-driven pipelines (`spec.md` -> `plan.md` -> `tasks.md`) and pre-implementation Q&A discovery interviews produced vastly superior, aligned results.
- **Code Review and Validation Strategies:** Adopting a strict "one function at a time" cadence combined with immediate automated test execution prevented regressions and kept generated logic verifiable.
- **When to Rely on AI vs. Manual Coding:** AI was exceptionally effective at scaffolding test cases, generating boilerplate patterns, and suggesting refactorings, but manual architectural guidance was essential when handling complex UI state machines and lifecycle hooks.
- **Understanding AI Limitations:** AI models easily slip into generating bloated, multi-assertion tests and unmaintainable long functions if guardrails like line limits and single-responsibility constraints are not strictly enforced.


### Software Engineering Insights
Building this application provided deep insights into fundamental software engineering principles:
- **Design Patterns:** Implementing the Strategy and Factory patterns concretely demonstrated the Open/Closed Principle—enabling new quiz modes to be introduced without touching existing scoring or session controller logic.
- **Testing Strategies:** Practicing TDD reinforced that automated tests are not just verification tools, but design tools that force you to consider API ergonomics, edge cases, and failure modes prior to writing implementation code.
- **Code Organization:** Enforcing strict modular boundaries and keeping functions under 40 lines prevented spaghetti code and ensured each module could be reasoned about, tested, and refactored in complete isolation.
- **Documentation Practices:** Learned that concise, executable specifications (`spec.md` with architectural diagrams and acceptance criteria) provide far more value than speculative, overly verbose documentation that quickly diverges from reality.


## Reflection

### What Worked Well
The most successful aspect of this project was the synergy between spec-driven planning and test-driven development. Breaking features into formal specifications (`spec.md`), implementation roadmaps (`plan.md`), and granular tasks (`tasks.md`) kept development tightly focused and prevented AI hallucinations or scope creep. Conducting an interactive Q&A interview before generating code surfaced crucial edge cases early. Enforcing a strict 40-line ceiling per function and reviewing code one function at a time ensured readability and high quality throughout. Above all, I am most proud of the architectural decoupling between the domain logic (`quiz_engine.py`), the Facade (`session_controller.py`), and the presentation layers—allowing both the CLI and Streamlit interfaces to share identical business logic without duplicate code.


### What Could Be Improved
Looking back, the primary area for improvement is managing file-level size and specification scope. While enforcing a 40-line function ceiling kept individual functions readable, several files (such as `quiz_engine.py` and `session_controller.py`) grew lengthy and could benefit from further decomposition into smaller sub-modules with explicit file-size limits. Additionally, while the features are backed by comprehensive specifications, the UI specification became overly long and dense; next time, I would constrain the spec drafting phase to be more concise and modular. Finally, I would improve inline documentation by ensuring all internal helper methods have comprehensive docstrings with parameter types, return values, and usage examples alongside the test suite.


### Future Enhancements
Given additional development time, several valuable enhancements could be integrated into the application:
- **Technical Improvements:** Transition session and card history persistence from local JSON files to an embedded SQLite database using an ORM like SQLAlchemy to enable robust multi-deck transaction safety.
- **New Functionality:** Expand question formats beyond standard prompt/answer pairs to support multiple-choice questions, fill-in-the-blanks, and image-based flashcards, as well as deck tagging and search.
- **Better User Experience:** Implement a full SuperMemo (SM-2) spaced repetition algorithm with scheduled intervals, calendar reminders, and interactive performance charts in Streamlit to track mastery over weeks.
- **Performance Optimizations:** Introduce asynchronous I/O and cached deck indexing for handling flashcard datasets with tens of thousands of cards without latency.


## Conclusion
This project fundamentally reshaped my understanding of AI-assisted engineering: rather than treating AI as an autonomous code generator, the most productive paradigm is an interactive, disciplined pair-programming partnership. AI delivers immense leverage when guided by formal specifications, granular task decompositions, and strict human verification. Going forward, I will permanently adopt spec-driven design (`spec.md`, `plan.md`, `tasks.md`) and test-driven development (TDD) as standard practices for any codebase. Establishing automated test suites before drafting implementation details and demanding small, single-responsibility functions creates clean, resilient software that is easily maintained, extended, and trusted.


## Appendices

### Appendix A: AI Interaction Log
The complete history of prompts, responses, modifications, and reasoning is documented in [`docs/ai_edit_log.md`](file:///Users/carlosvaleriano/Desktop/Upwork%20Portfolio/flashcard_quizzer/cd14602-project-starter/project/main/docs/ai_edit_log.md). Key milestone entries include:
- **2026-10-05 (Data Ingestion & Validation):** Established the TDD pipeline, generated 20 test fixtures, and compressed the JSON loader from 54 to 35 lines while preserving validation logic.
- **2026-10-06 (Quiz Engine Architecture):** Built the Strategy and Factory patterns across Tasks 0–10, decoupling card traversal algorithms and maintaining 87%+ module test coverage.
- **2026-10-06 (UI Feature Specification):** Conducted a 39-question interactive interview to author the comprehensive UI specification and architect the `SessionController` Facade.
- **2026-10-06 (Streamlit Lifecycle Bug Fixes):** Diagnosed rerun desynchronization loops, authored automated UI tests via `AppTest`, and stabilized form resets.


### Appendix B: Code Statistics
Quantitative codebase metrics and test execution measurements:
- **Test Suite Results:** 95 passed out of 95 tests across 8 test suites in 4.43 seconds (100% pass rate).
- **Overall Test Coverage:** 89% total coverage across 865 executable statements.
- **Module Coverage Breakdown:**
  - `utils/task_manager.py`: 100% (26/26 statements)
  - `streamlit_frontend.py`: 94% (145/154 statements)
  - `utils/session_controller.py`: 93% (209/225 statements)
  - `utils/quiz_engine.py`: 91% (223/245 statements)
  - `utils/file_handler.py`: 89% (50/56 statements)
  - `cli_frontend.py`: 74% (117/159 statements)
- **Code Style & Quality:** 0 flake8 lint violations (100% PEP 8 compliant).
- **Function Constraints:** 100% of functions adhere strictly to the sub-40-line limit.

### Appendix C: Additional Resources
Resources and literature that guided architectural and workflow decisions:
- **AI-Native Software Engineering:** Methodology guidelines for specification-driven development (`spec.md` -> `plan.md` -> `tasks.md`) and disciplined AI collaboration workflows.
- **Design Patterns Guide (`docs/design_patterns.md`):** Reference patterns for implementing Strategy, Factory, and Facade structures in Python.
- **Streamlit Testing Framework (`streamlit.testing.v1`):** Official documentation for headless, automated component testing using `AppTest`.
- **Pytest & Coverage Documentation:** Best practices for test isolation, fixture design, and test-driven Arrange-Act-Assert methodologies.
- **PEP 8 – Style Guide for Python Code:** Guidelines used to maintain lint compliance and readability across all source files.

---

**Total Report Length:** Aim for 2000-3000 words  
**Due Date:** 10/7/2026
**Submission Instructions:** N/A