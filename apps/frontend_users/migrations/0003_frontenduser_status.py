# Generated by Django 5.2 on 2025-04-18 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend_users', '0002_frontenduser_first_name_frontenduser_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='frontenduser',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('banned', 'Banned')], db_index=True, default='active', help_text='The current status of the front-end user account.', max_length=20, verbose_name='Status'),
        ),
    ]
