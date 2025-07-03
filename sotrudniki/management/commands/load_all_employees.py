from django.core.management.base import BaseCommand
from datetime import date
from sotrudniki.models import Podrazdelenie, Specialnost, Sotrudnik


class Command(BaseCommand):
    help = 'Загружает всех сотрудников из списка'

    def handle(self, *args, **options):
        # Получаем подразделения
        osnovnoe = Podrazdelenie.objects.get(kod="790")
        stroitelnoe = Podrazdelenie.objects.get(kod="791")

        # Создаем недостающие специальности
        specialnosti = {
            "Альпинист": Specialnost.objects.get_or_create(nazvanie="Альпинист")[0],
            "Подсобный рабочий": Specialnost.objects.get_or_create(nazvanie="Подсобный рабочий")[0],
            "Производитель работ": Specialnost.objects.get_or_create(nazvanie="Производитель работ")[0],
            "Главный инженер": Specialnost.objects.get_or_create(nazvanie="Главный инженер")[0],
            "Газорезчик": Specialnost.objects.get_or_create(nazvanie="Газорезчик")[0],
            "Начальник отдела продаж": Specialnost.objects.get_or_create(nazvanie="Начальник отдела продаж")[0],
            "Альпинист-Газорезчик": Specialnost.objects.get_or_create(nazvanie="Альпинист-Газорезчик")[0],
            "Заместитель генерального директора": Specialnost.objects.get_or_create(nazvanie="Заместитель генерального директора")[0],
            "Помощник начальника участка": Specialnost.objects.get_or_create(nazvanie="Помощник начальника участка")[0],
            "ИТР": Specialnost.objects.get_or_create(nazvanie="ИТР")[0],
            "Специалист подбора кадров": Specialnost.objects.get_or_create(nazvanie="Специалист подбора кадров")[0],
        }

        # Данные сотрудников
        employees_data = [
            ("Аскаров Азамат", "Альпинист", stroitelnoe, date(2024, 12, 10), date(2024, 12, 10)),
            ("Аскаров Адилет Нуржанович", "Альпинист", stroitelnoe, date(2024, 9, 1), date(2024, 9, 1)),
            ("Бусырев Денис Юрьевич", "Подсобный рабочий", stroitelnoe, date(2025, 6, 19), date(2025, 6, 19)),
            ("Васильев Александр Русланович", "Производитель работ", stroitelnoe, date(2024, 9, 2), date(2024, 9, 2)),
            ("Владимиров Виктор Валерьевич", "Главный инженер", stroitelnoe, date(2022, 3, 10), date(2022, 3, 10)),
            ("Дундаев Магомед Ахмедович", "Газорезчик", stroitelnoe, date(2025, 4, 7), date(2025, 4, 7)),
            ("Заочинская Мария Вадимовна", "Начальник отдела продаж", osnovnoe, date(2024, 2, 12), date(2024, 2, 12)),
            ("Захаров Игорь Петрович", "Газорезчик", stroitelnoe, date(2025, 4, 21), date(2025, 4, 21)),
            ("Калчакеев Мурат Куанычбекович", "Альпинист-Газорезчик", stroitelnoe, date(2025, 6, 2), date(2025, 6, 2)),
            ("Масленников Владислав Владимирович", "Заместитель генерального директора", stroitelnoe, date(2024, 12, 28), date(2024, 12, 28)),
            ("Молостов Сергей Сергеевич", "Газорезчик", stroitelnoe, date(2025, 4, 30), date(2025, 4, 30)),
            ("Мухитдинов Умед Хамидович", "Помощник начальника участка", stroitelnoe, date(2024, 12, 13), date(2024, 12, 13)),
            ("Назаров Ходжамурод Зарифходжаевич", "Альпинист-Газорезчик", stroitelnoe, date(2025, 5, 13), date(2025, 5, 13)),
            ("Овчаров Андрей Сергеевич", "ИТР", stroitelnoe, date(2024, 11, 10), date(2024, 11, 10)),
            ("Осипова Алёна Анатольевна", "Специалист подбора кадров", stroitelnoe, date(2022, 10, 20), date(2022, 10, 20)),
            ("Раджабов Кахрамон Хазраткулатович", "Газорезчик", stroitelnoe, date(2025, 5, 3), date(2025, 5, 3)),
            ("Руслан Уулу Ырыскелди", "Альпинист", stroitelnoe, date(2024, 10, 1), date(2024, 10, 1)),
            ("Сасыкеев Беренбек Усеинович", "Газорезчик", stroitelnoe, date(2024, 11, 10), date(2024, 11, 10)),
            ("Симонян Игорь Шотаевич", "Производитель работ", stroitelnoe, date(2022, 2, 9), date(2022, 2, 9)),
            ("Столбов Петр Юрьевич", "Альпинист", stroitelnoe, date(2024, 12, 10), date(2024, 12, 10)),
            ("Тажыханов Эрбол Чыныбекович", "Альпинист", stroitelnoe, date(2025, 1, 6), date(2025, 1, 6)),
            ("Умаров Фаррух Шакирович", "Газорезчик", stroitelnoe, date(2025, 6, 2), date(2025, 6, 2)),
            ("Хахаев Руслан Анатольевич", "Заместитель генерального директора", osnovnoe, date(2021, 8, 13), date(2021, 8, 13)),
            ("Чиглинцев Павел Юрьевич", "Подсобный рабочий", stroitelnoe, date(2024, 12, 10), date(2024, 12, 10)),
            ("Эшпулотов Улугбек Ганишер Угли", "Газорезчик", stroitelnoe, date(2025, 5, 3), date(2025, 5, 3)),
        ]

        created_count = 0
        for fio, spec_name, podrazdelenie, data_priema, data_nachala in employees_data:
            sotrudnik, created = Sotrudnik.objects.get_or_create(
                fio=fio,
                defaults={
                    "data_rozhdeniya": date(1990, 1, 1),  # Примерная дата рождения
                    "specialnost": specialnosti[spec_name],
                    "podrazdelenie": podrazdelenie,
                    "data_priema": data_priema,
                    "data_nachala_raboty": data_nachala
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Создан сотрудник: {fio}')
            else:
                self.stdout.write(f'Сотрудник уже существует: {fio}')

        self.stdout.write(
            self.style.SUCCESS(f'Загрузка завершена. Создано {created_count} новых сотрудников.')
        )