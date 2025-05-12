import asyncio

#подкормка удобрениями
async def fertilize(plant_name):
    print(f"7 Application of fertilizers for {plant_name}")
    await asyncio.sleep(3 / 1000)
    print(f"7 Fertilizers for the {plant_name} have been introduced")

#обработка от вредителей
async def pesticid_control(plant_name):
    print(f"8 Treatment of {plant_name} from pests")
    await asyncio.sleep(5 / 1000)
    print(f"8 The {plant_name} is treated from pests")

#выращивание одного растения
async def plant_process(plant_name, soak_time, grow_time, acclimation_time):
    print(f"0 Beginning of sowing the {plant_name} plant_name")
    print(f"1 Soaking of the {plant_name} started")

    # Параллельно запускаем подкормку и обработку
    fertilize_task = asyncio.create_task(fertilize(plant_name))
    pesticid_control_task = asyncio.create_task(pesticid_control(plant_name))

    await asyncio.sleep(soak_time / 1000)
    print(f"2 Soaking of the {plant_name} is finished")
    print(f"3 Shelter of the {plant_name} is supplied")

    await asyncio.sleep(grow_time / 1000)
    print(f"4 Shelter of the {plant_name} is removed")
    print(f"5 The {plant_name} has been transplanted")

    await asyncio.sleep(acclimation_time / 1000)
    print(f"6 The {plant_name} has taken root")

    # Дожидаемся завершения подкормки и обработки
    await fertilize_task
    await pesticid_control_task

    print(f"9 The seedlings of the {plant_name} are ready")


async def sowing(*plants_data):
    tasks = []
    for plant_data in plants_data:
        plant_name, soak_time, grow_time, acclimation_time = plant_data
        task = asyncio.create_task(plant_process(plant_name, soak_time, grow_time, acclimation_time))
        tasks.append(task)

    await asyncio.gather(*tasks)

# Пример использования
if __name__ == '__main__':
    data = [('carrot', 7, 18, 2),
            ('cabbage', 2, 6, 10),
            ('onion', 5, 12, 7)]
    asyncio.run(sowing(*data))
