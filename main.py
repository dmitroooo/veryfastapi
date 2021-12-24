database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("price", sqlalchemy.Integer),
   
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

app = FastAPI(
    docs_url="/", 
)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/product", response_model=List[ProductList], tags=["Products"])

async def find_all_products():
    query = products.select()
    return await database.fetch_all(query)

@app.post("/prosucts", response_model=ProductList, tags=["Products"])
async def register_product(product: ProductEntry):
    gID   = str(uuid.uuid1())
    query = products.insert().values(
        id = gID,
        name   = product.name,
        price = product.price,
    ) 
    await database.execute(query)
    return {
        "id": gID,
        **product.dict()
    }

@app.get("/products/{productId}", response_model=ProductList, tags=["Products"])
async def find_product_by_id(productId: str):
    query = products.select().where(products.c.id == productId)
    return await database.fetch_one(query)

@app.put("/products", response_model=ProductList, tags=["Products"])
async def update_productr(product: ProductUpdate):
    query = products.update().\
        where(products.c.id == product.id).\
        values(
            name = product.name,
            price  = product.price,
        )
    await database.execute(query)

    return await find_product_by_id(product.id)

@app.delete("/products/{productId}", tags=["Products"])
async def delete_product(product: ProductDelete):
    query = products.delete().where(products.c.id == product.id)
    await database.execute(query)

    return {
        "status" : True,
        "message": "This product has been deleted successfully." 
    }