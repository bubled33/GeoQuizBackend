import asyncio

from aiohttp import ClientSession


async def main():
    api_key= '9b04bfd6-f50a-4763-b411-70868732ebf1'

    async with ClientSession() as client:
        url = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode=Москва,+Тверская+улица,+дом+7'
        response = await client.get(url)
    print(await response.ht)

asyncio.run(main())