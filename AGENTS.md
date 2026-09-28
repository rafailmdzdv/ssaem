# Guidelines for AI Coding Agents

This document defines architectural, coding, and design standards that must be strictly followed by all AI coding agents working on this project.

---

## 1. Protocols and Interface Implementations

- **Explicit Inheritance**: When defining and using protocols (interfaces), all concrete implementations **must explicitly inherit** from the corresponding protocol class. Do not rely solely on duck typing or structural subtyping.
- **Use `@override` Decorator**: All methods implementing or overriding methods from a protocol or base class **must be decorated with `@override`** (imported from `typing`).
- **Example**:

  ```python
  from typing import Protocol, override

  class LearningDataRepository(Protocol):
      """Repository protocol to access user learning data."""

      def user_words(self, user_id: int) -> list[dict[str, str]]:
          """Retrieve learned vocabulary words for a given user."""
          ...

  class DjangoLearningDataRepository(LearningDataRepository):
      """Concrete repository accessing learning materials in the database."""

      @override
      def user_words(self, user_id: int) -> list[dict[str, str]]:
          ...
  ```

---

## 2. Method Naming Conventions (No `get` / `set` Prefixes)

- **No `get` or `set` Prefixes**: Methods **must not** start with `get_` or `set_`.
- Name methods after the entity, resource, or action they represent directly.
  - ❌ Incorrect: `get_user_grammars(user_id)`
  - ✅ Correct: `user_grammars(user_id)`
  - ❌ Incorrect: `get_user_words(user_id)`
  - ✅ Correct: `user_words(user_id)`
- Use Python properties (`@property`) when exposing simple attributes, and use clear verbs or noun phrases for methods without unnecessary getters/setters.

---

## 3. Layered Architecture and Import Rules

- Follow the layered architecture specified in `.importlinter`:
  - `(urls) | (admin)`
  - `(views) | (htmx) | (api)`
  - `(tasks)`
  - `(infra)`
  - `(models)`
  - `(logic)`
- A layer may only import from layers strictly below it.
- Logic is domain-pure and must never import from `models`, `infra`, or `views`.
- All applications in `server.apps.*` must remain independent from one another.
- `server.common` must not import anything from `server.apps`.

---

## 4. Code Quality and Style Standards

- **Strict Type Annotations**: All function/method signatures and variables must have explicit type annotations.
- **Final Classes**: Use `@final` from `typing` on classes that are not intended to be subclassed.
- **Linters & Formatters**:
  - `ruff` (formatting and linting)
  - `flake8` with `wemake-python-styleguide`
  - `import-linter` (contracts enforcement)
  - `pytest` with coverage requirements (minimum 70% coverage)

---

## 5. Docstring Rules for Third-Party Modules and Overridden Methods

- **No Module Docstrings for Third-Party / Framework Modules**: Do not add module-level docstrings to files related to Django, DMR, or other third-party frameworks (e.g., `models.py`, `views.py`, `admin.py`, `urls.py`, `apps.py`, `migrations/*.py`).
- **No Docstrings for Overridden Third-Party Methods**: Do not add docstrings to methods that are overridden from Django, DMR, or other third-party libraries (e.g., methods decorated with `@override` like `handle_error`, `clean`, `__str__`, `get_queryset`, etc.).
- **Keep Docstrings for Project Protocols**: Do not remove docstrings from methods implementing internal project protocols (e.g., concrete repository or LLM client implementations). These must still have docstrings documenting their behavior.
- **Example**:

  ```python
  class Word(models.Model):
      """Vocabulary word learned by a user."""
      ...

      # Overridden from Django: NO docstring
      @override
      def __str__(self) -> str:
          return f'{self.word} ({self.meaning})'

  class GenerateExerciseController(Controller[MsgspecSerializer]):
      """Generate exercise sentence for learning."""
      ...

      # Overridden from third-party DMR Controller: NO docstring
      @override
      def handle_error(
          self,
          endpoint: Endpoint,
          controller: Controller[MsgspecSerializer],
          exc: Exception,
      ) -> HttpResponse:
          ...

  class DjangoLearningDataRepository(LearningDataRepository):
      """Concrete repository accessing learning materials in the database."""

      # Implementing project protocol: KEEP docstrings
      @override
      def user_words(self, user_id: int) -> list[dict[str, str]]:
          """Retrieve vocabulary words learned by user."""
          ...
  ```

