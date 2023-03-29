from asgiref.sync import async_to_sync, sync_to_async
from getwowdataasync import WowApi
import asyncio

class DoesItWork():
    def __init__(self) -> None:
        wow_api = async_to_sync(WowApi.create)('us')
        print(wow_api.access_token)


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
DoesItWork()
