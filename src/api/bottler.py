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
            sql_update_green_ml = sqlalchemy.text(
                "UPDATE global_inventory SET num_green_ml = num_green_ml - :green_ml"
            )
            connection.execute(sql_update_green_ml, {"green_ml": potion.potion_type[1]})
            sql_update_red_ml = sqlalchemy.text(
                "UPDATE global_inventory SET num_red_ml = num_red_ml - :red_ml"
            )
            connection.execute(sql_update_red_ml, {"red_ml": potion.potion_type[0]})

            sql_update_blue_ml = sqlalchemy.text(
                "UPDATE global_inventory SET num_blue_ml = num_blue_ml - :blue_ml"
            )
            connection.execute(sql_update_blue_ml, {"blue_ml": potion.potion_type[2]})

            # Generate potion name
            
            if potion.potion_type == [100,0,0,0]:
                item_sku = "Reddy_teddy"
            elif potion.potion_type == [0,100,0,0]:
                item_sku = "Greeny_dreamy"
            elif potion.potion_type == [0,0,100,0]:
                item_sku = "Blue_berry"
            elif potion.potion_type == [50,50,0,0]:
                item_sku = "Brownie"
            elif potion.potion_type == [60,40,0,0]:
                item_sku = "Brownie_60"
            elif potion.potion_type == [40,60,0,0]:
                item_sku = "Brownie_40"
            elif potion.potion_type == [50,0,50,0]:
                item_sku = "Purplie"
            elif potion.potion_type == [60,0,40,0]:
                item_sku = "Purplie_60"
            elif potion.potion_type == [40,0,60,0]:
                item_sku = "Purplie_40"
            elif potion.potion_type == [0,50,50,0]:
                item_sku = "Yellow_mellow"
            elif potion.potion_type == [0,40,60,0]:
                item_sku = "Yellow_mellow_60"
            elif potion.potion_type == [0,60,40,0]:
                item_sku = "Yellow_mellow_40"
            elif potion.potion_type == [34,33,33,0]:
                item_sku = "Treble"
            
            # Check if the potion already exists in the database
            existing_quantity = connection.execute(
                sqlalchemy.text("SELECT quantity FROM potions WHERE item_sku = :item_sku"),
                {"item_sku": item_sku}
            ).fetchone()
            
                # If the potion already exists, update the quantity by incrementing it by 1
            new_quantity = existing_quantity[0] + 1
            connection.execute(
                sqlalchemy.text("UPDATE potions SET quantity = :new_quantity WHERE item_sku = :item_sku"),
                {"new_quantity": new_quantity, "item_sku": item_sku}
            )
            
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
        ml_inventory = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory")).fetchone()
        num_red_ml, num_green_ml, num_blue_ml = ml_inventory    

        while num_red_ml+num_green_ml+num_blue_ml>100:
            if num_red_ml == 0 and num_green_ml>=50 and num_blue_ml>=50:
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
            elif num_red_ml == 0 and num_green_ml>=40 and num_green_ml<50 and num_blue_ml>=60:
                plan.append({"potion_type": [0, 40, 60, 0], "quantity": 1})
                num_green_ml-=40
                num_blue_ml-=60
            elif num_red_ml == 0 and num_blue_ml>=40 and num_blue_ml<50 and num_green_ml>=60:
                plan.append({"potion_type": [0, 60, 40, 0], "quantity": 1})
                num_green_ml-60
                num_blue_ml-=40
            elif num_red_ml >= 60 and num_green_ml>=40 and num_green_ml<50 and num_blue_ml==0:
                plan.append({"potion_type": [60, 40, 0, 0], "quantity": 1})
                num_green_ml-=40
                num_red_ml-=60
            elif num_green_ml >= 60 and num_red_ml>=40 and num_red_ml<50 and num_blue_ml==0:
                plan.append({"potion_type": [40, 60, 0, 0], "quantity": 1})
                num_red_ml-=40
                num_green_ml-=60
            elif num_red_ml >= 60 and num_green_ml==0 and num_blue_ml<50 and num_blue_ml>=40:
                plan.append({"potion_type": [60, 0, 40, 0], "quantity": 1})
                num_blue_ml-=40
                num_red_ml-=60           
            elif num_blue_ml >= 60 and num_green_ml==0 and num_red_ml<50 and num_red_ml>=40:
                plan.append({"potion_type": [40, 0, 60, 0], "quantity": 1})
                num_red_ml-=40
                num_blue_ml-=60
            
        print(plan)
        return plan


if __name__ == "__main__":
    print(get_bottle_plan())