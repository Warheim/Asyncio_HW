import asyncio
import re
from aiohttp import ClientSession
from database import People, Base, Session, engine
from more_itertools import chunked
from datetime import datetime

url_regex = re.compile(
    "^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?$")


async def people_parser(people_id: int, session: ClientSession):
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json(content_type=None)
        parsed_data = {}

        for key, content in json_data.items():
            if content:
                if isinstance(content, str) and re.search(url_regex, content) and key != 'url':
                    coro = await content_request(content=content, session=session)
                    parsed_data[key] = list(coro.values())[0]

                elif isinstance(content, list):
                    coros = [content_request(content=url, session=session) for url in content if
                             re.search(url_regex, url)]
                    responses = await asyncio.gather(*coros)
                    items = [list(item.values())[0] for item in responses]
                    parsed_data[key] = ', '.join(items)

                else:
                    parsed_data[key] = content

        return parsed_data


async def content_request(content: str, session: ClientSession):
    async with session.get(content) as request:
        response = await request.json(content_type=None)
        return response


async def paste_to_db(people_list):
    async with Session() as session:
        for people in people_list:
            if 'Not found' not in people.values():
                post = People(**people)
                session.add(post)
                await session.commit()


async def task_handler(tasks: list):
    asyncio.all_tasks() - {asyncio.current_task()}
    for task in tasks:
        await task


MAX_REQUESTS = 10


async def main():
    tasks = []
    async with ClientSession() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        for chunk in chunked(range(1, 100), MAX_REQUESTS):
            coros = [people_parser(people_id=people_id, session=session) for people_id in chunk]
            people_list = await asyncio.gather(*coros)
            filling_db = paste_to_db(people_list)
            prepare_task = asyncio.create_task(filling_db)
            tasks.append(prepare_task)

    await task_handler(tasks)


if __name__ == '__main__':
    start = datetime.now()
    asyncio.run(main())
    print(datetime.now() - start)
