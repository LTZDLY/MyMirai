import asyncio

from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

async def printf(app, i):
    await app.sendFriendMessage(349468958, MessageChain.create([Plain(str(i))]))
    print('repeat')

async def repeat(app):
    i = 0
    while i < 10:
        i += 1
        await asyncio.sleep(5)
        asyncio.create_task(printf(app, i))
