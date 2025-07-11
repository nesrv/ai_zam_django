from django.core.management.base import BaseCommand
from django.db import transaction
from object.models import Objekt, ResursyPoObjektu, SvodnayaRaskhodDokhodPoDnyam, KategoriyaPoObjektu

class Command(BaseCommand):
    help = 'Удалить объект с указанным ID'

    def add_arguments(self, parser):
        parser.add_argument('objekt_id', type=int, help='ID объекта для удаления')

    def handle(self, *args, **options):
        objekt_id = options['objekt_id']
        
        try:
            with transaction.atomic():
                objekt = Objekt.objects.get(id=objekt_id)
                objekt_name = objekt.nazvanie
                
                # Удаляем связанные записи
                ResursyPoObjektu.objects.filter(objekt=objekt).delete()
                SvodnayaRaskhodDokhodPoDnyam.objects.filter(objekt=objekt).delete()
                KategoriyaPoObjektu.objects.filter(objekt=objekt).delete()
                
                # Удаляем сам объект
                objekt.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Объект "{objekt_name}" с ID {objekt_id} успешно удален')
                )
        except Objekt.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Объект с ID {objekt_id} не найден')
            )