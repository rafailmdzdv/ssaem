# Copyright © 2026 Rafail Medzhidov <rafayt323@gmail.com>
# SPDX-License-Identifier: MIT

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Grammar',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'grammar',
                    models.CharField(max_length=100, verbose_name='Grammar'),
                ),
                (
                    'meaning',
                    models.CharField(max_length=255, verbose_name='Meaning'),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Created at',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name='grammars',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='User',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Grammar',
                'verbose_name_plural': 'Grammars',
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'word',
                    models.CharField(max_length=100, verbose_name='Word'),
                ),
                (
                    'meaning',
                    models.CharField(max_length=255, verbose_name='Meaning'),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Created at',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name='words',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='User',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Word',
                'verbose_name_plural': 'Words',
            },
        ),
    ]
