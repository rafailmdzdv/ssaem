# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import Final, final, override

from server.apps.exercises.exceptions import (
    EmptyGrammarsError,
    EmptyWordsError,
)
from server.apps.exercises.logic.interfaces import (
    LearningDataRepository,
    UserGrammar,
    UserWord,
)
from server.apps.exercises.models import Grammar, Word

_WORD: Final = 'word'
_MEANING: Final = 'meaning'
_GRAMMAR: Final = 'grammar'


@final
class DjangoLearningDataRepository(LearningDataRepository):
    """Repository accessing user vocabulary and grammar in database."""

    @override
    def user_words(self, user_id: int) -> list[UserWord]:
        """Retrieve vocabulary words learned by user."""
        words = list(
            Word.objects.filter(user_id=user_id).values(_WORD, _MEANING),
        )
        if not words:
            raise EmptyWordsError
        return words

    @override
    def user_grammars(self, user_id: int) -> list[UserGrammar]:
        """Retrieve grammar points available to user."""
        grammars = list(
            Grammar.objects.filter(user_id=user_id).values(
                _GRAMMAR,
                _MEANING,
            ),
        )
        if not grammars:
            raise EmptyGrammarsError
        return grammars
