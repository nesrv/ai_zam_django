from django.db import migrations

def add_default_podrazdelenie_to_organizacii(apps, schema_editor):
    Organizaciya = apps.get_model('sotrudniki', 'Organizaciya')
    Podrazdelenie = apps.get_model('sotrudniki', 'Podrazdelenie')
    OrganizaciyaPodrazdelenie = apps.get_model('sotrudniki', 'OrganizaciyaPodrazdelenie')
    
    # Создаем или получаем подразделение "Линейные сотрудники"
    default_podrazdelenie, created = Podrazdelenie.objects.get_or_create(
        kod='792',
        defaults={'nazvanie': 'Линейные сотрудники'}
    )
    
    # Если подразделение уже существует, но название не соответствует, обновляем его
    if not created and default_podrazdelenie.nazvanie != 'Линейные сотрудники':
        default_podrazdelenie.nazvanie = 'Линейные сотрудники'
        default_podrazdelenie.save()
    
    # Добавляем подразделение во все организации
    for org in Organizaciya.objects.all():
        OrganizaciyaPodrazdelenie.objects.get_or_create(
            organizaciya=org,
            podrazdelenie=default_podrazdelenie,
            defaults={'is_default': True}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('sotrudniki', '0052_add_organizaciya_podrazdelenie'),
    ]

    operations = [
        migrations.RunPython(add_default_podrazdelenie_to_organizacii),
    ]