# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from http import HTTPStatus
from typing import Final
from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse
from plugins.auth import make_jwt_token

from server.apps.exercises.exceptions import EmptyWordsError
from server.apps.exercises.logic.services import ExerciseService
from server.apps.exercises.logic.value_objects import (
    ExerciseCheckResult,
    GeneratedExercise,
)

_GENERATE_URL: Final = reverse('api:exercises:generate')
_CHECK_URL: Final = reverse('api:exercises:check')

_AUTH_HEADER: Final = 'HTTP_AUTHORIZATION'


def _auth_header(user_id: int) -> dict[str, str]:
    token = make_jwt_token(user_id)
    return {_AUTH_HEADER: f'Bearer {token}'}


@pytest.mark.django_db
def test_generate_exercise_unauthorized(client: Client) -> None:
    response = client.post(_GENERATE_URL)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_generate_exercise_success(client: Client, create_user) -> None:
    fake_exercise = GeneratedExercise(
        sentence='I go to school.',
        reference_translation='학교에 가요.',
        words_used=['학교', '가다'],
        grammar_used=['-에', '-아요/어요'],
    )
    with patch.object(
        ExerciseService,
        'generate',
        return_value=fake_exercise,
    ) as mock_generate:
        response = client.post(
            _GENERATE_URL,
            **_auth_header(create_user.pk),
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body['sentence'] == 'I go to school.'
        assert body['reference_translation'] == '학교에 가요.'
        assert body['words_used'] == ['학교', '가다']
        assert body['grammar_used'] == ['-에', '-아요/어요']

        mock_generate.assert_called_once_with(
            user_id=create_user.pk,
            native_language=create_user.source_language,
        )


@pytest.mark.django_db
def test_generate_exercise_empty_words_error(
    client: Client,
    create_user,
) -> None:
    with patch.object(
        ExerciseService,
        'generate',
        side_effect=EmptyWordsError,
    ):
        response = client.post(
            _GENERATE_URL,
            **_auth_header(create_user.pk),
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        body = response.json()
        assert 'There is no any words' in body['detail'][0]['msg']


@pytest.mark.django_db
def test_generate_exercise_unhandled_error(
    client: Client,
    create_user,
) -> None:
    with (
        patch.object(
            ExerciseService,
            'generate',
            side_effect=RuntimeError('Crash'),
        ),
        pytest.raises(RuntimeError, match='Crash'),
    ):
        client.post(
            _GENERATE_URL,
            **_auth_header(create_user.pk),
        )


@pytest.mark.django_db
def test_check_exercise_unauthorized(client: Client) -> None:
    response = client.post(
        _CHECK_URL,
        data={'sentence': 'I go to school.', 'user_answer': '학교에 가요.'},
        content_type='application/json',
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_check_exercise_success(client: Client, create_user) -> None:
    fake_result = ExerciseCheckResult(
        is_correct=True,
        feedback='Great job!',
        corrected_sentence='학교에 가요.',
    )
    with patch.object(
        ExerciseService,
        'check',
        return_value=fake_result,
    ) as mock_check:
        response = client.post(
            _CHECK_URL,
            data={
                'sentence': 'I go to school.',
                'user_answer': '학교에 가요.',
                'reference_translation': '학교에 가요.',
            },
            content_type='application/json',
            **_auth_header(create_user.pk),
        )
        body = response.json()

        assert response.status_code == HTTPStatus.OK
        assert body['is_correct'] is True
        assert body['feedback'] == 'Great job!'
        assert body['corrected_sentence'] == '학교에 가요.'

        mock_check.assert_called_once_with(
            native_language=create_user.source_language,
            sentence='I go to school.',
            user_answer='학교에 가요.',
            reference_translation='학교에 가요.',
        )


@pytest.mark.django_db
def test_check_exercise_missing_fields(client: Client, create_user) -> None:
    response = client.post(
        _CHECK_URL,
        data={'sentence': 'Only sentence here'},
        content_type='application/json',
        **_auth_header(create_user.pk),
    )
    assert response.status_code in (
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.UNPROCESSABLE_ENTITY,
    )
