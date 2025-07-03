from django.core.management.base import BaseCommand
from sotrudniki.models import Sotrudnik, Podrazdelenie, Specialnost


class Command(BaseCommand):
    help = 'Проверяет данные сотрудников в базе'

    def handle(self, *args, **options):
        total_employees = Sotrudnik.objects.count()
        self.stdout.write(f'Всего сотрудников в базе: {total_employees}')
        
        # Статистика по подразделениям
        self.stdout.write('\nСтатистика по подразделениям:')
        for podrazdelenie in Podrazdelenie.objects.all():
            count = Sotrudnik.objects.filter(podrazdelenie=podrazdelenie).count()
            self.stdout.write(f'  {podrazdelenie.nazvanie}: {count} сотрудников')
        
        # Статистика по специальностям
        self.stdout.write('\nСтатистика по специальностям:')
        for specialnost in Specialnost.objects.all():
            count = Sotrudnik.objects.filter(specialnost=specialnost).count()
            self.stdout.write(f'  {specialnost.nazvanie}: {count} сотрудников')
        
        # Последние 5 добавленных сотрудников
        self.stdout.write('\nПоследние 5 сотрудников:')
        for sotrudnik in Sotrudnik.objects.order_by('-id')[:5]:
            self.stdout.write(f'  {sotrudnik.fio} - {sotrudnik.specialnost} ({sotrudnik.podrazdelenie})')