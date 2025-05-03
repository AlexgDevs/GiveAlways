import asyncio

from database import (
    Participation,
    User,
    Giveaway,
    up
)

async def main():
    up()



if __name__=='__main__':
    asyncio.run(main())


