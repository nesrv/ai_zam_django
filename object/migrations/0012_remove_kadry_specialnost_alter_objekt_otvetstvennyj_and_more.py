# Generated by Django 5.0 on 2025-07-05 19:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("object", "0011_objekt_is_active"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="kadry",
            name="specialnost",
        ),
        migrations.AlterField(
            model_name="objekt",
            name="otvetstvennyj",
            field=models.CharField(
                default="Иванов Иван Иванович",
                max_length=255,
                verbose_name="Ответственный",
            ),
        ),
        migrations.DeleteModel(
            name="Specialnost",
        ),
        migrations.DeleteModel(
            name="Kadry",
        ),
    ]
