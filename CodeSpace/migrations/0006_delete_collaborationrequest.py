# Generated by Django 5.0.2 on 2024-11-26 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CodeSpace', '0005_project_created_at_alter_project_file_type_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CollaborationRequest',
        ),
    ]
