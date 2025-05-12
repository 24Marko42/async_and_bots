import asyncio

async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({i})...")
        await asyncio.sleep(0)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")

async def main():
    await asyncio.gather(
        factorial("A", 15),
        factorial("B", 7),
        factorial("C", 4),
    )

if __name__ == '__main__':
    asyncio.run(main())
