import asyncio

async def candidate_task(name, preparing_time, defense_time, task_number):
    print(f"{name} started the {task_number} task.")
    await asyncio.sleep(preparing_time / 100)
    print(f"{name} moved on to the defense of the {task_number} task.")
    await asyncio.sleep(defense_time / 100)
    print(f"{name} completed the {task_number} task.")

async def candidate_process(name, preparing1, defense1, preparing2, defense2):
    # Первое задание
    await candidate_task(name, preparing1, defense1, 1)
    
    # Отдых после первого задания
    print(f"{name} is good people and now resting.")
    await asyncio.sleep(5 / 100)
    
    # Второе задание
    await candidate_task(name, preparing2, defense2, 2)

async def interviews(*candidates):
    tasks = []
    for cand in candidates:
        name, preparing1, defense1, preparing2, defense2 = cand
        task = asyncio.create_task(candidate_process(name, preparing1, defense1, preparing2, defense2))
        tasks.append(task)
    
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    import time
    
    data = [
        ('Ivan', 5, 2, 7, 2),
        ('John', 3, 4, 5, 1),
        ('Sophia', 4, 2, 5, 1)
    ]
    
    t0 = time.time()
    asyncio.run(interviews(*data))
    print(time.time() - t0)