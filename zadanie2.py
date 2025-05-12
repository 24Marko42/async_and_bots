import asyncio
import aiohttp
from aiohttp import ClientTimeout

async def get_ip(session, url, service_name):
    try:
        async with session.get(url, timeout=ClientTimeout(total=5)) as response:
            ip = (await response.text()).strip()
            return ip, service_name
    except Exception as e:
        print(f"Ошибка при запросе к {service_name}: {str(e)}")
        return None, None

async def main():
    services = [
        ("https://api.ipify.org", "Ipify"),
        ("https://checkip.amazonaws.com", "Amazon AWS"),
        ("https://ifconfig.me/ip", "IfConfig.me"),
    ]

    async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:
        tasks = [asyncio.create_task(get_ip(session, url, name)) for url, name in services]
        
        for future in asyncio.as_completed(tasks):
            ip, service_name = await future
            if ip:
                print(f"Ваш IP адрес: {ip} (получено через {service_name})")
                # Отменяем все оставшиеся задачи
                for task in tasks:
                    task.cancel()
                break

if __name__ == '__main__':
    asyncio.run(main())