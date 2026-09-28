# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

"""Gemini LLM client implementation with tool calling support."""

import json
from typing import Any, Final, final, override

import httpx

from server.apps.exercises.logic.constants import CHECK_SYSTEM_PROMPT
from server.apps.exercises.logic.interfaces import LLMClient, ToolMap
from server.apps.exercises.logic.value_objects import (
    ExerciseCheckResult,
    GeneratedExercise,
)

_DEFAULT_API_BASE: Final = 'https://generativelanguage.googleapis.com/v1beta'
_DEFAULT_MODEL: Final = 'gemini-2.5-flash'
_MAX_TOOL_TURNS: Final = 5
_TIMEOUT_SECONDS: Final = 20.0

_ROLE: Final = 'role'
_PARTS: Final = 'parts'
_TEXT: Final = 'text'
_NAME: Final = 'name'
_USER: Final = 'user'
_CALL_ID: Final = 'id'


@final
class GeminiAPIError(Exception):
    """Raised when the Gemini API request fails."""


def _build_tools_declaration(
    tool_names: list[str],
) -> list[dict[str, Any]]:
    """Build Gemini tool declarations."""
    declarations = [
        {
            _NAME: tool_name,
            'description': f'Provide data for {tool_name}',
            'parameters': {'type': 'OBJECT', 'properties': {}},
        }
        for tool_name in tool_names
    ]
    return [{'functionDeclarations': declarations}]


def _extract_parts(api_response: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = api_response.get('candidates', [])
    if not candidates:
        raise GeminiAPIError('No candidates returned from Gemini API.')
    return list(candidates[0].get('content', {}).get(_PARTS, []))


def _parse_parts_json(parts: list[dict[str, Any]]) -> dict[str, Any]:
    """Parse JSON object from response parts, stripping codeblocks."""
    text_chunks = [part.get(_TEXT, '') for part in parts]
    raw = ''.join(text_chunks).strip()
    if raw.startswith('```'):
        lines = raw.splitlines()
        end_idx = -1 if lines[-1].startswith('```') else None
        lines = lines[1:end_idx]
        raw = '\n'.join(lines).strip()
    return json.loads(raw)  # type: ignore[no-any-return]


def _parse_exercise_result(
    parts: list[dict[str, Any]],
) -> GeneratedExercise:
    parsed = _parse_parts_json(parts)
    return GeneratedExercise(
        sentence=str(parsed.get('sentence', '')),
        reference_translation=str(parsed.get('reference_translation', '')),
        words_used=list(parsed.get('words_used', [])),
        grammar_used=list(parsed.get('grammar_used', [])),
    )


def _format_function_response(
    call: dict[str, Any],
    tools: ToolMap,
) -> dict[str, Any]:
    """Format function execution result for Gemini API."""
    fn_name = call[_NAME]
    tool_runner = tools.get(fn_name, list)
    fn_response: dict[str, Any] = {
        _NAME: fn_name,
        'response': {
            'output': tool_runner(),
        },
    }
    call_id = call.get(_CALL_ID)
    if call_id is not None:
        fn_response[_CALL_ID] = call_id
    return fn_response


@final
class GeminiLLMClient(LLMClient):
    """Client for Google Gemini API conforming to LLMClient protocol."""

    def __init__(
        self,
        api_key: str = '',
        model: str = _DEFAULT_MODEL,
        api_base_url: str = _DEFAULT_API_BASE,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Initialize Gemini client."""
        self._api_key = api_key
        self._model = model
        self._api_base_url = api_base_url
        self._http_client = http_client or httpx.Client(
            timeout=_TIMEOUT_SECONDS,
        )

    @override
    def generate_exercise(
        self,
        system_prompt: str,
        user_context: dict[str, str],
        tools: ToolMap,
    ) -> GeneratedExercise:
        """Generate an exercise using tool-calling loop."""
        self._check_api_key()
        messages: list[dict[str, Any]] = [
            {
                _ROLE: _USER,
                _PARTS: [
                    {
                        _TEXT: (
                            f'User context: {json.dumps(user_context)}\n\n'
                            'Generate the next exercise.'
                        ),
                    },
                ],
            },
        ]
        tool_decl = _build_tools_declaration(list(tools.keys()))
        return self._run_generation_loop(
            system_prompt,
            messages,
            tool_decl,
            tools,
        )

    @override
    def check_exercise(
        self,
        native_language: str,
        sentence: str,
        user_answer: str,
        reference_translation: str = '',
    ) -> ExerciseCheckResult:
        """Evaluate a student answer for a sentence."""
        self._check_api_key()
        prompt = (
            f'Native language: {native_language}\n'
            f'Source sentence: {sentence}\n'
            f'Student answer: {user_answer}\n'
            f'Reference translation: {reference_translation}\n'
        )
        payload = {
            'systemInstruction': {_PARTS: [{_TEXT: CHECK_SYSTEM_PROMPT}]},
            'contents': [{_ROLE: _USER, _PARTS: [{_TEXT: prompt}]}],
        }
        api_response = self._post_request(payload)
        parts = _extract_parts(api_response)
        parsed = _parse_parts_json(parts)
        return ExerciseCheckResult(
            is_correct=bool(parsed.get('is_correct', False)),
            feedback=str(parsed.get('feedback', '')),
            corrected_sentence=str(parsed.get('corrected_sentence', '')),
        )

    def _check_api_key(self) -> None:
        if not self._api_key:
            raise GeminiAPIError('Gemini API key is not configured.')

    def _run_generation_loop(
        self,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools_decl: list[dict[str, Any]],
        tools: ToolMap,
    ) -> GeneratedExercise:
        for _ in range(_MAX_TOOL_TURNS):
            payload = {
                'systemInstruction': {_PARTS: [{_TEXT: system_prompt}]},
                'contents': messages,
                'tools': tools_decl,
            }
            api_response = self._post_request(payload)
            parts = _extract_parts(api_response)
            calls = [part for part in parts if 'functionCall' in part]
            if not calls:
                return _parse_exercise_result(parts)
            self._handle_function_calls(
                parts,
                calls,
                messages,
                tools,
            )
        raise GeminiAPIError('Exceeded maximum tool-calling turns.')

    def _handle_function_calls(
        self,
        parts: list[dict[str, Any]],
        function_calls: list[dict[str, Any]],
        messages: list[dict[str, Any]],
        tools: ToolMap,
    ) -> None:
        messages.append({_ROLE: 'model', _PARTS: parts})
        for call_part in function_calls:
            call = call_part['functionCall']
            messages.append(
                {
                    _ROLE: 'user',
                    _PARTS: [
                        {
                            'functionResponse': _format_function_response(
                                call,
                                tools,
                            ),
                        },
                    ],
                },
            )

    def _post_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = (
            f'{self._api_base_url}/models/'
            f'{self._model}:generateContent?key={self._api_key}'
        )
        response = self._http_client.post(url, json=payload)
        if response.status_code != httpx.codes.OK:
            raise GeminiAPIError(
                f'Gemini API error {response.status_code}: {response.text}',
            )
        return response.json()  # type: ignore[no-any-return]
