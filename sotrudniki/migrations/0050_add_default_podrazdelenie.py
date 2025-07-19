from django.db import migrations

def add_default_podrazdelenie(apps, schema_editor):
    Organizaciya = apps.get_model('sotrudniki', 'Organizaciya')
    Podrazdelenie = apps.get_model('sotrudniki', 'Podrazdelenie')
    
    # Создаем или получаем подразделение "Линейные сотрудники"
    default_podrazdelenie, created = Podrazdelenie.objects.get_or_create(
        kod='792',
        defaults={'nazvanie': 'Линейные сотрудники'}
    )
    
    # Если подразделение уже существует, но название не соответствует, обновляем его
    if not created and default_podrazdelenie.nazvanie != 'Линейные сотрудники':
        default_podrazdelenie.nazvanie = 'Линейные сотрудники'
        default_podrazdelenie.save()
    
    # Добавляем подразделение во все организации, у которых его нет
    for org in Organizaciya.objects.all():
        if not Podrazdelenie.objects.filter(organizaciya=org).exists():
            # Создаем копию подразделения для каждой организации
            Podrazdelenie.objects.create(
                organizaciya=org,
                kod=f"{org.id}-792",
                nazvanie='Линейные сотрудники'
            )

class Migration(migrations.Migration):
    dependencies = [
        ('sotrudniki', '0049_remove_sotrudnik_objekty'),
    ]

    operations = [
        migrations.RunPython(add_default_podrazdelenie),
    ]