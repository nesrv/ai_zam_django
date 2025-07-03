from django.core.management.base import BaseCommand
from django.db.models import Sum, F
from datetime import datetime, timedelta
from object.models import (
    RaskhodResursa, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam, 
    Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu
)

class Command(BaseCommand):
    help = 'Собирает данные из итоговых строк расходов и доходов по дням в svodnaya_raskhod_dokhod_po_dnyam'

    def handle(self, *args, **options):
        self.stdout.write('Начинаем сбор данных из итоговых строк...')
        
        # Очищаем сводную таблицу
        deleted_count = SvodnayaRaskhodDokhodPoDnyam.objects.all().delete()[0]
        self.stdout.write(f'Удалено {deleted_count} старых записей')
        
        # Получаем все объекты
        objekty = Objekt.objects.all()
        
        # Создаем 20 дней для анализа
        today = datetime.now().date()
        days = [today - timedelta(days=i) for i in range(20)]
        
        created_count = 0
        
        for objekt in objekty:
            self.stdout.write(f'Обрабатываем объект: {objekt.nazvanie}')
            
            for day in days:
                # Вычисляем итоговые фактические расходы по дням
                total_raskhod = 0.0
                
                # Получаем все ресурсы объекта (кроме подрядных организаций)
                resources = ResursyPoObjektu.objects.filter(
                    objekt=objekt
                ).exclude(
                    resurs__kategoriya_resursa__nazvanie='Подрядные организации'
                ).select_related('resurs', 'resurs__kategoriya_resursa')
                
                for resource in resources:
                    try:
                        fr = FakticheskijResursPoObjektu.objects.get(resurs_po_objektu=resource)
                        rashody = RaskhodResursa.objects.filter(
                            fakticheskij_resurs=fr,
                            data=day
                        )
                        for rashod in rashody:
                            expense_amount = float(resource.cena) * float(rashod.izraskhodovano)
                            total_raskhod += expense_amount
                    except FakticheskijResursPoObjektu.DoesNotExist:
                        continue
                
                # Вычисляем итоговые фактические доходы по дням
                total_dokhod = 0.0
                
                # Получаем ресурсы подрядных организаций
                income_resources = ResursyPoObjektu.objects.filter(
                    objekt=objekt,
                    resurs__kategoriya_resursa__nazvanie='Подрядные организации'
                ).select_related('resurs', 'resurs__kategoriya_resursa')
                
                for resource in income_resources:
                    try:
                        fr = FakticheskijResursPoObjektu.objects.get(resurs_po_objektu=resource)
                        dokhody = DokhodResursa.objects.filter(
                            fakticheskij_resurs=fr,
                            data=day
                        )
                        for dokhod in dokhody:
                            income_amount = float(resource.cena) * float(dokhod.vypolneno)
                            total_dokhod += income_amount
                    except FakticheskijResursPoObjektu.DoesNotExist:
                        continue
                
                # Создаем запись только если есть расходы или доходы
                if total_raskhod > 0 or total_dokhod > 0:
                    balans = total_dokhod - total_raskhod
                    
                    SvodnayaRaskhodDokhodPoDnyam.objects.create(
                        objekt=objekt,
                        data=day,
                        raskhod=total_raskhod,
                        dokhod=total_dokhod,
                        balans=balans
                    )
                    created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} записей в сводной таблице')
        )