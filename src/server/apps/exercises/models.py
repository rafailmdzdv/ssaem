# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT
from typing import Final, final, override

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

_WORD_MAX_LENGTH: Final = 100
_MEANING_MAX_LENGTH: Final = 255


@final
class Word(models.Model):
    """Vocabulary word learned by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='words',
        verbose_name=_('User'),
    )
    word = models.CharField(
        _('Word'),
        max_length=_WORD_MAX_LENGTH,
    )
    meaning = models.CharField(
        _('Meaning'),
        max_length=_MEANING_MAX_LENGTH,
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _('Word')
        verbose_name_plural = _('Words')

    @override
    def __str__(self) -> str:
        return f'{self.word} ({self.meaning})'


@final
class Grammar(models.Model):
    """Grammar structure learned by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grammars',
        verbose_name=_('User'),
    )
    grammar = models.CharField(
        _('Grammar'),
        max_length=_WORD_MAX_LENGTH,
    )
    meaning = models.CharField(
        _('Meaning'),
        max_length=_MEANING_MAX_LENGTH,
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _('Grammar')
        verbose_name_plural = _('Grammars')

    @override
    def __str__(self) -> str:
        return f'{self.grammar} ({self.meaning})'
