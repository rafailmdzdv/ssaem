# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from http import HTTPStatus
from typing import final, override

from django.http import HttpResponse
from dmr import Body, Controller, ResponseSpec, modify
from dmr.endpoint import Endpoint
from dmr.errors import ErrorModel
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.security.jwt import JWTSyncAuth

from server.apps.exercises.exceptions import UserGenerationError
from server.apps.exercises.logic.services import ExerciseService
from server.apps.exercises.schemas import (
    CheckExercisePayload,
    CheckExerciseResponse,
    GenerateExerciseResponse,
)
from server.common.di import HasContainer


@final
class GenerateExerciseController(
    HasContainer,
    Controller[MsgspecSerializer],
):
    """Generate exercise sentence for learning."""

    auth = (JWTSyncAuth(),)
    responses = (ResponseSpec(ErrorModel, status_code=HTTPStatus.BAD_REQUEST),)

    @modify(status_code=HTTPStatus.OK)
    def post(self) -> GenerateExerciseResponse:
        """Generate a new exercise sentence."""
        service = self.resolve(ExerciseService)
        user = self.request.user
        native_lang = getattr(user, 'source_language', 'en')
        exercise = service.generate(
            user_id=getattr(user, 'pk', 0),
            native_language=native_lang,
        )
        return {
            'sentence': exercise.sentence,
            'reference_translation': exercise.reference_translation,
            'words_used': exercise.words_used,
            'grammar_used': exercise.grammar_used,
        }

    @override
    def handle_error(
        self,
        endpoint: Endpoint,
        controller: Controller[MsgspecSerializer],
        exc: Exception,
    ) -> HttpResponse:
        if isinstance(exc, UserGenerationError):
            return self.to_error(
                controller.format_error(exc.message),
                status_code=HTTPStatus.BAD_REQUEST,
            )
        return super().handle_error(endpoint, controller, exc)


@final
class CheckExerciseController(
    HasContainer,
    Controller[MsgspecSerializer],
):
    """Check submitted translation for correctness."""

    auth = (JWTSyncAuth(),)

    @modify(status_code=HTTPStatus.OK)
    def post(
        self,
        parsed_body: Body[CheckExercisePayload],
    ) -> CheckExerciseResponse:
        """Check whether the user entered the sentence correctly."""
        service = self.resolve(ExerciseService)
        user = self.request.user
        native_lang = getattr(user, 'source_language', 'en')
        evaluation = service.check(
            native_language=native_lang,
            sentence=parsed_body['sentence'],
            user_answer=parsed_body['user_answer'],
            reference_translation=parsed_body.get('reference_translation', ''),
        )
        return {
            'is_correct': evaluation.is_correct,
            'feedback': evaluation.feedback,
            'corrected_sentence': evaluation.corrected_sentence,
        }
