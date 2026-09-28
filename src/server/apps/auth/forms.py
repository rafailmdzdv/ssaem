# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import final

from django import forms

from server.apps.auth import models


@final
class UploadAvatarForm(forms.ModelForm[models.User]):
    """Form used to upload a user's avatar."""

    @final
    class Meta:
        model = models.User
        fields = ('avatar',)
