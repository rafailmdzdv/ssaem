# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from typing import Final, final

from django.contrib.auth import get_user_model
from dmr.security.jwt import JWTSyncAuth
from dmr.security.jwt.blocklist import JWTokenBlocklistSyncMixin

User = get_user_model()


@final
class JWTAuthWithBlocklist(JWTokenBlocklistSyncMixin, JWTSyncAuth):
    """Authentication class that can blacklist tokens."""


jwt_blocklist_auth: Final = JWTAuthWithBlocklist()
