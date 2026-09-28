# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT
from typing import Final, final

from django.contrib import admin

from server.apps.exercises.models import Grammar, Word

_WORD: Final = 'word'
_GRAMMAR: Final = 'grammar'
_MEANING: Final = 'meaning'
_USER: Final = 'user'
_CREATED_AT: Final = 'created_at'


@final
@admin.register(Word)
class WordAdmin(admin.ModelAdmin[Word]):
    list_display = (_WORD, _MEANING, _USER, _CREATED_AT)
    search_fields = (_WORD, _MEANING)
    list_filter = (_CREATED_AT,)


@final
@admin.register(Grammar)
class GrammarAdmin(admin.ModelAdmin[Grammar]):
    list_display = (_GRAMMAR, _MEANING, _USER, _CREATED_AT)
    search_fields = (_GRAMMAR, _MEANING)
    list_filter = (_CREATED_AT,)
