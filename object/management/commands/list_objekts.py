from django.core.management.base import BaseCommand
from object.models import Objekt

class Command(BaseCommand):
    help = 'Показать все объекты'

    def handle(self, *args, **options):
        objekts = Objekt.objects.all()
        if objekts:
            self.stdout.write("Список объектов:")
            for obj in objekts:
                self.stdout.write(f"ID: {obj.id}, Название: {obj.nazvanie}")
        else:
            self.stdout.write("Объекты не найдены")