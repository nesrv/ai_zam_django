from django.core.management.base import BaseCommand
from sotrudniki.models import Organizaciya, Sotrudnik


class Command(BaseCommand):
    help = 'Создает организацию и привязывает к ней всех сотрудников'

    def handle(self, *args, **options):
        # Создаем организацию ООО "Развитие"
        organizaciya, created = Organizaciya.objects.get_or_create(
            inn="1234567890",
            defaults={"nazvanie": "ООО \"Развитие\""}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Создана организация: {organizaciya.nazvanie}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Организация уже существует: {organizaciya.nazvanie}')
            )
        
        # Привязываем всех сотрудников к этой организации
        sotrudniki_bez_org = Sotrudnik.objects.filter(organizaciya__isnull=True)
        count = sotrudniki_bez_org.count()
        
        if count > 0:
            sotrudniki_bez_org.update(organizaciya=organizaciya)
            self.stdout.write(
                self.style.SUCCESS(f'Привязано {count} сотрудников к организации {organizaciya.nazvanie}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Все сотрудники уже привязаны к организациям')
            )
        
        # Статистика
        total_sotrudniki = Sotrudnik.objects.filter(organizaciya=organizaciya).count()
        self.stdout.write(
            self.style.SUCCESS(f'Всего сотрудников в организации {organizaciya.nazvanie}: {total_sotrudniki}')
        )