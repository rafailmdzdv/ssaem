# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

"""Response schemas for exercise endpoints."""

from typing import TypedDict, final


@final
class GenerateExerciseResponse(TypedDict):
    """Response returned when generating an exercise."""

    sentence: str
    reference_translation: str
    words_used: list[str]
    grammar_used: list[str]


@final
class CheckExerciseResponse(TypedDict):
    """Response returned when evaluating an exercise."""

    is_correct: bool
    feedback: str
    corrected_sentence: str
