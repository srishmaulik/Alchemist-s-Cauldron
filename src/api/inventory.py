from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import math
import datetime
router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/audit")
def get_inventory():
    with db.engine.begin() as connection:
        # Query to get the number of potions
        num_potions_query = sqlalchemy.text("SELECT SUM(quantity) FROM potion_ledger_entries")
        num_potions_result = connection.execute(num_potions_query).scalar()

        # Query to get the milliliters of each color in barrels
        ml_in_barrels_query = sqlalchemy.text("SELECT SUM(red_ml), SUM(green_ml), SUM(blue_ml), SUM(dark_ml) FROM barrel_ledgers")
        ml_in_barrels_result = connection.execute(ml_in_barrels_query).fetchone()

        # Query to get the amount of gold
        gold_query = sqlalchemy.text("SELECT COALESCE(SUM(change),0) FROM account_ledger_entries")
        gold_result = connection.execute(gold_query).scalar()

        # Construct the response
        inventory = {
            "number_of_potions": 1,
            "ml_in_barrels":  1,
            "gold": 0
        }

    return inventory

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    with db.engine.begin() as connection:
        
        num_potions_query = sqlalchemy.text("SELECT SUM(quantity) FROM potion_ledger_entries")
        num_potions_result = connection.execute(num_potions_query).scalar()
        ml_in_barrels_query = sqlalchemy.text("SELECT SUM(red_ml), SUM(green_ml), SUM(blue_ml), SUM(dark_ml) FROM barrel_ledgers")
        ml_in_barrels_result = connection.execute(ml_in_barrels_query).fetchone()
        gold_query = sqlalchemy.text("SELECT SUM(change) FROM account_ledger_entries")
        gold_result = connection.execute(gold_query).scalar()
        capacities = connection.execute(sqlalchemy.text("SELECT ml_capacity, potion_capacity FROM global_inventory")).fetchone()
        ml_capacity, potion_capacity = capacities
        
        if gold_result >= 1000:
            ml_capacity += 1
            gold_result -= 1000
            
        if gold_result>=1000:
            potion_capacity += 1
            gold_result -= 1000
                
            
            

            # Query to get the milliliters of each color in barrels
        
        
        
        # Calculate the maximum number of potions and ml of potion the shop can currently store
        
    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase: CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    # gold_to_be_subtracted = 0
    # with db.engine.begin() as connection:
    #     # Get current gold balance from the account ledger
        
    #     gold_query = "SELECT SUM(change) FROM account_ledger_entries"
    #     gold_balance = connection.execute(sqlalchemy.text(gold_query)).scalar()
       
    #     capacities = connection.execute(sqlalchemy.text("SELECT ml_capacity, potion_capacity FROM global_inventory")).fetchone()
    #     initial_ml_capacity, initial_potion_capacity = capacities
    #     if capacity_purchase.ml_capacity>1:
    #         connection.execute(sqlalchemy.text("UPDATE global_inventory SET ml_capacity = :ml_capacity"), {"ml_capacity": capacity_purchase.ml_capacity})
    #         gold_to_be_subtracted += (capacity_purchase.ml_capacity-initial_ml_capacity)*1000
    #     if capacity_purchase.potion_capacity>1:
    #         connection.execute(sqlalchemy.text("UPDATE global_inventory SET potion_capacity = :potion_capacity"),{'potion_capacity': capacity_purchase.potion_capacity})
    #         gold_to_be_subtracted += (capacity_purchase.potion_capacity-initial_potion_capacity)*1000



    #     # Update the gold balance in the account ledger
    #     if gold_balance>=gold_to_be_subtracted:
    #         sql_update_gold = f"""
    #         INSERT INTO account_transactions (created_at, description)
    #         VALUES (:created_at, :description)
    #         RETURNING id
    #         """
    #         transaction_id = connection.execute(
    #             sqlalchemy.text(sql_update_gold),
    #             {"created_at": datetime.datetime.now(), "description": "Capacity purchase"}
    #         ).scalar_one()

            # connection.execute(
            #     sqlalchemy.text(
            #         "INSERT INTO account_ledger_entries (account_id, account_transaction_id, change) "
            #         "VALUES (:account_id, :transaction_id, :change)"
            #     ),
            #     {"account_id": 1, "transaction_id": transaction_id, "change": 0}
            # )

    return "OK"
