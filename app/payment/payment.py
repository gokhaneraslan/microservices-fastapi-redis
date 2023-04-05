from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests, time

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=['*'],
    allow_headers=['*'],
    allow_methods=['*']
)

redis = get_redis_connection(
    host="redis-17084.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=17084,
    password="OOKZhk9AtzRHxxDEZDn2bap7XYiw1vER",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


@app.get("/")
def index():
    return {
        "Hello World!"
    }


@app.get("/orders/{pk}")
def get(pk:str):
    order = Order.get(pk)
    redis.xadd('refund_order', order.dict(), '*')
    return order


@app.post("/orders")
async def create_order(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()

    req = requests.get('http://127.0.0.1:8000/products/%s' % body['id'])
    product = req.json()

    order = Order(
        product_id= body['id'],
        price= product['price'],
        fee= 0.2 * product['price'],
        total= 1.2 * product['price'],
        quantity= body['quantity'],
        status='pending'
    )

    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()

    redis.xadd('order_completed', order.dict(), '*')
    