import orm,asyncio
from models import User,Blog,Comment

def test(loop):
    yield from orm.create_pool(loop=loop,user='jsxnh',password='jsxnh',db='jsxnh')
    
    u=User(name='test',email='test@example.com',passwd='23',image='about:blank')
    yield from u.save()
loop=asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
