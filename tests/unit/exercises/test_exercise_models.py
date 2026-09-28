# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import final

from hypothesis.extra import django

from server.apps.auth.models import User
from server.apps.exercises.models import Grammar, Word


@final
class TestExerciseModels(django.TestCase):
    """Tests for Word and Grammar models."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='student@example.com',
            password='password123',
        )

    def test_word_creation_and_str(self) -> None:
        word = Word.objects.create(
            user=self.user,
            word='학교',
            meaning='school',
        )
        assert word.pk is not None
        assert str(word) == '학교 (school)'

    def test_grammar_creation_and_str(self) -> None:
        grammar = Grammar.objects.create(
            user=self.user,
            grammar='-아요/어요',
            meaning='present polite ending',
        )
        assert grammar.pk is not None
        assert str(grammar) == '-아요/어요 (present polite ending)'
