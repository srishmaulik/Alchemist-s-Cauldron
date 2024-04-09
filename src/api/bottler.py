from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            # Update the inventory with the delivered potions
            sql_update_inventory = f"UPDATE global_inventory SET num_green_potions = num_green_potions + {potion.quantity}"
            connection.execute(sqlalchemy.text(sql_update_inventory))
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    plan = []
    
    with db.engine.begin() as connection:
        # Fetch the current inventory of green ml from the global inventory table
        sql_green_ml = "SELECT num_green_ml FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql_green_ml))
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    for row in result:
            num_green_ml = row[0]

            # Determine how many green potions to produce based on the available green ml
            if num_green_ml > 0:
                # Determine the quantity of green ml per green potion
                ml_per_potion = num_green_ml  # Bottling all available green ml into one potion
                # Calculate the number of potions to produce
                quantity = num_green_ml // ml_per_potion
                
                # Add the plan for bottling green potions to the list
                plan.append({
                    "potion_type": [0,0,100,0],  # Assuming green potions are type 0
                    "quantity": quantity
                })
    return plan

if __name__ == "__main__":
    print(get_bottle_plan())