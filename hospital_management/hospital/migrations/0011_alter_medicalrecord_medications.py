# Generated by Django 5.1.5 on 2025-02-10 12:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hospital", "0010_remove_appointment_prescription_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="medicalrecord",
            name="medications",
            field=models.TextField(),
        ),
    ]
