from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from .inventory import*
import datetime 
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
        connection.execute(sqlalchemy.text("TRUNCATE TABLE barrel_ledgers RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE carts RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE cart_items RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE account_transactions RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE account_ledger_entries RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE potion_ledger_entries RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE global_inventory RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE TABLE accounts RESTART IDENTITY CASCADE"))
        connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers(red_ml, green_ml, blue_ml, dark_ml)""VALUES(:red_ml, :green_ml, :blue_ml, :dark_ml)"), {"red_ml": 0, "green_ml":0, "blue_ml": 0, "dark_ml":0})
        connection.execute(
        sqlalchemy.text(
            "INSERT INTO accounts (customer_name, character_class, level) "
            "VALUES (:customer_name, :character_class, :level)"
        ),
        {"customer_name": "Shop Keeper", "character_class": "Shop Owner", "level": 1}
    )
        account_id_query = sqlalchemy.text(
        "SELECT account_id FROM accounts WHERE customer_name = :customer_name"
    )
        transaction_description = "Default gold = 100"
        transaction_id = connection.execute(
            sqlalchemy.text("INSERT INTO account_transactions (created_at, description) "
                            "VALUES (:created_at, :description) RETURNING id"),
            {"created_at": datetime.datetime.now(), "description": transaction_description}
        ).scalar_one()

        account_id_result = connection.execute(account_id_query, {"customer_name": "Shop Keeper"}).fetchone()
        reset_globals()
        if account_id_result:
            account_id = account_id_result[0]
            
            # Insert a row into account_ledger_entries with gold value of 100
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO account_ledger_entries (account_transaction_id, account_id, change) "
                    "VALUES (:transaction_id, :account_id, :change)"
                ),
                {"transaction_id": transaction_id , "account_id": account_id, "change": 100}
            )
        


        

    return "OK"