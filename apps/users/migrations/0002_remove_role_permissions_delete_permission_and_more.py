# Generated by Django 5.2 on 2025-04-18 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='permissions',
        ),
        migrations.DeleteModel(
            name='Permission',
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.JSONField(blank=True, default=list, help_text="List of permission strings granted to this role (e.g., ['content.add_contentinstance', 'content.publish_blogpost']). Use '*' for all permissions.", verbose_name='Permissions'),
        ),
    ]
