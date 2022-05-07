from aioredis import Redis
from wampify.signals import entrypoint_signals
from settings import settings


# ConnectionPool
redis: Redis = Redis.from_url(url=settings.REDIS_URL)


@entrypoint_signals.on
async def opened(story):
    story.redis = redis.client()
    # print('Redis Async Session initialized')


@entrypoint_signals.on
async def raised(story, e):
    await story.redis.close()
    # print('Redis Async Session raised')


@entrypoint_signals.on
async def closed(story):
    await story.redis.close()
    # print('Redis Async Session closed')

