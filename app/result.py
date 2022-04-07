"""result.py"""


class ProductsDetails:
    """ProductsDetails"""

    def __init__(self, name, qty):
        self.name = name
        self.qty = qty


class Product:
    """ProductsDetails"""

    def __init__(self, product_id, name):
        self.id = product_id
        self.name = name


class SalesDetails:
    """SalesDetails"""

    def __init__(self, store, timestamp, sale_id, products):
        self.store = store
        self.timestamp = timestamp
        self.sale_id = sale_id
        self.products = products


class Stores:
    """Stores"""

    def __init__(self, store_id, name):
        self.id = store_id
        self.name = name


class Cities:
    """Cities"""

    def __init__(self, address_id, store_id, address, address_zip, city):
        self.id = address_id
        self.store_id = store_id
        self.address = address
        self.zip = address_zip
        self.city = city


class Sales:
    """Sales"""

    def __init__(self, sale_id, time, store):
        self.id = sale_id
        self.time = time
        self.store = store


class SoldProducts:
    """Sold_Products"""

    def __init__(self, sp_id, product, sale, quantity):
        self.id = sp_id
        self.product = product
        self.sale = sale
        self.quantity = quantity
