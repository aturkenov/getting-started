from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from wampify.signals import entrypoint_signals
from settings import settings


engine = create_async_engine(
    settings.ASYNC_TIMESCALE_SQLALCHEMY_URL,
    echo=settings.TIMESCALE_SQLALCHEMY_ECHO,
    pool_size=settings.TIMESCALE_SQLALCHEMY_POOL_SIZE,
    max_overflow=settings.TIMESCALE_SQLALCHEMY_MAX_OVERFLOW,
)


@entrypoint_signals.on
async def opened(story):
    story.timescale = AsyncSession(engine)
    # print('Timescale SQLAlchemy Async Session initialized')


@entrypoint_signals.on
async def raised(story, e):
    await story.timescale.rollback()
    await story.timescale.close()
    # print('Timescale SQLAlchemy Async Session rollback')


@entrypoint_signals.on
async def closed(story):
    await story.timescale.commit()
    await story.timescale.close()
    # print('Timescale SQLAlchemy Async Session closed')

