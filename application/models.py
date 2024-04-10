from sqlalchemy import Table, MetaData, Column, Integer, VARCHAR, Float, TIMESTAMP, func


meta = MetaData()
statistics = Table(
    'statistics', meta,
    Column('id', Integer, primary_key=True),
    Column('currency', VARCHAR),
    Column('date_', TIMESTAMP, default=func.now()),
    Column('price', Float),
)
