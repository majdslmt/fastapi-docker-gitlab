"""Entities."""

from app.config import settings

import uuid

import databases

import ormar

import sqlalchemy


database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    """BaseMeta."""
    metadata = metadata
    database = database


class Stores(ormar.Model):
    """Stores."""
    class Meta(BaseMeta):
        """Stores."""
        tablename = "stores"
    id: uuid = ormar.UUID(primary_key=True)
    name: str = ormar.String(max_length=128, unique=True, nullable=False)


class Cities(ormar.Model):
    """Cities."""
    class Meta(BaseMeta):
        """Cities."""
        tablename = "store_addresses"
    id: uuid = ormar.UUID(primary_key=True)
    zip: str = ormar.String(max_length=128)
    address: str = ormar.String(max_length=128)
    city: str = ormar.String(max_length=128,)
    store: uuid = ormar.UUID(foreign_key=True)


class Sales(ormar.Model):
    """Sales."""
    class Meta(BaseMeta):
        """Sales."""
        tablename = "sales"


engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
