# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from server.apps.exercises.schemas.payload.exercise import (
    CheckExercisePayload,
    GenerateExercisePayload,
)
from server.apps.exercises.schemas.response.exercise import (
    CheckExerciseResponse,
    GenerateExerciseResponse,
)

__all__ = (
    'CheckExercisePayload',
    'CheckExerciseResponse',
    'GenerateExercisePayload',
    'GenerateExerciseResponse',
)
