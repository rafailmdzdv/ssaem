# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import final


class UserGenerationError(Exception):
    """Base user generation error (401)."""

    message: str


@final
class EmptyWordsError(UserGenerationError):
    """Raised if there are no any words."""

    message = 'There is no any words. Please, fill it into settings.'


@final
class EmptyGrammarsError(UserGenerationError):
    """Raised if there are no any grammars."""

    message = 'There is no any grammars. Please, fill it into settings.'
