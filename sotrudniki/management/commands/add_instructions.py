from django.core.management.base import BaseCommand
from datetime import timedelta
from sotrudniki.models import Sotrudnik, DokumentySotrudnika, Instruktazhi


class Command(BaseCommand):
    help = 'Добавляет инструктажи всем сотрудникам'

    def handle(self, *args, **options):
        for sotrudnik in Sotrudnik.objects.all():
            dokumenty, created = DokumentySotrudnika.objects.get_or_create(sotrudnik=sotrudnik)
            
            # Дата инструктажа = дата начала работы
            data_instruktazha = sotrudnik.data_nachala_raboty
            # Дата очередного инструктажа = дата инструктажа + 6 месяцев
            data_ocherednogo = data_instruktazha + timedelta(days=180)
            
            Instruktazhi.objects.get_or_create(
                dokumenty_sotrudnika=dokumenty,
                data_instruktazha=data_instruktazha,
                defaults={
                    'vid_instruktazha': 'Первичный',
                    'tekst_instruktazha': 'Первичный инструктаж по охране труда',
                    'instruktor': 'Симонян Игорь Шотаевич, Производитель работ',
                    'data_ocherednogo_instruktazha': data_ocherednogo
                }
            )
            
            self.stdout.write(f'Добавлен инструктаж для {sotrudnik.fio}')

        self.stdout.write(self.style.SUCCESS('Инструктажи добавлены всем сотрудникам'))