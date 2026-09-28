# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

# NOTE: simple layers go on top!

from collections.abc import Callable
from typing import Any

import punq


def _global_namespace() -> dict[str, Any]:
    from django.conf import LazySettings  # noqa: F401
    from django.core.cache import BaseCache  # noqa: F401

    return locals()  # noqa: WPS421


def _create_injector[Thing](
    container: punq.Container,
    localns: dict[str, Any],
) -> Callable[[Thing], Thing]:
    # We need to provide the same string names as we do in the definition.
    localns.pop('container')
    localns.update(_global_namespace())
    container.registrations._localns.update(localns)  # noqa: SLF001
    return lambda service: service


def _inject_django(container: punq.Container) -> None:
    from django.conf import LazySettings, settings

    # Django:
    container.register(
        LazySettings,
        instance=settings,
        scope=punq.Scope.singleton,
    )


def _inject_exercises(container: punq.Container) -> None:
    from django.conf import settings

    from server.apps.exercises.infra.gemini import (
        GeminiLLMClient,
    )
    from server.apps.exercises.infra.repositories import (
        DjangoLearningDataRepository,
    )
    from server.apps.exercises.logic.interfaces import (
        LearningDataRepository,
        LLMClient,
    )
    from server.apps.exercises.logic.services import (
        ExerciseService,
    )

    gemini_client = GeminiLLMClient(
        api_key=getattr(settings, 'GEMINI_API_KEY', ''),
        model=getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash'),
    )
    container.register(
        LLMClient,
        instance=gemini_client,
        scope=punq.Scope.singleton,
    )
    repo = DjangoLearningDataRepository()
    container.register(
        LearningDataRepository,
        instance=repo,
        scope=punq.Scope.singleton,
    )
    container.register(
        ExerciseService,
        instance=ExerciseService(gemini_client, repo),
        scope=punq.Scope.singleton,
    )


def populate_dependencies(container: punq.Container) -> punq.Container:
    """Populates dependencies for the container."""
    # Deps:
    _inject_django(container)
    # Apps:
    _inject_exercises(container)
    return container
