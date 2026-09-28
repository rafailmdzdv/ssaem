# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT
from typing import Final

from dmr.routing import Router, path

from server.apps.exercises.views import (
    CheckExerciseController,
    GenerateExerciseController,
)

app_name = 'exercises'

exercise_router: Final = Router(
    'exercises/',
    (
        path(
            'generate/',
            GenerateExerciseController.as_view(),
            name='generate',
        ),
        path(
            'check/',
            CheckExerciseController.as_view(),
            name='check',
        ),
    ),
    tags=['Exercises'],
)
