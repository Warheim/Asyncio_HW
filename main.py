import asyncio
import re
from aiohttp import ClientSession
from database import People, Base, Session, engine
from more_itertools import chunked
from datetime import datetime

url_regex = re.compile(
    "^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?$")


async def people_request(people_id: int, session: ClientSession):
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json()
        coros = []
        for key, content in json_data.items():
            if content and (isinstance(content, str)) and re.search(url_regex, content):
                coro = content_str_request(content, session=session)
                coros.append(coro)
            elif content and isinstance(content, list):
                coro = content_list_request(content, session=session)
                coros.append(coro)
        data_ready = await asyncio.gather(*coros)
        print(data_ready)


async def content_str_request(content: str, session: ClientSession):
    async with session.get(content) as request:
        response = await request.json()
        return response


async def content_list_request(content: list, session: ClientSession):
    for url in content:
        async with session.get(url) as request:
            response = await request.json()
            return response


# async def paste_to_db(people_list):
#     async with Session() as session:
#         for people in people_list:
#             post = People(**people)
#             session.add(post)
#             await session.commit()


MAX_REQUESTS = 10


async def main():
    async with ClientSession() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        for chunk in chunked(range(1, 2), MAX_REQUESTS):
            coros = []
            for people_id in chunk:
                coro = people_request(people_id=people_id, session=session)
                if coro is not None:
                    coros.append(coro)
            people_list = await asyncio.gather(*coros)


start = datetime.now()
asyncio.run(main())
print(datetime.now() - start)
