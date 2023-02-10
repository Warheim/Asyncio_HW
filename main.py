import asyncio
import re
from aiohttp import ClientSession
from database import People, Base, Session, engine
from more_itertools import chunked
from datetime import datetime

url_regex = re.compile(
    "^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?$")


async def json_get(url: str, session: ClientSession):
    async with session.get(url) as response:
        json_data = await response.json()
        return json_data


async def content_request(key, url, json_data, session: ClientSession):
    async with session.get(url) as response:
        values = []
        content_data = await response.json()
        values.append(list(content_data.values())[0])
        json_data[key] = ''.join(values)
        return json_data


async def url_reader(json_data: dict, session: ClientSession):
    coros = []
    for key, value in json_data.items():
        if value and value not in ('Not found', 'url') and isinstance(value, list):
            for url in value:
                coro = await content_request(key, url, json_data, session=session)
                coros.append(coro)
    result = await asyncio.gather(*coros)
    print(result)


async def people_request(people_id: int, session: ClientSession):
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json()
        result = await url_reader(json_data=json_data, session=session)
        return result


async def paste_to_db(people_list):
    async with Session() as session:
        for people in people_list:
            post = People(**people)
            session.add(post)
            await session.commit()


MAX_REQUESTS = 10


async def main():
    async with ClientSession() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        for chunk in chunked(range(1, 100), MAX_REQUESTS):
            coros = []
            for people_id in chunk:
                coro = people_request(people_id=people_id, session=session)
                if coro is not None:
                    coros.append(coro)
            people_list = await asyncio.gather(*coros)


start = datetime.now()
asyncio.run(main())
print(datetime.now() - start)
