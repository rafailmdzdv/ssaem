# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

"""LLM configuration settings."""

from server.settings.components import config

# Gemini API configuration:
GEMINI_API_KEY: str = config('GEMINI_API_KEY', default='')
GEMINI_MODEL: str = config('GEMINI_MODEL', default='gemini-2.5-flash')
