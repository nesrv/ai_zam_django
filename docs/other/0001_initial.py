from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='SpecodezhaSiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazvanie', models.CharField(max_length=255, verbose_name='Название')),
                ('edinica_izmereniya', models.CharField(max_length=50, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Спецодежда и СИЗ',
                'verbose_name_plural': 'Спецодежда и СИЗ',
            },
        ),
    ]