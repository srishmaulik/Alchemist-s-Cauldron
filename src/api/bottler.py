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

    with db.engine.begin() as connection:
        for potion in potions_delivered:
            # Construct potion name based on potion type
            potion_name = f"RED_{potion.potion_type[0]}_GREEN_{potion.potion_type[1]}_BLUE_{potion.potion_type[2]}"

            # Check if the potion already exists in the database
            existing_potion = connection.execute(sqlalchemy.text(f"SELECT * FROM potions WHERE potion_name = '{potion_name}'")).fetchone()

            if existing_potion:
                # If the potion already exists, update the quantity and price
                existing_quantity = existing_potion['quantity']
                new_quantity = existing_quantity + potion.quantity
                
                connection.execute(sqlalchemy.text(f"UPDATE potions SET quantity = {new_quantity}, WHERE potion_name = '{potion_name}'"))
            else:
                # If the potion does not exist, insert a new row
                price_per_bottle = round(0.5 * potion.potion_type[1] + 0.45 * potion.potion_type[0] + 0.4 * potion.potion_type[2])
                connection.execute(sqlalchemy.text(f"INSERT INTO potions (potion_name, red_ml, green_ml, blue_ml, quantity, price) VALUES ('{potion_name}', {potion.potion_type[0]}, {potion.potion_type[1]}, {potion.potion_type[2]}, {potion.quantity}, {price_per_bottle})"))

            # Update global inventory based on potion type
            sql_update_green_ml = f"UPDATE global_inventory SET num_green_ml = num_green_ml - {potion.quantity*potion.potion_type[1]}"
            sql_update_red_ml = f"UPDATE global_inventory SET num_red_ml = num_red_ml - {potion.quantity*potion.potion_type[0]}"
            sql_update_blue_ml = f"UPDATE global_inventory SET num_blue_ml = num_blue_ml - {potion.quantity*potion.potion_type[2]}"

            connection.execute(sqlalchemy.text(sql_update_green_ml))
            connection.execute(sqlalchemy.text(sql_update_red_ml))
            connection.execute(sqlalchemy.text(sql_update_blue_ml))

    print(f"Potions delivered: {potions_delivered} Order ID: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan(potions_delivered: list[PotionInventory]):
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
        available_green_ml = num_green_ml
        available_red_ml = num_red_ml
        available_blue_ml = num_blue_ml
        
        
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    
        
        for recipe in potions_delivered:
            quantity = 0
            for i in range(0, recipe.quantity):
            # Check if there's enough inventory for this potion type
                if available_green_ml >= recipe.potion_type[1] and available_red_ml>=recipe.potion_type[0] and available_blue_ml>=recipe.potion_type[2]:

                    # Calculate the number of potions to produce
                    quantity += 1
                    available_green_ml -= recipe.potion_type[1]
                    available_red_ml -= recipe.potion_type[0]
                    available_blue_ml -= recipe.potion_type[2]

                # Add the plan for bottling this potion type to the list
            plan.append({
                "potion_type": recipe.potion_type,
                "quantity": quantity
            })
    return plan 
if __name__ == "__main__":
    print(get_bottle_plan())