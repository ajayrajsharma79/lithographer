# Generated by Django 5.2 on 2025-04-18 06:53

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrontEndUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(help_text='Used for login and notifications.', max_length=254, unique=True, verbose_name='email address')),
                ('display_name', models.CharField(help_text='Publicly visible name (e.g., for comments).', max_length=150, unique=True, verbose_name='Display Name')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into the Django admin site (always False for FrontEndUser).', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='frontenduser_set', related_query_name='frontenduser', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='frontenduser_set', related_query_name='frontenduser', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Front-End User',
                'verbose_name_plural': 'Front-End Users',
                'ordering': ['display_name'],
            },
        ),
    ]
