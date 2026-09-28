# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from datetime import timedelta
from enum import Enum
from http import HTTPStatus
from typing import final, override

from django.conf import settings
from django.utils import timezone
from dmr import Body, Controller, modify
from dmr.parsers import MultiPartParser
from dmr.plugins.msgspec import MsgspecSerializer
from dmr.security import AuthenticatedHttpRequest
from dmr.security.jwt import request_jwt
from dmr.security.jwt.views import (
    ObtainTokensPayload as DmrObtainTokensPayload,
)
from dmr.security.jwt.views import (
    ObtainTokensResponse,
    ObtainTokensSyncController,
    RefreshTokenPayload,
    RefreshTokenSyncController,
    VerifyTokenPayload,
    VerifyTokenSyncController,
)

from server.apps.auth.auth import jwt_blocklist_auth
from server.apps.auth.forms import UploadAvatarForm
from server.apps.auth.models import User
from server.apps.auth.schemas import (
    ObtainTokensPayload,
    RefreshTokenResponse,
    UpdateUserPayload,
    UpdateUserResponse,
    UploadAvatarResponse,
    UserResponse,
)


class _TokenType(Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


@final
class ObtainTokensController(
    ObtainTokensSyncController[
        MsgspecSerializer,
        ObtainTokensPayload,
        ObtainTokensResponse,
    ],
):
    """Authenticate with email and password to get JWT access and refresh tokens."""  # noqa: E501

    jwt_expiration = timedelta(seconds=settings.JWT_ACCESS_EXPIRES_IN)
    jwt_refresh_expiration = timedelta(seconds=settings.JWT_REFRESH_EXPIRES_IN)

    @override
    def convert_auth_payload(
        self,
        payload: ObtainTokensPayload,
    ) -> DmrObtainTokensPayload:
        return {
            'username': payload['email'],
            'password': payload['password'],
        }

    @override
    def make_api_response(self) -> ObtainTokensResponse:
        now = timezone.now()
        return {
            'access_token': self.create_jwt_token(
                expiration=now + self.jwt_expiration,
                token_type=_TokenType.ACCESS.value,
            ),
            'refresh_token': self.create_jwt_token(
                expiration=now + self.jwt_refresh_expiration,
                token_type=_TokenType.REFRESH.value,
            ),
        }


@final
class RefreshTokenController(
    RefreshTokenSyncController[
        MsgspecSerializer,
        RefreshTokenPayload,
        RefreshTokenResponse,
    ],
):
    """Refresh access token using refresh token."""

    jwt_expiration = timedelta(seconds=settings.JWT_ACCESS_EXPIRES_IN)

    @override
    def convert_refresh_payload(self, payload: RefreshTokenPayload) -> str:
        return payload['refresh_token']

    @override
    def make_api_response(self) -> RefreshTokenResponse:
        now = timezone.now()
        return {
            'access_token': self.create_jwt_token(
                expiration=now + self.jwt_expiration,
                token_type=_TokenType.ACCESS.value,
            ),
        }


@final
class VerifyTokenController(
    VerifyTokenSyncController[MsgspecSerializer, VerifyTokenPayload],
):
    """Validate access token."""

    @override
    def convert_verify_payload(self, payload: VerifyTokenPayload) -> str:
        return payload['access_token']


@final
class LogoutController(Controller[MsgspecSerializer]):
    """Logout and deactivate tokens."""

    auth = (jwt_blocklist_auth,)

    @modify(status_code=HTTPStatus.NO_CONTENT)
    def post(self) -> None:
        """Deactivate tokens."""
        jwt_blocklist_auth.blocklist(
            request_jwt(
                self.request,
                strict=True,
            ),
        )


@final
class UserController(Controller[MsgspecSerializer]):
    """Acquire user information."""

    request: AuthenticatedHttpRequest[User]
    auth = (jwt_blocklist_auth,)

    def get(self) -> UserResponse | None:
        """Retrieve user information."""
        return {
            'email': self.request.user.email,
            'first_name': self.request.user.first_name or '',
            'last_name': self.request.user.last_name or '',
            'source_language': self.request.user.source_language,
            'avatar_url': self.request.build_absolute_uri(
                self.request.user.avatar.url,
            )
            or '',
        }


@final
class UpdateUserController(Controller[MsgspecSerializer]):
    """Update user fields."""

    request: AuthenticatedHttpRequest[User]
    auth = (jwt_blocklist_auth,)

    def patch(self, parsed_body: Body[UpdateUserPayload]) -> UpdateUserResponse:
        """Update user information."""
        User.objects.filter(pk=self.request.user.pk).update(**parsed_body)
        return {'success': True}


@final
class UpdateUserAvatarController(Controller[MsgspecSerializer]):
    """Update the user avatar."""

    parsers = (MultiPartParser(),)
    request: AuthenticatedHttpRequest[User]
    auth = (jwt_blocklist_auth,)

    def post(self) -> UploadAvatarResponse:
        """Upload the new user avatar."""
        form = UploadAvatarForm(
            self.request.POST,
            self.request.FILES,
            instance=self.request.user,
        )
        if form.is_valid():
            form.save()
        return {
            'avatar_url': self.request.build_absolute_uri(
                self.request.user.avatar.url,
            ),
        }


# TODO #217:30min Add the sign up controller
# TODO #217 Add OAuth 2.0
