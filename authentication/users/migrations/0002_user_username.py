# Generated by Django 3.2.19 on 2024-04-15 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default=models.CharField(max_length=255), max_length=255, unique=True),
        ),
    ]
