"""main.py"""
import uuid
from collections import namedtuple

import psycopg

from fastapi import FastAPI, HTTPException

from app.db import database

from app.result import Cities, SalesDetails, Stores

app = FastAPI(title="FastAPI, Docker")


@app.get("/stores")
async def get_all_stores():
    """get all stores."""
    query = f'{"SELECT * FROM stores"}'
    try:
        with app.db.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
    except psycopg.errors.Error:
        app.db.rollback()
        raise HTTPException(status_code=400, detail="Invalid datetime format!")
    entries = [Stores(*r) for r in result]
    return {"data": entries}


@app.get("/stores/{name}")
async def get_stores_by_name(name: str):
    """get store by name."""
    query = """SELECT * FROM stores WHERE name = %s"""
    try:
        with app.db.cursor() as cur:
            cur.execute(query, (name,))
            result = cur.fetchall()
    except psycopg.errors.Error:
        app.db.rollback()
        raise HTTPException(status_code=400, detail="Invalid query!")
    entries = [Stores(*r) for r in result]
    return {"data": entries}


@app.get("/cities")
async def get_all_cities():
    """get all addresses."""
    query = f'{"SELECT * from store_addresses"}'
    try:
        with app.db.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
    except psycopg.errors.Error:
        app.db.rollback()
        raise HTTPException(status_code=400, detail="Invalid query!")
    entries = [Cities(*r) for r in result]
    return {"data": entries}


@app.get("/cities/{city}")
async def get_city_by_zip(city: str):
    """get an address bya city."""
    query = """SELECT id, store, address, zip, city FROM store_addresses WHERE city = %s"""
    try:
        with app.db.cursor() as cur:
            cur.execute(query, (city,))
            result = cur.fetchall()
    except psycopg.errors.Error:
        app.db.rollback()
        raise HTTPException(status_code=400, detail="Invalid query!")
    entries = [Cities(*r) for r in result]
    return {"data": entries}


def is_valid_uuid(value):
    """check uuid input."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


@app.get("/sales/{sale_id}")
def sales_id(sale_id: str):
    """get sale by id."""
    if is_valid_uuid(sale_id) is False:
        return HTTPException(status_code=400, detail="Id not valid")
    with app.db.cursor() as cur:
        cur.execute(
            """
                SELECT stores.name, sales.time, sales.id, products.name, sold_products.quantity
                FROM stores
                JOIN sales ON stores.id = sales.store
                JOIN sold_products ON sold_products.sale = sales.id
                JOIN products ON products.id = sold_products.product
                WHERE sales.id = %s;
                """, (sale_id,))
        db_response = cur.fetchall()
    if not db_response:
        raise HTTPException(status_code=404, detail="404 Not Found")
    name, date_time, db_id = db_response[0][:3]
    products = []

    for sale in db_response:
        products.append({
            "name": sale[-2],
            "qty": sale[-1]
        })
    result = SalesDetails(name, str(date_time), str(db_id), products)
    return {"data": vars(result)}


QueryResultInventory = namedtuple("QueryResultInventory", ("product_name",
                                                           "adjusted_quantity",
                                                           "store_name"))


@app.get("/inventory")
def get_inventory(store=None, product=None):
    """get_inventory."""
    store_clause, product_clause = "", ""
    parameters = []
    if store:
        try:
            uuid.UUID(store)
        except ValueError as err:
            raise HTTPException(status_code=422,
                                detail="Invalid UUID for store!") from err
        store_clause = "WHERE stores.id = %s"
        parameters.append(store)
    if product:
        try:
            uuid.UUID(product)
        except ValueError as err:
            raise HTTPException(status_code=422,
                                detail="Invalid UUID for product!") from err
        product_clause = "WHERE products.id = %s"
        if parameters:
            product_clause = product_clause.replace("WHERE", "AND")
        parameters.append(product)
    query = """SELECT products.name,
               SUM(inventory.quantity) + SUM(sold_products.quantity),
               stores.name
               FROM inventory
               JOIN products ON products.id = inventory.product
               JOIN stores ON stores.id = inventory.store
               JOIN sold_products ON sold_products.product = products.id
               {store} {product}
               GROUP BY stores.name, products.name;
    """
    query = query.format(store=store_clause, product=product_clause)
    with app.db.cursor() as cur:
        cur.execute(query, parameters)
        result = cur.fetchall()
    entries = [QueryResultInventory(*r)._asdict() for r in result]
    return sorted(entries, key=lambda x: (x["store_name"], x["product_name"]))


#
# @app.get("/sales/{sale_id}")
# async def get_sale_by_id(sale_id: str):
#     """get store and products by sales id."""
#     try:
#         if is_valid_uuid(sale_id) is False:
#             return HTTPException(status_code=400, detail="Id not valid")
#         query = f"select sales.id as sale_id, time as timestamp, name as store from public.sales INNER JOIN stores ON sales.store = stores.id where sales.id = '{sale_id}'"
#         with app.db.cursor() as cur:
#             cur.execute(query)
#             sale = cur.fetchall()
#             products_list = []
#             if not sale:
#                 return HTTPException(status_code=404, detail="Item not found")
#             entries_sales = [Sales(*r) for r in sale]
#             sales_id_db = entries_sales[0].id
#             print(sales_id_db)
#             products_query = f"select * from sold_products where sold_products.sale = '{sales_id_db}'"
#             cur.execute(products_query)
#             sold_products = cur.fetchall()
#             entries_sold_products = [SoldProducts(*r) for r in sold_products]
#             array_len = len(sold_products)
#             for i in range(array_len):
#                 print("entries_sold_products[i].product")
#                 print(entries_sold_products[i].product)
#                 cur.execute(f"select id, name  from products where id = '{entries_sold_products[i].product}'")
#                 product = cur.fetchall()
#                 entries_products = [Product(*r) for r in product]
#                 products_list.append(
#                     ProductsDetails(str(entries_products[0].name), int(entries_sold_products[i].quantity)))
#         result = SalesDetails(entries_sales[0].store, entries_sales[0].time, sales_id_db, products_list)
#         return {"data": vars(result)}
#     except psycopg.errors.Error:
#         app.db.rollback()
#         raise HTTPException(status_code=400, detail="Invalid query!")


@app.on_event("startup")
async def startup():
    """start connection to db"""
    app.db = psycopg.connect(str(database.url))


@app.on_event("shutdown")
def shutdown():
    """This is used to correctly close the DB connection when stopping the API.
    This function doesn't need to be ported to your codebase.
    """
    app.db.close()
