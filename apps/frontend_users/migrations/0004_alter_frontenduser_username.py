# Generated by Django 5.2 on 2025-04-18 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend_users', '0003_frontenduser_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frontenduser',
            name='username',
            field=models.CharField(help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, verbose_name='Username'),
        ),
    ]
