# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import final, override

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

_NAME_MAX_LENGTH = 150
_SURNAME_MAX_LENGTH = _NAME_MAX_LENGTH


@final
class UserManager(BaseUserManager['User']):
    def create_user(
        self,
        email: str,
        password: str,
        **extra_fields: object,
    ) -> 'User':
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user_object(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields: object,
    ) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user_object(email, password, **extra_fields)

    def _create_user_object(
        self,
        email: str,
        password: str,
        **extra_fields: object,
    ) -> 'User':
        user = self.model(
            email=email,
            **extra_fields,
        )
        user.password = make_password(password)
        user.save()
        return user


@final
class User(AbstractBaseUser, PermissionsMixin):
    class Language(models.TextChoices):
        RU = 'ru', _('Russian')
        EN = 'en', _('English')

    email = models.EmailField(_('Email address'), unique=True)
    first_name = models.CharField(
        _('First name'),
        max_length=_NAME_MAX_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=_SURNAME_MAX_LENGTH,
        blank=True,
    )
    is_staff = models.BooleanField(
        _('Is staff'),
        default=False,
    )
    source_language = models.CharField(
        _('Source language'),
        choices=Language.choices,
        default=Language.EN,
    )
    avatar = models.ImageField(upload_to='user/avatar/')

    USERNAME_FIELD = 'email'

    objects = UserManager()

    @override
    def clean(self) -> None:
        self.email = self.__class__.objects.normalize_email(self.email)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
