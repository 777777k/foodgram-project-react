# Generated by Django 4.2.6 on 2023-11-15 14:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=150, validators=[django.core.validators.MaxLengthValidator(limit_value=150)], verbose_name='Пароль'),
        ),
    ]
