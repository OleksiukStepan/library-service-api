# Generated by Django 5.1.2 on 2024-10-18 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="telegram_chat_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]