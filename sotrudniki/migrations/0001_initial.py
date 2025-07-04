# Generated by Django 5.0 on 2025-07-03 09:03

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DokumentySotrudnika",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документы сотрудника",
                "verbose_name_plural": "Документы сотрудников",
            },
        ),
        migrations.CreateModel(
            name="Podrazdelenie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "kod",
                    models.CharField(max_length=50, unique=True, verbose_name="Код"),
                ),
                ("nazvanie", models.CharField(max_length=200, verbose_name="Название")),
            ],
            options={
                "verbose_name": "Подразделение",
                "verbose_name_plural": "Подразделения",
            },
        ),
        migrations.CreateModel(
            name="Specialnost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nazvanie",
                    models.CharField(
                        max_length=200, verbose_name="Название специальности"
                    ),
                ),
            ],
            options={
                "verbose_name": "Специальность",
                "verbose_name_plural": "Специальности",
            },
        ),
        migrations.CreateModel(
            name="VidyDokumentov",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nazvanie", models.CharField(max_length=200, verbose_name="Название")),
                (
                    "tip",
                    models.CharField(
                        choices=[
                            ("dokument", "Документ"),
                            ("protokol", "Протокол"),
                            ("instruktazh", "Инструктаж"),
                        ],
                        max_length=20,
                        verbose_name="Тип",
                    ),
                ),
            ],
            options={
                "verbose_name": "Вид документа",
                "verbose_name_plural": "Виды документов",
            },
        ),
        migrations.CreateModel(
            name="InstrukciiKartochki",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nazvanie", models.CharField(max_length=300, verbose_name="Название")),
                ("tekst_kartochki", models.TextField(verbose_name="Текст карточки")),
                (
                    "soglasovan",
                    models.BooleanField(default=False, verbose_name="Согласован"),
                ),
                (
                    "raspechatn",
                    models.BooleanField(default=False, verbose_name="Распечатан"),
                ),
                (
                    "data_sozdaniya",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Дата создания"
                    ),
                ),
                (
                    "dokumenty_sotrudnika",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sotrudniki.dokumentysotrudnika",
                        verbose_name="Документы сотрудника",
                    ),
                ),
            ],
            options={
                "verbose_name": "Инструкция/карточка",
                "verbose_name_plural": "Инструкции/карточки",
            },
        ),
        migrations.CreateModel(
            name="Instruktazhi",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "data_instruktazha",
                    models.DateField(verbose_name="Дата инструктажа"),
                ),
                (
                    "vid_instruktazha",
                    models.CharField(max_length=100, verbose_name="Вид инструктажа"),
                ),
                (
                    "tekst_instruktazha",
                    models.TextField(verbose_name="Текст инструктажа"),
                ),
                (
                    "instruktor",
                    models.CharField(max_length=150, verbose_name="Инструктор"),
                ),
                (
                    "data_ocherednogo_instruktazha",
                    models.DateField(verbose_name="Дата очередного инструктажа"),
                ),
                (
                    "raspechatn",
                    models.BooleanField(default=False, verbose_name="Распечатан"),
                ),
                (
                    "dokumenty_sotrudnika",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sotrudniki.dokumentysotrudnika",
                        verbose_name="Документы сотрудника",
                    ),
                ),
            ],
            options={
                "verbose_name": "Инструктаж",
                "verbose_name_plural": "Инструктажи",
            },
        ),
        migrations.CreateModel(
            name="ProtokolyObucheniya",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nomer_programmy",
                    models.CharField(max_length=50, verbose_name="Номер программы"),
                ),
                (
                    "nazvanie_kursa",
                    models.CharField(max_length=200, verbose_name="Название курса"),
                ),
                ("tekst_protokola", models.TextField(verbose_name="Текст протокола")),
                ("data_prikaza", models.DateField(verbose_name="Дата приказа")),
                (
                    "data_dopuska",
                    models.DateField(
                        blank=True, null=True, verbose_name="Дата допуска"
                    ),
                ),
                (
                    "data_ocherednoy_proverki",
                    models.DateField(
                        blank=True, null=True, verbose_name="Дата очередной проверки"
                    ),
                ),
                (
                    "registracionnyy_nomer",
                    models.CharField(
                        max_length=50, verbose_name="Регистрационный номер"
                    ),
                ),
                (
                    "raspechatn",
                    models.BooleanField(default=False, verbose_name="Распечатан"),
                ),
                (
                    "dokumenty_sotrudnika",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sotrudniki.dokumentysotrudnika",
                        verbose_name="Документы сотрудника",
                    ),
                ),
            ],
            options={
                "verbose_name": "Протокол обучения",
                "verbose_name_plural": "Протоколы обучения",
            },
        ),
        migrations.CreateModel(
            name="Sotrudnik",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fio", models.CharField(max_length=300, verbose_name="ФИО")),
                ("data_rozhdeniya", models.DateField(verbose_name="Дата рождения")),
                ("data_priema", models.DateField(verbose_name="Дата приема")),
                (
                    "data_nachala_raboty",
                    models.DateField(verbose_name="Дата начала работы"),
                ),
                (
                    "podrazdelenie",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="sotrudniki.podrazdelenie",
                        verbose_name="Подразделение",
                    ),
                ),
                (
                    "specialnost",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="sotrudniki.specialnost",
                        verbose_name="Специальность",
                    ),
                ),
            ],
            options={
                "verbose_name": "Сотрудник",
                "verbose_name_plural": "Сотрудники",
            },
        ),
        migrations.AddField(
            model_name="dokumentysotrudnika",
            name="sotrudnik",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="sotrudniki.sotrudnik",
                verbose_name="Сотрудник",
            ),
        ),
    ]
