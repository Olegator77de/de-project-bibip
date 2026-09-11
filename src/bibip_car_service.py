from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale
from datetime import datetime
from decimal import Decimal

import os


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        models_file = os.path.join(self.root_directory_path, 'models.txt')
        models_index_file = os.path.join(self.root_directory_path,
                                         'models_index.txt')

        # Пишем индекс в память
        models_index = []
        if os.path.exists(models_index_file):
            with open(models_index_file, 'r') as f:
                for line in f:
                    model_id, line_num = line.strip().split(',')
                    models_index.append((int(model_id), int(line_num)))

        # Номер новой строки
        line_number = len(models_index)

        # Запись данных
        model_line = (
            f'{model.id};{model.name};{model.brand}'
        ).ljust(500) + '\n'
        with open(models_file, 'a') as f:
            f.write(model_line)

        # Обновление индекса в памяти
        models_index.append((model.id, line_number))
        models_index.sort()

        # Перезапись индекса
        with open(models_index_file, 'w') as f:
            for current_id, current_num in models_index:
                f.write(f'{current_id},{current_num}\n')

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        cars_index_file = (
            os.path.join(self.root_directory_path, 'cars_index.txt')
        )
        # Пишем индекс в память
        cars_index = []
        if os.path.exists(cars_index_file):
            with open(cars_index_file, 'r') as f:
                for line in f:
                    vin, line_num = line.strip().split(',')
                    cars_index.append((vin, int(line_num)))

        # Номер новой строки
        line_number = len(cars_index)

        # Запись данных
        car_line = (
            f'{car.vin};{car.model};{car.price};'
            f'{car.date_start.date()};{car.status.value}'
        ).ljust(500) + '\n'
        with open(cars_file, 'a') as f:
            f.write(car_line)

        # Обновление индекса в памяти
        cars_index.append((car.vin, line_number))
        cars_index.sort()

        # Перезапись индекса
        with open(cars_index_file, 'w') as f:
            for current_vin, current_num in cars_index:
                f.write(f'{current_vin},{current_num}\n')

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        sales_file = os.path.join(self.root_directory_path, 'sales.txt')
        sales_index_file = os.path.join(self.root_directory_path,
                                        'sales_index.txt')
        cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        cars_index_file = os.path.join(self.root_directory_path,
                                       'cars_index.txt')

        # Записываем продажу
        sales_index = []
        if os.path.exists(sales_index_file):
            with open(sales_index_file, 'r') as f:
                for line in f:
                    num, pos = line.strip().split(',')
                    sales_index.append((num, int(pos)))

        # Номер новой строки
        line_number = len(sales_index)

        # Формирование строки продажи
        sale_line = (
            f'{sale.sales_number};{sale.car_vin};'
            f'{sale.sales_date.date()};{sale.cost}'
        ).ljust(500) + '\n'

        # Записываем продажу в файл
        with open(sales_file, 'a') as f:
            f.write(sale_line)

        # Обновляем индекс в памяти
        sales_index.append((sale.sales_number, line_number))
        sales_index.sort()

        # Перезаписываем индекс продаж
        with open(sales_index_file, 'w') as f:
            for current_num, current_pos in sales_index:
                f.write(f'{current_num},{current_pos}\n')

        # Находим машину
        cars_index = []
        with open(cars_index_file, 'r') as f:
            for line in f:
                vin, pos = line.strip().split(',')
                cars_index.append((vin, int(pos)))

        car_pos = None
        for current_vin, current_pos in cars_index:
            if current_vin == sale.car_vin:
                car_pos = current_pos
                break

        if car_pos is None:
            raise ValueError(f'Машина с VIN {sale.car_vin} не найдена')

        with open(cars_file, 'r') as f:
            f.seek(car_pos * 501)
            car_data = f.read(500).strip()

        vin, model, price, date_start, status = car_data.split(';')

        # Обновление статуса
        updated_car = Car(
            vin=vin,
            model=int(model),
            price=Decimal(price),
            date_start=datetime.strptime(date_start, '%Y-%m-%d'),
            status=CarStatus.sold
        )

        # Повторная запись
        updated_line = (
            f'{updated_car.vin};{updated_car.model};'
            f'{updated_car.price};{updated_car.date_start.date()};'
            f'{updated_car.status.value}'
        ).ljust(500) + '\n'

        with open(cars_file, 'r+') as f:
            f.seek(car_pos * 501)
            f.write(updated_line)

        return updated_car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        result = []

        with open(cars_file, 'r') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) < 5:
                    continue
                if parts[4] == status.value:
                    car = Car(
                        vin=parts[0],
                        model=int(parts[1]),
                        price=Decimal(parts[2]),
                        date_start=datetime.strptime(parts[3], '%Y-%m-%d'),
                        status=CarStatus(parts[4])
                    )
                    result.append(car)

        return result

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        cars_index_file = (
                    os.path.join(self.root_directory_path, 'cars_index.txt')
                )
        models_index_file = os.path.join(
            self.root_directory_path, 'models_index.txt'
            )
        models_file = os.path.join(self.root_directory_path, 'models.txt')
        sales_file = os.path.join(self.root_directory_path, 'sales.txt')

        # Индекс машины
        cars_index = []
        with open(cars_index_file, 'r') as f:
            for line in f:
                vin_str, pos_str = line.strip().split(',')
                cars_index.append((vin_str, int(pos_str)))

        # Позиция машины по VIN
        car_pos = None
        for current_vin, pos in cars_index:
            if current_vin == vin:
                car_pos = pos
                break

        # Если машина не найдена - None
        if car_pos is None:
            return None

        with open(cars_file, 'r') as f:
            f.seek(car_pos * 501)
            car_data = f.read(500).strip()

        car_vin, model_id, price, date_start, status = car_data.split(';')

        # Индекс моделей
        models_index = []
        with open(models_index_file, 'r') as f:
            for line in f:
                id_str, pos_str = line.strip().split(',')
                models_index.append((int(id_str), int(pos_str)))

        model_pos = None
        for current_id, pos in models_index:
            if current_id == int(model_id):
                model_pos = pos
                break

        if model_pos is None:
            return None

        with open(models_file, 'r') as f:
            f.seek(model_pos * 501)
            model_data = f.read(500).strip()

        _, model_name, model_brand = model_data.split(';')

        sales_date = None
        sales_cost = None

        if status == 'sold':
            if os.path.exists(sales_file):
                with open(sales_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split(';')
                        if len(parts) < 4:
                            continue
                        if parts[1] == vin:
                            sales_date = datetime.strptime(
                                parts[2], '%Y-%m-%d'
                                )
                            sales_cost = Decimal(parts[3])
                            break

        return CarFullInfo(
            vin=vin,
            car_model_name=model_name,
            car_model_brand=model_brand,
            price=Decimal(price),
            date_start=datetime.strptime(date_start, '%Y-%m-%d'),
            status=CarStatus(status),
            sales_date=sales_date,
            sales_cost=sales_cost
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        cars_index_file = os.path.join(
            self.root_directory_path, 'cars_index.txt'
            )

        cars_index = []
        with open(cars_index_file, 'r') as f:
            for line in f:
                str_vin, str_pos = line.strip().split(',')
                cars_index.append((str_vin, int(str_pos)))

        car_pos = None
        for current_vin, pos in cars_index:
            if current_vin == vin:
                car_pos = pos
                break

        if car_pos is None:
            raise ValueError(f'Машина с VIN {vin} не найдена')

        with open(cars_file, 'r') as f:
            f.seek(car_pos * 501)
            car_data = f.read(500).strip()

        old_vin, model, price, date_start, status = car_data.split(';')

        updated_car = Car(
            vin=new_vin,
            model=int(model),
            price=Decimal(price),
            date_start=datetime.strptime(date_start, '%Y-%m-%d'),
            status=CarStatus(status)
        )

        updated_line = (
            f'{updated_car.vin};{updated_car.model};'
            f'{updated_car.price};{updated_car.date_start.date()};'
            f'{updated_car.status.value}'
        ).ljust(500) + '\n'

        with open(cars_file, 'r+') as f:
            f.seek(car_pos * 501)
            f.write(updated_line)

        new_index = []
        for current_vin, pos in cars_index:
            if current_vin == vin:
                new_index.append((new_vin, pos))
            else:
                new_index.append((current_vin, pos))

        new_index.sort()

        with open(cars_index_file, 'w') as f:
            for current_vin, pos in new_index:
                f.write(f'{current_vin},{pos}\n')

        return updated_car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        sales_file = os.path.join(self.root_directory_path, 'sales.txt')
        sales_index_file = os.path.join(
            self.root_directory_path, 'sales_index.txt'
            )
        cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        cars_index_file = os.path.join(
            self.root_directory_path, 'cars_index.txt'
            )

        # Чтение индекса продаж
        sales_index = []
        with open(sales_index_file, 'r') as f:
            for line in f:
                current_num, current_pos = line.strip().split(',')
                sales_index.append((current_num, int(current_pos)))

        # Поиск позиции продажи
        sale_pos = None
        for num, pos in sales_index:
            if num == sales_number:
                sale_pos = pos
                break

        # Если не нашли — выводим ошибку
        if sale_pos is None:
            raise ValueError(f'Продажа {sales_number} не найдена')

        # Чтение строк продаж, чтобы узнать car_vin
        with open(sales_file, 'r') as f:
            f.seek(sale_pos * 501)
            sale_data = f.read(500).strip()

        _, car_vin, _, _ = sale_data.split(';')

        # Чтение строк sales.txt в отдельный список
        all_sales = []
        with open(sales_file, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    all_sales.append(stripped)

        # Удаление строки по позиции
        del all_sales[sale_pos]

        # Перезаписываем sales.txt
        with open(sales_file, 'w') as f:
            for sale_line in all_sales:
                f.write(sale_line.ljust(500) + '\n')

        # Пересчет индекса продаж
        new_sales_index = []
        for i, sale_line in enumerate(all_sales):
            num = sale_line.split(';')[0]
            new_sales_index.append((num, i))

        new_sales_index.sort()

        # Перезапись sales_index.txt
        with open(sales_index_file, 'w') as f:
            for num, pos in new_sales_index:
                f.write(f'{num},{pos}\n')

        # Поиск машины по car_vin
        cars_index = []
        with open(cars_index_file, 'r') as f:
            for line in f:
                str_vin, str_pos = line.strip().split(',')
                cars_index.append((str_vin, int(str_pos)))

        car_pos = None
        for current_vin, pos in cars_index:
            if current_vin == car_vin:
                car_pos = pos
                break

        if car_pos is None:
            raise ValueError(f'Машина с VIN {car_vin} не найдена')

        # Смена статуса на available
        with open(cars_file, 'r') as f:
            f.seek(car_pos * 501)
            car_data = f.read(500).strip()

        vin, model, price, date_start, status = car_data.split(';')

        updated_car = Car(
            vin=vin,
            model=int(model),
            price=Decimal(price),
            date_start=datetime.strptime(date_start, '%Y-%m-%d'),
            status=CarStatus.available
        )

        updated_line = (
            f'{updated_car.vin};{updated_car.model};'
            f'{updated_car.price};{updated_car.date_start.date()};'
            f'{updated_car.status.value}'
        ).ljust(500) + '\n'

        with open(cars_file, 'r+') as f:
            f.seek(car_pos * 501)
            f.write(updated_line)

        return updated_car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        sales_file = os.path.join(self.root_directory_path, 'sales.txt')
        cars_file = os.path.join(self.root_directory_path, 'cars.txt')
        cars_index_file = os.path.join(
            self.root_directory_path, 'cars_index.txt'
            )
        models_file = os.path.join(self.root_directory_path, 'models.txt')
        models_index_file = os.path.join(
            self.root_directory_path, 'models_index.txt'
            )

        # 1. Читаем индекс машин в память
        cars_index = {}
        with open(cars_index_file, 'r') as f:
            for line in f:
                vin, pos = line.strip().split(',')
                cars_index[vin] = int(pos)

        # 2. Считаем продажи и максимальную цену по моделям
        # model_stats[model_id] = [количество_продаж, макс_цена]
        model_stats: dict[int, list] = {}
        with open(sales_file, 'r') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) < 4:
                    continue

                car_vin = parts[1]
                if car_vin not in cars_index:
                    continue

                # Читаем машину по VIN
                car_pos = cars_index[car_vin]
                with open(cars_file, 'r') as cf:
                    cf.seek(car_pos * 501)
                    car_data = cf.read(500).strip()

                _, model_id_str, price_str, _, _ = car_data.split(';')
                model_id = int(model_id_str)
                price = Decimal(price_str)

                if model_id not in model_stats:
                    model_stats[model_id] = [0, price]

                model_stats[model_id][0] += 1
                if price > model_stats[model_id][1]:
                    model_stats[model_id][1] = price

        # 3. Сортируем по (количество DESC, цена DESC)
        sorted_models = sorted(
            model_stats.items(),
            key=lambda item: (item[1][0], item[1][1]),
            reverse=True
        )

        # 4. Топ-3
        top_3 = sorted_models[:3]

        # 5. Читаем индекс моделей
        models_index = {}
        with open(models_index_file, 'r') as f:
            for line in f:
                mid, pos = line.strip().split(',')
                models_index[int(mid)] = int(pos)

        # 6. Собираем результат
        result = []
        for model_id, stats in top_3:
            model_pos = models_index[model_id]
            with open(models_file, 'r') as f:
                f.seek(model_pos * 501)
                model_data = f.read(500).strip()

            _, name, brand = model_data.split(';')

            result.append(ModelSaleStats(
                car_model_name=name,
                brand=brand,
                sales_number=stats[0]
            ))

        return result
