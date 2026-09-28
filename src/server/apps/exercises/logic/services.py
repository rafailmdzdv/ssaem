# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

"""Domain service orchestrating exercise operations."""

from typing import final

import attrs

from server.apps.exercises.logic.constants import SYSTEM_PROMPT
from server.apps.exercises.logic.interfaces import (
    LearningDataRepository,
    LLMClient,
    ToolMap,
)
from server.apps.exercises.logic.value_objects import (
    ExerciseCheckResult,
    GeneratedExercise,
)


@final
@attrs.define(slots=True, frozen=True)
class ExerciseService:
    """Service orchestrating exercise generation and evaluation."""

    _llm_client: LLMClient
    _repository: LearningDataRepository

    def generate(
        self,
        user_id: int,
        native_language: str,
    ) -> GeneratedExercise:
        """Generate an exercise based on user knowledge."""
        tools: ToolMap = {
            'user_words': lambda: self._repository.user_words(user_id),
            'user_grammars': (lambda: self._repository.user_grammars(user_id)),
        }
        user_context = {'native_language': native_language}
        return self._llm_client.generate_exercise(
            system_prompt=SYSTEM_PROMPT,
            user_context=user_context,
            tools=tools,
        )

    def check(
        self,
        native_language: str,
        sentence: str,
        user_answer: str,
        reference_translation: str = '',
    ) -> ExerciseCheckResult:
        """Check whether the user translation is correct."""
        return self._llm_client.check_exercise(
            native_language=native_language,
            sentence=sentence,
            user_answer=user_answer,
            reference_translation=reference_translation,
        )
