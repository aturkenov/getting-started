from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from wampify.signals import entrypoint_signals
from settings import settings


engine = create_async_engine(
    settings.ASYNC_SQLALCHEMY_URL,
    echo=settings.SQLALCHEMY_ECHO,
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
)


@entrypoint_signals.on
async def opened(story):
    story.postgres = AsyncSession(engine)
    # print('SQLAlchemy Async Session initialized')


@entrypoint_signals.on
async def raised(story, e):
    await story.postgres.rollback()
    await story.postgres.close()
    # print('SQLAlchemy Async Session rollback')


@entrypoint_signals.on
async def closed(story):
    await story.postgres.commit()
    await story.postgres.close()
    # print('SQLAlchemy Async Session closed')

