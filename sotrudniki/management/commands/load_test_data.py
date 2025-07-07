from django.core.management.base import BaseCommand
from datetime import date
from sotrudniki.models import Podrazdelenie, Specialnost, Sotrudnik, InstrukciiKartochki, ProtokolyObucheniya, Instruktazhi


class Command(BaseCommand):
    help = 'Загружает тестовые данные сотрудников'

    def handle(self, *args, **options):
        # Создаем подразделения
        osnovnoe, _ = Podrazdelenie.objects.get_or_create(
            kod="790",
            defaults={"nazvanie": "Основное подразделение"}
        )
        
        stroitelnoe, _ = Podrazdelenie.objects.get_or_create(
            kod="791", 
            defaults={"nazvanie": "Строительное управление"}
        )

        # Создаем специальности
        alpinist_gazorezchik, _ = Specialnost.objects.get_or_create(
            nazvanie="Альпинист-Газорезчик"
        )
        alpinist, _ = Specialnost.objects.get_or_create(
            nazvanie="Альпинист"
        )
        gazorezchik, _ = Specialnost.objects.get_or_create(
            nazvanie="Газорезчик"
        )
        proizvoditel, _ = Specialnost.objects.get_or_create(
            nazvanie="Производитель работ"
        )

        # Создаем сотрудника Аманбек Уулу Эмирлан
        sotrudnik, created = Sotrudnik.objects.get_or_create(
            fio="Аманбек Уулу Эмирлан",
            defaults={
                "data_rozhdeniya": date(2000, 6, 29),
                "specialnost": alpinist_gazorezchik,
                "podrazdelenie": stroitelnoe,
                "data_priema": date(2025, 1, 27),
                "data_nachala_raboty": date(2025, 1, 27)
            }
        )

        if created:
            # Создаем инструкции и карточки
            InstrukciiKartochki.objects.create(
                dokumenty_sotrudnika=dokumenty,
                nazvanie="Должностная инструкция",
                tekst_kartochki="Должностная инструкция для альпиниста-газорезчика"
            )
            
            InstrukciiKartochki.objects.create(
                dokumenty_sotrudnika=dokumenty,
                nazvanie="Личная карточка работника",
                tekst_kartochki="Личная карточка работника"
            )
            
            InstrukciiKartochki.objects.create(
                dokumenty_sotrudnika=dokumenty,
                nazvanie="Личная карточка учета выдачи СИЗ",
                tekst_kartochki="Карточка учета средств индивидуальной защиты"
            )
            
            InstrukciiKartochki.objects.create(
                dokumenty_sotrudnika=dokumenty,
                nazvanie="Карта оценки проф. рисков",
                tekst_kartochki="Карта оценки профессиональных рисков"
            )

            # Создаем протоколы обучения
            ProtokolyObucheniya.objects.create(
                dokumenty_sotrudnika=dokumenty,
                nomer_programmy="2025/СТ.02-0011",
                nazvanie_kursa="Стажировка на рабочем месте",
                tekst_protokola="Протокол стажировки на рабочем месте",
                data_prikaza=date(2025, 6, 25),
                data_dopuska=date(2025, 6, 27),
                data_ocherednoy_proverki=date(2025, 6, 30),
                registracionnyy_nomer="-"
            )
            
            ProtokolyObucheniya.objects.create(
                dokumenty_sotrudnika=dokumenty,
                nomer_programmy="2025/В.07-0016",
                nazvanie_kursa="В-Безопасные методы и приемы выполнения ремонтных, монтажных и демонтажных работ зданий и сооружений",
                tekst_protokola="Протокол обучения безопасным методам работы",
                data_prikaza=date(2025, 6, 25),
                data_dopuska=date(2025, 6, 25),
                data_ocherednoy_proverki=date(2026, 6, 24),
                registracionnyy_nomer="129091967"
            )

            # Создаем инструктаж
            Instruktazhi.objects.create(
                dokumenty_sotrudnika=dokumenty,
                data_instruktazha=date(2025, 1, 27),
                vid_instruktazha="Первичный",
                tekst_instruktazha="Первичный инструктаж по охране труда",
                instruktor="Симонян Игорь Шотаевич, Производитель работ",
                data_ocherednogo_instruktazha=date(2025, 7, 26)
            )

            self.stdout.write(
                self.style.SUCCESS(f'Успешно создан сотрудник: {sotrudnik.fio}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Сотрудник уже существует: {sotrudnik.fio}')
            )

        self.stdout.write(self.style.SUCCESS('Загрузка тестовых данных завершена'))