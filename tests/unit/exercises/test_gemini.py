# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

import json

import httpx
import pytest

from server.apps.exercises.infra.gemini import (
    GeminiAPIError,
    GeminiLLMClient,
)
from server.apps.exercises.logic.interfaces import ToolMap


def _tool_calling_handler(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    messages = body.get('contents', [])
    if len(messages) == 1:
        return httpx.Response(
            200,
            json={
                'candidates': [
                    {
                        'content': {
                            'parts': [
                                {
                                    'functionCall': {
                                        'id': 'words_call_1',
                                        'name': 'user_words',
                                        'args': {},
                                    },
                                },
                                {
                                    'functionCall': {
                                        'name': 'user_grammars',
                                        'args': {},
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
        )
    return httpx.Response(
        200,
        json={
            'candidates': [
                {
                    'content': {
                        'parts': [
                            {
                                'text': json.dumps(
                                    {
                                        'sentence': 'I go to school.',
                                        'reference_translation': '학교에 가요.',
                                        'words_used': ['학교', '가다'],
                                        'grammar_used': ['-에', '-아요/어요'],
                                    },
                                ),
                            },
                        ],
                    },
                },
            ],
        },
    )


def _wrapped_json_handler(request: httpx.Request) -> httpx.Response:
    wrapped_json = (
        '```json\n'
        '{\n'
        '  "sentence": "Я ем яблоко.",\n'
        '  "reference_translation": "사과를 먹어요.",\n'
        '  "words_used": ["사과", "먹다"],\n'
        '  "grammar_used": ["-을/를"]\n'
        '}\n'
        '```'
    )
    return httpx.Response(
        200,
        json={
            'candidates': [
                {'content': {'parts': [{'text': wrapped_json}]}},
            ],
        },
    )


def _check_exercise_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            'candidates': [
                {
                    'content': {
                        'parts': [
                            {
                                'text': json.dumps(
                                    {
                                        'is_correct': True,
                                        'feedback': 'Отличный перевод!',
                                        'corrected_sentence': '학교에 가요.',
                                    },
                                ),
                            },
                        ],
                    },
                },
            ],
        },
    )


def _empty_candidates_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={'candidates': []})


def _error_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500, text='Internal Server Error')


def test_missing_api_key_raises_error() -> None:
    client = GeminiLLMClient(api_key='')
    with pytest.raises(
        GeminiAPIError,
        match='Gemini API key is not configured',
    ):
        client.generate_exercise('prompt', {}, {})


def test_gemini_tool_calling_loop() -> None:
    transport = httpx.MockTransport(_tool_calling_handler)
    http_client = httpx.Client(transport=transport)
    gemini = GeminiLLMClient(
        api_key='fake_test_key',
        http_client=http_client,
    )

    tools: ToolMap = {
        'user_words': lambda: [{'word': '학교', 'meaning': 'school'}],
        'user_grammars': lambda: [{'grammar': '-에', 'meaning': 'location'}],
    }
    exercise = gemini.generate_exercise(
        system_prompt='system prompt',
        user_context={'native_language': 'en'},
        tools=tools,
    )

    assert exercise.sentence == 'I go to school.'
    assert exercise.reference_translation == '학교에 가요.'
    assert '학교' in exercise.words_used
    assert '-에' in exercise.grammar_used


def test_gemini_markdown_wrapped_json() -> None:
    transport = httpx.MockTransport(_wrapped_json_handler)
    http_client = httpx.Client(transport=transport)
    gemini = GeminiLLMClient(
        api_key='fake_test_key',
        http_client=http_client,
    )

    exercise = gemini.generate_exercise(
        system_prompt='prompt',
        user_context={'native_language': 'ru'},
        tools={},
    )
    assert exercise.sentence == 'Я ем яблоко.'
    assert exercise.reference_translation == '사과를 먹어요.'


def test_gemini_http_error() -> None:
    transport = httpx.MockTransport(_error_handler)
    http_client = httpx.Client(transport=transport)
    gemini = GeminiLLMClient(
        api_key='fake_test_key',
        http_client=http_client,
    )

    with pytest.raises(GeminiAPIError, match='Gemini API error 500'):
        gemini.generate_exercise('prompt', {}, {})


def test_gemini_check_exercise() -> None:
    transport = httpx.MockTransport(_check_exercise_handler)
    http_client = httpx.Client(transport=transport)
    gemini = GeminiLLMClient(
        api_key='fake_test_key',
        http_client=http_client,
    )

    evaluation = gemini.check_exercise(
        native_language='ru',
        sentence='Я иду в школу.',
        user_answer='학교에 가요.',
        reference_translation='학교에 가요.',
    )

    assert evaluation.is_correct is True
    assert evaluation.feedback == 'Отличный перевод!'
    assert evaluation.corrected_sentence == '학교에 가요.'


def test_gemini_empty_candidates() -> None:
    transport = httpx.MockTransport(_empty_candidates_handler)
    http_client = httpx.Client(transport=transport)
    gemini = GeminiLLMClient(
        api_key='fake_test_key',
        http_client=http_client,
    )

    with pytest.raises(GeminiAPIError, match='No candidates returned'):
        gemini.generate_exercise('prompt', {}, {})


def _infinite_tool_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            'candidates': [
                {
                    'content': {
                        'parts': [
                            {
                                'functionCall': {
                                    'name': 'user_words',
                                    'args': {},
                                },
                            },
                        ],
                    },
                },
            ],
        },
    )


def test_gemini_max_tool_turns_exceeded() -> None:
    transport = httpx.MockTransport(_infinite_tool_handler)
    http_client = httpx.Client(transport=transport)
    gemini = GeminiLLMClient(
        api_key='fake_test_key',
        http_client=http_client,
    )

    with pytest.raises(GeminiAPIError, match='Exceeded maximum'):
        gemini.generate_exercise('prompt', {}, {'user_words': list})
