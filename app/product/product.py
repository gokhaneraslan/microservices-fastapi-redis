from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    host="redis-17084.c55.eu-central-1-1.ec2.cloud.redislabs.com",
    port=17084,
    password="OOKZhk9AtzRHxxDEZDn2bap7XYiw1vER",
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


def format(pk:str):
    product = Product.get(pk)

    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }


@app.get("/products/get")
async def get_all():
    return [format(pk) for pk in Product.all_pks()]


@app.post("/products/create")
async def create(product: Product):
    return product.save()


@app.get("/products/{pk}")
async def fetch_one(pk:str):
    return Product.get(pk)


@app.delete("/products/{pk}")
async def del_one(pk:str):
    product = Product.get(pk)

    return product.delete(product)