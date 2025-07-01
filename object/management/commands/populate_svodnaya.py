from django.core.management.base import BaseCommand
from django.db.models import Sum
from object.models import Objekt, RaskhodResursa, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam

class Command(BaseCommand):
    help = 'Заполняет сводную таблицу данными из расходов и доходов'

    def handle(self, *args, **options):
        SvodnayaRaskhodDokhodPoDnyam.objects.all().delete()
        
        dates_objects = set()
        
        for raskhod in RaskhodResursa.objects.all():
            objekt = raskhod.fakticheskij_resurs.resurs_po_objektu.objekt
            dates_objects.add((objekt.id, raskhod.data))
            
        for dokhod in DokhodResursa.objects.all():
            objekt = dokhod.fakticheskij_resurs.resurs_po_objektu.objekt
            dates_objects.add((objekt.id, dokhod.data))
        
        for objekt_id, data in dates_objects:
            objekt = Objekt.objects.get(id=objekt_id)
            
            raskhod_total = RaskhodResursa.objects.filter(
                fakticheskij_resurs__resurs_po_objektu__objekt=objekt,
                data=data
            ).aggregate(total=Sum('izraskhodovano'))['total'] or 0
            
            dokhod_total = DokhodResursa.objects.filter(
                fakticheskij_resurs__resurs_po_objektu__objekt=objekt,
                data=data
            ).aggregate(total=Sum('vypolneno'))['total'] or 0
            
            SvodnayaRaskhodDokhodPoDnyam.objects.create(
                objekt=objekt,
                data=data,
                raskhod=raskhod_total,
                dokhod=dokhod_total,
                balans=dokhod_total - raskhod_total
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Создано {len(dates_objects)} записей в сводной таблице')
        )