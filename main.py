import asyncio
from aiohttp import ClientSession
from database import People, Base, Session, engine
from more_itertools import chunked


async def make_request(people_id: int, session: ClientSession):
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        json_data = await response.json(content_type=None)
        if 'Not found' not in json_data.values():
            return json_data


async def paste_to_db(people_list):
    async with Session() as session:
        for people in people_list:
            new_person = People(**people)
            session.add(new_person)
        await session.commit()


MAX_REQUESTS = 10


async def main():
    tasks = []
    async with ClientSession() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        for chunk in chunked(range(1, 101), MAX_REQUESTS):
            coros = []
            for people_id in chunk:
                coro = make_request(people_id=people_id, session=session)
                if coro is not None:
                    coros.append(coro)
            people_list = await asyncio.gather(*coros)
            await paste_to_db(people_list)


asyncio.run(main())
