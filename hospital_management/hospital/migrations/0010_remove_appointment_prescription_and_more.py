# Generated by Django 5.1.5 on 2025-02-10 10:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hospital", "0009_appointment_prescription"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="appointment",
            name="prescription",
        ),
        migrations.AddField(
            model_name="medicalrecord",
            name="prescription",
            field=models.TextField(blank=True, null=True),
        ),
    ]
