import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов в БД'

    def handle(self, *args, **options):
        Ingredient.objects.all().delete()
        file_path = os.path.join(
            os.path.abspath(
                os.path.join(settings.BASE_DIR, os.pardir)
            ), 'data', 'ingredients.csv'
        )
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)

            for row in csv_reader:
                name, measurement_unit = row
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    defaults={'measurement_unit': measurement_unit}
                )

        self.stdout.write(
            self.style.SUCCESS('Ингредиенты успешно импортированы')
        )
