# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

"""Payload schemas for exercise operations."""

from typing import NotRequired, TypedDict, final


@final
class GenerateExercisePayload(TypedDict, total=False):
    """Payload to customize exercise generation (optional)."""

    difficulty: NotRequired[str]
    exercise_type: NotRequired[str]


@final
class CheckExercisePayload(TypedDict):
    """Payload to check user answer."""

    sentence: str
    user_answer: str
    reference_translation: NotRequired[str]
