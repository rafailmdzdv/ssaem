# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import final, override

from server.apps.exercises.logic.interfaces import (
    LearningDataRepository,
    LLMClient,
    ToolMap,
)
from server.apps.exercises.logic.services import ExerciseService
from server.apps.exercises.logic.value_objects import (
    ExerciseCheckResult,
    GeneratedExercise,
)


@final
class MockLLMClient(LLMClient):
    """Mock LLM implementation conforming to LLMClient interface."""

    def __init__(self) -> None:
        """Initialize mock LLM client."""
        self.last_system_prompt: str = ''
        self.last_user_context: dict[str, str] = {}
        self.last_tools: ToolMap = {}
        self.last_checked: dict[str, str] = {}

    @override
    def generate_exercise(
        self,
        system_prompt: str,
        user_context: dict[str, str],
        tools: ToolMap,
    ) -> GeneratedExercise:
        self.last_system_prompt = system_prompt
        self.last_user_context = user_context
        self.last_tools = tools
        words_data = tools['user_words']()
        grammar_data = tools['user_grammars']()
        return GeneratedExercise(
            sentence='I go to school.',
            reference_translation='학교에 가요.',
            words_used=[word_entry['word'] for word_entry in words_data[:2]],
            grammar_used=[
                grammar_entry['grammar'] for grammar_entry in grammar_data[:1]
            ],
        )

    @override
    def check_exercise(
        self,
        native_language: str,
        sentence: str,
        user_answer: str,
        reference_translation: str = '',
    ) -> ExerciseCheckResult:
        self.last_checked = {
            'native_language': native_language,
            'sentence': sentence,
            'user_answer': user_answer,
            'reference_translation': reference_translation,
        }
        is_match = user_answer.strip() == reference_translation.strip()
        return ExerciseCheckResult(
            is_correct=is_match,
            feedback='Good job!' if is_match else 'Try again!',
            corrected_sentence=reference_translation,
        )


@final
class FakeRepository(LearningDataRepository):
    """Fake repository implementation for testing."""

    @override
    def user_words(self, user_id: int) -> list[dict[str, str]]:
        return [{'word': '학교', 'meaning': 'school'}]

    @override
    def user_grammars(self, user_id: int) -> list[dict[str, str]]:
        return [{'grammar': '-에', 'meaning': 'location'}]


def test_service_generate_content() -> None:
    mock_llm = MockLLMClient()
    fake_repo = FakeRepository()
    assert isinstance(mock_llm, LLMClient)
    assert isinstance(fake_repo, LearningDataRepository)

    service = ExerciseService(mock_llm, fake_repo)
    exercise = service.generate(user_id=42, native_language='ru')

    assert exercise.sentence == 'I go to school.'
    assert exercise.reference_translation == '학교에 가요.'
    assert exercise.words_used == ['학교']


def test_service_generate_context() -> None:
    mock_llm = MockLLMClient()
    fake_repo = FakeRepository()
    service = ExerciseService(mock_llm, fake_repo)
    exercise = service.generate(user_id=42, native_language='ru')

    assert exercise.grammar_used == ['-에']
    assert mock_llm.last_user_context == {'native_language': 'ru'}
    assert 'user_words' in mock_llm.last_tools
    assert 'user_grammars' in mock_llm.last_tools


def test_service_check_flow_correct() -> None:
    mock_llm = MockLLMClient()
    fake_repo = FakeRepository()
    service = ExerciseService(mock_llm, fake_repo)

    check_result = service.check(
        native_language='ru',
        sentence='I go to school.',
        user_answer='학교에 가요.',
        reference_translation='학교에 가요.',
    )

    assert check_result.is_correct is True
    assert check_result.feedback == 'Good job!'
    assert check_result.corrected_sentence == '학교에 가요.'


def test_service_check_flow_incorrect() -> None:
    mock_llm = MockLLMClient()
    fake_repo = FakeRepository()
    service = ExerciseService(mock_llm, fake_repo)

    check_result = service.check(
        native_language='en',
        sentence='I go to school.',
        user_answer='틀린 답',
        reference_translation='학교에 가요.',
    )

    assert check_result.is_correct is False
    assert check_result.feedback == 'Try again!'
