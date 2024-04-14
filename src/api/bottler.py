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
            potion_type = potion.potion_type

            # Update inventory based on potion type
            if potion_type == [0, 100, 0, 0]:  # Green potion
                sql_update_inventory = f"UPDATE global_inventory SET num_green_potions = num_green_potions + {potion.quantity}"
            elif potion_type == [100, 0, 0, 0]:  # Red potion
                sql_update_inventory = f"UPDATE global_inventory SET num_red_potions = num_red_potions + {potion.quantity}"
            elif potion_type == [0, 0, 100, 0]:  # Blue potion
                sql_update_inventory = f"UPDATE global_inventory SET num_blue_potions = num_blue_potions + {potion.quantity}"
            else:
                # Handle unexpected potion type (optional)
                return {"error": "Invalid potion type"}

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
        sql_red_ml = "SELECT num_red_ml FROM global_inventory"
        sql_blue_ml = "SELECT num_blue_ml FROM global_inventory"
        green_result = connection.execute(sqlalchemy.text(sql_green_ml))
        red_result = connection.execute(sqlalchemy.text(sql_red_ml))
        blue_result = connection.execute(sqlalchemy.text(sql_blue_ml))
        
        num_green_ml = green_result.fetchone()[0]
        num_red_ml = red_result.fetchone()[0]
        num_blue_ml = blue_result.fetchone()[0]
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into green potions.
        potion_recipes = [
                # Green potion recipe (assuming type 0)
                {"potion_type": [0, 100, 0, 0], "ml_per_potion": 50},
                # Red potion recipe (assuming type 1)
                {"potion_type": [100, 0, 0, 0], "ml_per_potion": 50},  # Adjust ml per potion
                # Blue potion recipe (assuming type 2)
                {"potion_type": [0, 0, 100, 0], "ml_per_potion": 50},  # Adjust ml per potion
            ]
        for recipe in potion_recipes:
            available_ml = num_green_ml if recipe["potion_type"] == [0, 100, 0, 0] else (  # Check potion type
                num_red_ml if recipe["potion_type"] == [100, 0, 0, 0] else num_blue_ml
            )
            ml_per_potion = recipe["ml_per_potion"]

            # Check if there's enough inventory for this potion type
            if available_ml >= ml_per_potion:
                # Calculate the number of potions to produce
                quantity = available_ml // ml_per_potion

                # Add the plan for bottling this potion type to the list
                plan.append({
                    "potion_type": recipe["potion_type"],
                    "quantity": quantity
                })
    return plan 
if __name__ == "__main__":
    print(get_bottle_plan())