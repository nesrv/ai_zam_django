from django.core.management.base import BaseCommand
from object.models import Resurs, KategoriyaResursa

class Command(BaseCommand):
    help = 'Добавляет ресурсы в таблицу resurs для kategoriya_resursa_id = 1'

    def handle(self, *args, **options):
        # Получаем категорию ресурса с id = 1
        try:
            kategoriya = KategoriyaResursa.objects.get(id=1)
        except KategoriyaResursa.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Категория ресурса с id=1 не найдена')
            )
            return

        # Список ресурсов для добавления
        resursy = [
            'Альпинист',
            'Альпинист-Газорезчик',
            'Газорезчик',
            'Производитель работ',
            'Главный инженер',
            'Начальник участка',
            'Помощник начальника участка'
        ]

        # Добавляем ресурсы
        created_count = 0
        for resurs_name in resursy:
            resurs, created = Resurs.objects.get_or_create(
                naimenovanie=resurs_name,
                kategoriya_resursa=kategoriya,
                defaults={'edinica_izmereniya': 'час'}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создан ресурс: {resurs_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Ресурс уже существует: {resurs_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {created_count} новых ресурсов')
        )