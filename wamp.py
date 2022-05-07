import sys
sys.path.append('./source/')

import asyncio
from api.wamp.hunter import *


async def main():
    from driver.wamp.hunter import wampify as hunter_wampify
    await hunter_wampify.run(start_loop=False)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()

