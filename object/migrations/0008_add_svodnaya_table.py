from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('object', '0007_rename_dokhod_to_vypolneno'),
    ]

    operations = [
        migrations.CreateModel(
            name='SvodnayaRaskhodDokhodPoDnyam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Дата')),
                ('raskhod', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Расход')),
                ('dokhod', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Доход')),
                ('balans', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Баланс')),
                ('objekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='object.objekt', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Сводная по дням',
                'verbose_name_plural': 'Сводная по дням',
                'db_table': 'svodnaya_raskhod_dokhod_po_dnyam',
            },
        ),
        migrations.AlterUniqueTogether(
            name='svodnayaraskhoddokhodpodnyam',
            unique_together={('objekt', 'data')},
        ),
    ]