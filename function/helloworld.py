from mirai import Mirai, Plain, MessageChain, Friend, Group, GroupMessage, FriendMessage, MessageChain
import asyncio
import itertools
import ini

qq = 1424912867  # 字段 qq 的值
authKey = 'LTZDLYLLS'  # 字段 authKey 的值
# httpapi所在主机的地址端口,如果 setting.yml 文件里字段 "enableWebsocket" 的值为 "true" 则需要将 "/" 换成 "/ws", 否则将接收不到消息.
mirai_api_http_locate = 'localhost:8080/'

app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

@app.receiver("BotOnlineEvent")
async def event_input(app: Mirai):
    print("我来了")

@app.receiver("FriendMessage")
async def event_fri_msg(app: Mirai, friend: Friend, messagechain: MessageChain):
    for i in itertools.chain(messagechain):
        if(hasattr(i, "text")):
            msg = i.text
    '''
    if(friend.id == 349468958 and msg == '1'):
        print("livestart!")
        ini.livestart()
    '''
    chain = list(itertools.islice(messagechain, 1, len(messagechain)))
    print (f"msg=[{len(chain)}]", end=' ')
    print (list(map(str, chain)))
    print (chain)
    print (friend)
    await app.sendFriendMessage(friend.id, chain)
'''
@app.receiver("GroupMessage")
async def event_grp_msg(app: Mirai, group: Group, messagechain: MessageChain):
    chain = list(itertools.islice(messagechain, 1, len(messagechain)))
    print (f"msg=[{len(chain)}]", end=' ')
    print (list(map(str, chain)))
    print (chain)
    await app.sendFriendMessage(349468958, chain)
'''
if __name__ == "__main__":
    app.run()
