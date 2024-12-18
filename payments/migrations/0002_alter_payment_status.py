# Generated by Django 5.1.2 on 2024-10-19 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("PAID", "Paid"),
                    ("EXPIRED", "Expired"),
                ],
                max_length=10,
            ),
        ),
    ]
