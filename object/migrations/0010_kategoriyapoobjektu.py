# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('object', '0009_objekt_organizaciya_alter_dokhodresursa_vypolneno'),
    ]

    operations = [
        migrations.CreateModel(
            name='KategoriyaPoObjektu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kategoriya', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='object.kategoriyaresursa', verbose_name='Категория')),
                ('objekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='object.objekt', verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Категория по объекту',
                'verbose_name_plural': 'Категории по объектам',
                'db_table': 'kategoriya_po_objektu',
            },
        ),
        migrations.AlterUniqueTogether(
            name='kategoriyapoobjektu',
            unique_together={('objekt', 'kategoriya')},
        ),
    ]