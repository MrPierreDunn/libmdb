# Generated by Django 3.2 on 2024-02-07 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_user_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('admin', 'admin'), ('moderator', 'moderator')], default='user', max_length=30, verbose_name='Роль пользователя'),
        ),
    ]
