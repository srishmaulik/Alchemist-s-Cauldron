from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import math
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
            # Update global inventory

            # Generate potion name
            
            if potion.potion_type == [100,0,0,0]:
                item_sku = "Reddy_teddy"
            elif potion.potion_type == [0,100,0,0]:
                item_sku = "Greeny_dreamy"
            elif potion.potion_type == [0,0,100,0]:
                item_sku = "Blue_berry"
            elif potion.potion_type == [50,50,0,0]:
                item_sku = "Brownie"
            
            elif potion.potion_type == [50,0,50,0]:
                item_sku = "Purplie"
            
            elif potion.potion_type == [0,50,50,0]:
                item_sku = "Yellow_mellow"
            
            elif potion.potion_type == [34,33,33,0]:
                item_sku = "Treble"
            elif potion.potion_type == [25,25,25,25]:
                item_sku = "Fourden"
            elif potion.potion_type == [0,0,0,100]:
                item_sku = "Dark_knight"
            
            # Check if the potion already exists in the database
            
            potion_id = connection.execute(sqlalchemy.text("SELECT potion_id FROM potions WHERE item_sku = :item_sku"),{"item_sku": item_sku}).scalar()
                # If the potion already exists, update the quantity by incrementing it by 1
            
            connection.execute(
                sqlalchemy.text("INSERT INTO barrel_ledgers(red_ml, green_ml, blue_ml, dark_ml)" "VALUES(:red_ml, :green_ml, :blue_ml, :dark_ml)"),
                {"red_ml": -potion.potion_type[0]*potion.quantity, "green_ml": -potion.potion_type[1]*potion.quantity, "blue_ml":-potion.potion_type[2]*potion.quantity, "dark_ml": -potion.potion_type[3]*potion.quantity}
            )
            connection.execute(sqlalchemy.text("INSERT INTO potion_ledger_entries(potion_id, quantity)" "VALUES(:potion_id, :quantity)"),{"potion_id": potion_id, "quantity": potion.quantity})
                # If the potion does not exist, insert a new row with quantity 1
                
    print(f"Potions delivered: {potions_delivered} Order ID: {order_id}")

    return "OK"
      

        

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    plan = []
    
    with db.engine.begin() as connection:
         # Fetch the current inventory of green ml from the global inventory table
        ml_inventory = connection.execute(sqlalchemy.text("SELECT SUM(red_ml), SUM(green_ml), SUM(blue_ml), SUM(dark_ml) FROM barrel_ledgers")).fetchone()
        if ml_inventory:
            num_red_ml, num_green_ml, num_blue_ml, num_dark_ml = ml_inventory    

            while num_red_ml+num_green_ml+num_blue_ml+num_dark_ml>100:

                if num_dark_ml>=100:
                    plan.append({"potion_type": [0,0,0,100]})
                    num_dark_ml-=100
                elif num_dark_ml>=25 and num_blue_ml>=25 and num_green_ml>=25 and num_red_ml>=25:
                    plan.append({"potion_type": [25, 25, 25, 25], "quantity": 1})
                    num_green_ml-=25
                    num_blue_ml-=25
                    num_dark_ml -=25
                    num_red_ml -=25
                elif num_red_ml == 0 and num_green_ml>=50 and num_blue_ml>=50:
                    plan.append({"potion_type": [0, 50, 50, 0], "quantity": 1})
                    num_green_ml-=50
                    num_blue_ml-=50
                elif num_red_ml >= 50 and num_green_ml>=50 and num_blue_ml==0:
                    plan.append({"potion_type": [50, 50, 0, 0], "quantity": 1})
                    num_green_ml-=50
                    num_red_ml-=50
                elif num_red_ml >= 50 and num_green_ml==0 and num_blue_ml>=50:
                    plan.append({"potion_type": [50, 0, 50, 0], "quantity": 1})
                    num_blue_ml-=50
                    num_red_ml-=50
                elif num_red_ml>=34 and num_green_ml>=33 and num_blue_ml>=33:
                    plan.append({"potion_type": [34, 33, 33, 0], "quantity": 1})
                    num_blue_ml-=33
                    num_red_ml-=34
                    num_blue_ml-=33
                elif num_red_ml>=100 and num_green_ml==0 and num_blue_ml==0:
                    plan.append({"potion_type": [100, 0, 0, 0], "quantity": 1})
                    num_red_ml-=100
                elif num_red_ml==0 and num_green_ml>=100 and num_blue_ml==0:
                    plan.append({"potion_type": [0, 100, 0, 0], "quantity": 1})
                    num_green_ml-=100
                elif num_red_ml==0 and num_green_ml==0 and num_blue_ml>=100:
                    plan.append({"potion_type": [0, 0, 100, 0], "quantity": 1})
                    num_blue_ml-=100
            
            
        print(plan)
        return plan


if __name__ == "__main__":
    print(get_bottle_plan())