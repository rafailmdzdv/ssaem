# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from dmr.exceptions import NotAuthenticatedError
from dmr.security.jwt.token import JWToken
from jwt.exceptions import InvalidKeyError

_ALGORITHM = 'HS256'


@pytest.mark.django_db
def test_token_encode_decode_roundtrip() -> None:
    token = JWToken(
        sub='42',
        exp=timezone.now() + timedelta(hours=1),
        jti='unique-id-1',
        extras={'type': 'access'},
    )
    encoded = token.encode(secret=settings.SECRET_KEY, algorithm=_ALGORITHM)
    decoded = JWToken.decode(
        encoded,
        secret=settings.SECRET_KEY,
        algorithm=_ALGORITHM,
    )

    assert decoded.sub == '42'
    assert decoded.jti == 'unique-id-1'
    assert decoded.extras['type'] == 'access'


@pytest.mark.django_db
def test_token_with_refresh_type() -> None:
    token = JWToken(
        sub='1',
        exp=timezone.now() + timedelta(days=7),
        jti='refresh-id',
        extras={'type': 'refresh'},
    )
    encoded = token.encode(secret=settings.SECRET_KEY, algorithm=_ALGORITHM)
    decoded = JWToken.decode(
        encoded,
        secret=settings.SECRET_KEY,
        algorithm=_ALGORITHM,
    )

    assert decoded.extras['type'] == 'refresh'


@pytest.mark.django_db
def test_token_with_past_expiry_fails_at_creation() -> None:
    with pytest.raises(
        ValueError,
        match='exp value must be a datetime in the future',
    ):
        JWToken(
            sub='1',
            exp=timezone.now() - timedelta(hours=1),
            jti='expired-id',
            extras={'type': 'access'},
        )


@pytest.mark.django_db
def test_token_decode_expired_token() -> None:
    import jwt as pyjwt  # noqa: PLC0415

    payload = {
        'sub': '1',
        'exp': (timezone.now() - timedelta(hours=1)).timestamp(),
        'iat': (timezone.now() - timedelta(hours=2)).timestamp(),
        'jti': 'expired-decode-id',
        'type': 'access',
    }
    encoded = pyjwt.encode(
        payload,
        key=settings.SECRET_KEY,
        algorithm=_ALGORITHM,
    )

    with pytest.raises(NotAuthenticatedError):
        JWToken.decode(
            encoded,
            secret=settings.SECRET_KEY,
            algorithm=_ALGORITHM,
        )


@pytest.mark.django_db
def test_wrong_secret_raises() -> None:
    token = JWToken(
        sub='1',
        exp=timezone.now() + timedelta(hours=1),
        jti='wrong-secret-id',
        extras={'type': 'access'},
    )
    long_key = 'correct-secret-key-that-is-long-enough-for-hmac'
    encoded = token.encode(secret=long_key, algorithm=_ALGORITHM)

    with pytest.raises(InvalidKeyError):
        JWToken.decode(encoded, secret='wrong-secret', algorithm=_ALGORITHM)


@pytest.mark.django_db
def test_token_preserves_issuer() -> None:
    token = JWToken(
        sub='1',
        exp=timezone.now() + timedelta(hours=1),
        iss='my-app',
        jti='iss-test',
        extras={'type': 'access'},
    )
    encoded = token.encode(secret=settings.SECRET_KEY, algorithm=_ALGORITHM)
    decoded = JWToken.decode(
        encoded,
        secret=settings.SECRET_KEY,
        algorithm=_ALGORITHM,
    )

    assert decoded.iss == 'my-app'


@pytest.mark.django_db
def test_token_preserves_audiences() -> None:
    token = JWToken(
        sub='1',
        exp=timezone.now() + timedelta(hours=1),
        aud='my-audience',
        jti='aud-test',
        extras={'type': 'access'},
    )
    encoded = token.encode(secret=settings.SECRET_KEY, algorithm=_ALGORITHM)
    decoded = JWToken.decode(
        encoded,
        secret=settings.SECRET_KEY,
        algorithm=_ALGORITHM,
    )

    assert decoded.aud == 'my-audience'
