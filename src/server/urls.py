# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

"""
Main URL mapping configuration file.

Include other URLConfs from external apps using method `include()`.

It is also a good practice to keep a single URL to the root index page.

This examples uses Django's default media
files serving technique in development.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.admindocs import urls as admindocs_urls
from django.urls import include
from django.views.generic import TemplateView
from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, SwaggerView
from dmr.openapi.views.yaml import OpenAPIYamlView
from dmr.routing import Router, path
from health_check.views import HealthCheckView

from server.apps.auth import urls as auth_urls
from server.apps.exercises import urls as exercise_urls

admin.autodiscover()

router = Router(
    'api/v1/',
    (
        auth_urls.auth_router.to_urlpatterns(namespace='auth'),
        auth_urls.user_router.to_urlpatterns(namespace='user'),
        exercise_urls.exercise_router.to_urlpatterns(namespace='exercises'),
    ),
)
schema = build_schema(router)


urlpatterns = (
    router.to_urlpatterns(namespace='api', app_name='server'),
    # Health checks:
    path(
        'health/',
        HealthCheckView.as_view(
            checks=[
                'health_check.Cache',
                'health_check.Database',
                'health_check.Storage',
            ],
        ),
        name='health_check',
    ),
    path(
        'docs/openapi.json/',
        OpenAPIJsonView.as_view(schema),
        name='openapi_json',
    ),
    path(
        'docs/openapi.yaml/',
        OpenAPIYamlView.as_view(schema),
        name='openapi_yaml',
    ),
    path('docs/', SwaggerView.as_view(schema), name='swagger'),
    # django-admin:
    path('admin/doc/', include(admindocs_urls)),
    path('admin/', admin.site.urls),
    # Text and xml static files:
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='common/txt/robots.txt',
            content_type='text/plain',
        ),
        name='robots_txt',
    ),
    path(
        'humans.txt',
        TemplateView.as_view(
            template_name='common/txt/humans.txt',
            content_type='text/plain',
        ),
        name='humans_txt',
    ),
)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns = (
        # URLs specific only to django-debug-toolbar:
        path('__debug__/', include(debug_toolbar.urls)),
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    )
