# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import final

import pytest
from hypothesis.extra import django

from server.apps.auth.models import User
from server.apps.exercises.exceptions import (
    EmptyGrammarsError,
    EmptyWordsError,
)
from server.apps.exercises.infra.repositories import (
    DjangoLearningDataRepository,
)
from server.apps.exercises.models import Grammar, Word


@final
class TestLearningDataRepository(django.TestCase):
    """Tests for DjangoLearningDataRepository."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='repo_user@example.com',
            password='password123',
        )
        self.repo = DjangoLearningDataRepository()

    def test_user_words_empty(self) -> None:
        with pytest.raises(EmptyWordsError):
            self.repo.user_words(self.user.pk)

    def test_user_words_from_db(self) -> None:
        Word.objects.create(
            user=self.user,
            word='책',
            meaning='book',
        )
        words = self.repo.user_words(self.user.pk)
        assert len(words) == 1
        assert words[0]['word'] == '책'
        assert words[0]['meaning'] == 'book'

    def test_user_grammars_empty(self) -> None:
        with pytest.raises(EmptyGrammarsError):
            self.repo.user_grammars(self.user.pk)

    def test_user_grammars_from_db(self) -> None:
        Grammar.objects.create(
            user=self.user,
            grammar='-(으)ㄹ 거예요',
            meaning='future tense',
        )
        grammars = self.repo.user_grammars(self.user.pk)
        assert len(grammars) == 1
        assert grammars[0]['grammar'] == '-(으)ㄹ 거예요'
        assert grammars[0]['meaning'] == 'future tense'
