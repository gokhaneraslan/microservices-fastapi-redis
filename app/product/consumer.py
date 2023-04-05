from product import redis, Product, fetch_one
import time
import asyncio

key= 'order_completed'
group= 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group alreday exists!')

async def get_one(pk):
    return await fetch_one(pk)

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                product = get_one(obj['product_id'])
                product = asyncio.run(product)
                print(product)

    except Exception as e:
        print(str(e))

    time.sleep(1)
