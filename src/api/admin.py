from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        # Truncate tables to remove all data
        connection.execute(sqlalchemy.text("TRUNCATE TABLE potions RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE barrels RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE carts RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE cart_items RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE account_transactions RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE account_ledger_entries RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = 0, green_ml = 0, blue_ml = 0"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 100"))

    return "OK"

