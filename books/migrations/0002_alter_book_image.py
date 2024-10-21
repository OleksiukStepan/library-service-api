# Generated by Django 5.1.2 on 2024-10-21 11:01

import books.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=books.models.books_image_file_path,
                validators=[books.models.validate_image_size],
            ),
        ),
    ]