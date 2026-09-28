# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from collections.abc import Callable, Sequence
from typing import Protocol, TypedDict, final, runtime_checkable

from server.apps.exercises.logic.value_objects import (
    ExerciseCheckResult,
    GeneratedExercise,
)

ToolCallable = Callable[[], Sequence['UserWord | UserGrammar']]
ToolMap = dict[str, ToolCallable]


@final
class UserWord(TypedDict):
    """Dictionary representation of a user word."""

    word: str
    meaning: str


@final
class UserGrammar(TypedDict):
    """Dictionary representation of a user grammar point."""

    grammar: str
    meaning: str


@runtime_checkable
class LLMClient(Protocol):
    """General interface for Large Language Model providers."""

    def generate_exercise(
        self,
        system_prompt: str,
        user_context: dict[str, str],
        tools: ToolMap,
    ) -> GeneratedExercise:
        """Generate an exercise using context and tools."""
        ...

    def check_exercise(
        self,
        native_language: str,
        sentence: str,
        user_answer: str,
        reference_translation: str = '',
    ) -> ExerciseCheckResult:
        """Evaluate student translation accuracy and grammar."""
        ...


@runtime_checkable
class LearningDataRepository(Protocol):
    """Repository protocol to access user learning data."""

    def user_words(self, user_id: int) -> list[UserWord]:
        """Retrieve learned vocabulary words for a given user."""
        ...

    def user_grammars(self, user_id: int) -> list[UserGrammar]:
        """Retrieve available grammar points for a given user."""
        ...
