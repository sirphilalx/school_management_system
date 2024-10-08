# Generated by Django 5.1.1 on 2024-10-07 22:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(limit_choices_to={'role': 'teacher'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='classes_taught', to=settings.AUTH_USER_MODEL),
        ),
    ]
