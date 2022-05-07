import sys
sys.path.append('./source/')

import asyncio
from api.wamp.ami import *


async def main():
    from driver.wamp.ami import wampify as ami_wampify
    await ami_wampify.run(start_loop=False)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()

