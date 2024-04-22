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
            sql_update_green_ml = f"UPDATE global_inventory SET num_green_ml = num_green_ml - {potion.potion_type[1]}"
            sql_update_red_ml = f"UPDATE global_inventory SET num_red_ml = num_red_ml - {potion.potion_type[0]}"
            sql_update_blue_ml = f"UPDATE global_inventory SET num_blue_ml = num_blue_ml - {potion.potion_type[2]}"
            sql_update_potion_red_ml = f"UPDATE potions SET red_ml = red_ml + {potion.potion_type[0]}"
            sql_update_potion_blue_ml = f"UPDATE potions SET blue_ml = blue_ml + {potion.potion_type[2]}"
            sql_update_potion_green_ml = f"UPDATE potions SET green_ml = green_ml + {potion.potion_type[1]}"

            if potion.potion_type[0] > 0 and potion.potion_type[1] > 0 and potion.potion_type[2] > 0:
                potion_name = "TRIFECTA_POTION"
                connection.execute(sqlalchemy.text(sql_update_green_ml))
                connection.execute(sqlalchemy.text(sql_update_red_ml))
                connection.execute(sqlalchemy.text(sql_update_blue_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_green_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_red_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_blue_ml))
            elif potion.potion_type[0] > 0 and potion.potion_type[1] > 0 and potion.potion_type[2] == 0:
                potion_name = "RED_GREEN_POTION"
                connection.execute(sqlalchemy.text(sql_update_green_ml))
                connection.execute(sqlalchemy.text(sql_update_red_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_green_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_red_ml))
            elif potion.potion_type[0] == 0 and potion.potion_type[1] > 0 and potion.potion_type[2] > 0:
                potion_name = "BLUE_GREEN_POTION"
                connection.execute(sqlalchemy.text(sql_update_blue_ml))
                connection.execute(sqlalchemy.text(sql_update_green_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_blue_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_green_ml))
            elif potion.potion_type[0] > 0 and potion.potion_type[1] == 0 and potion.potion_type[2] > 0:
                potion_name = "RED_BLUE_POTION"
                connection.execute(sqlalchemy.text(sql_update_red_ml))
                connection.execute(sqlalchemy.text(sql_update_blue_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_red_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_blue_ml))
            elif potion.potion_type[0] > 0 and potion.potion_type[1] == 0 and potion.potion_type[2] == 0:
                potion_name = "RED_POTION"
                connection.execute(sqlalchemy.text(sql_update_red_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_red_ml))
            elif potion.potion_type[0] == 0 and potion.potion_type[1] > 0 and potion.potion_type[2] == 0:
                potion_name = "GREEN_POTION"
                connection.execute(sqlalchemy.text(sql_update_green_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_green_ml))
            elif potion.potion_type[0] == 0 and potion.potion_type[1] == 0 and potion.potion_type[2] > 0:
                potion_name = "BLUE_POTION"
                connection.execute(sqlalchemy.text(sql_update_blue_ml))
                connection.execute(sqlalchemy.text(sql_update_potion_blue_ml))
                

            # Check if the potion already exists in the database
            existing_potion = connection.execute(
                sqlalchemy.text("SELECT * FROM potions WHERE potion_name = :potion_name"),
                {"potion_name": potion_name}
            ).fetchone()

            if existing_potion:
                # If the potion already exists, update the quantity by incrementing it by 1
                existing_quantity = existing_potion[2]
                new_quantity = existing_quantity + 1
                connection.execute(
                    sqlalchemy.text("UPDATE potions SET quantity = :new_quantity WHERE potion_name = :potion_name"),
                    {"new_quantity": new_quantity, "potion_name": potion_name}
                )
                
           

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
        sql_red_ml = f"SELECT num_red_ml FROM global_inventory"
        sql_green_ml = f"SELECT num_green_ml FROM global_inventory"
        sql_blue_ml = f"SELECT num_blue_ml FROM global_inventory"
        green_result = connection.execute(sqlalchemy.text(sql_green_ml))
        red_result = connection.execute(sqlalchemy.text(sql_red_ml))
        blue_result = connection.execute(sqlalchemy.text(sql_blue_ml))

        num_green_ml = green_result.fetchone()[0]
        num_red_ml = red_result.fetchone()[0]
        num_blue_ml = blue_result.fetchone()[0]
        total_ml = num_green_ml+num_blue_ml+num_red_ml

        while total_ml>=100:
            if num_green_ml == 0 and num_blue_ml == 0:
                
                total_ml -= 100
                plan.append({"potion_type": [100,0,0,0], "quantity": 1})

            elif num_red_ml == 0 and num_blue_ml == 0:
                total_ml -= 100
                plan.append({"potion_type": [0,100,0,0], "quantity": 1})

            elif num_red_ml == 0 and num_green_ml == 0:
                
                total_ml -= 100
                plan.append({"potion_type": [0,0,100,0], "quantity": 1})

            elif num_green_ml == 0 and num_red_ml > 0 and num_blue_ml > 0:
    # Calculate the total sum of available ml
                

                # Calculate the proportion based on the available ml for each color
                red_proportion = num_red_ml / total_ml * 100
                blue_proportion = num_blue_ml / total_ml * 100

                # Round the proportions to integers
                red_quantity = round(red_proportion)
                blue_quantity = round(blue_proportion)

                # Adjust the quantities to ensure the sum equals 100
                total_quantity = red_quantity + blue_quantity
                adjustment = 100 - total_quantity
                if adjustment != 0:
                    # Adjust one of the quantities to make the total sum exactly 100
                    if adjustment > 0:
                        # Increase the quantity of the larger proportion
                        if red_proportion > blue_proportion:
                            red_quantity += adjustment
                        else:
                            blue_quantity += adjustment
                    else:
                        # Decrease the quantity of the larger proportion
                        if red_proportion > blue_proportion:
                            red_quantity -= adjustment
                        else:
                            blue_quantity -= adjustment
                total_ml -=100
                plan.append({"potion_type":[red_quantity, 0, blue_quantity, 0], "quantity": 1})


            elif num_red_ml == 0 and num_blue_ml > 0 and num_green_ml > 0:
    # Calculate the total sum of available ml
                

                # Calculate the proportion based on the available ml for each color
                green_proportion = num_green_ml / total_ml * 100
                blue_proportion = num_blue_ml / total_ml * 100

                # Round the proportions to integers
                green_quantity = round(green_proportion)
                blue_quantity = round(blue_proportion)

                # Adjust the quantities to ensure the sum equals 100
                total_quantity = green_quantity + blue_quantity
                adjustment = 100 - total_quantity
                if adjustment != 0:
                    # Adjust one of the quantities to make the total sum exactly 100
                    if adjustment > 0:
                        # Increase the quantity of the larger proportion
                        if green_proportion > blue_proportion:
                            green_quantity += adjustment
                        else:
                            blue_quantity += adjustment
                    else:
                        # Decrease the quantity of the larger proportion
                        if green_proportion > blue_proportion:
                            green_quantity -= adjustment
                        else:
                            blue_quantity -= adjustment
                total_ml -=100            
                plan.append({"potion_type": [0, green_quantity, blue_quantity], "quantity": 1})
            elif num_blue_ml == 0 and num_red_ml > 0 and num_green_ml > 0:
    # Calculate the total sum of available ml
                

                # Calculate the proportion based on the available ml for each color
                green_proportion = num_green_ml / total_ml * 100
                red_proportion = num_red_ml / total_ml * 100

                # Round the proportions to integers
                green_quantity = round(green_proportion)
                blue_quantity = round(red_proportion)

                # Adjust the quantities to ensure the sum equals 100
                total_quantity = green_quantity + red_quantity
                adjustment = 100 - total_quantity
                if adjustment != 0:
                    # Adjust one of the quantities to make the total sum exactly 100
                    if adjustment > 0:
                        # Increase the quantity of the larger proportion
                        if green_proportion > red_proportion:
                            green_quantity += adjustment
                        else:
                            red_quantity += adjustment
                    else:
                        # Decrease the quantity of the larger proportion
                        if green_proportion > red_proportion:
                            green_quantity -= adjustment
                        else:
                            red_quantity -= adjustment
                total_ml -=100
                plan.append({"potion_type": [red_quantity, green_quantity, 0,0 ], "quantity": 1})
            elif num_green_ml > 0 and num_red_ml > 0 and num_blue_ml > 0:
    # Calculate the quantity based on the proportions
                total_ml = num_green_ml + num_red_ml + num_blue_ml

                # Calculate the proportion of each color
                green_proportion = num_green_ml / total_ml * 100
                red_proportion = num_red_ml / total_ml * 100
                blue_proportion = num_blue_ml / total_ml * 100

                # Round the proportions to integers
                green_quantity = round(green_proportion)
                red_quantity = round(red_proportion)
                blue_quantity = round(blue_proportion)

                # Adjust the quantities to ensure the sum equals 100
                total_quantity = green_quantity + red_quantity + blue_quantity
                adjustment = 100 - total_quantity
                if adjustment != 0:
                    # Adjust one of the quantities to make the total sum exactly 100
                    if adjustment > 0:
                        # Increase the quantity of the largest proportion
                        if green_proportion > red_proportion and green_proportion > blue_proportion:
                            green_quantity += adjustment
                        elif red_proportion > blue_proportion:
                            red_quantity += adjustment
                        else:
                            blue_quantity += adjustment
                    else:
                        # Decrease the quantity of the largest proportion
                        if green_proportion > red_proportion and green_proportion > blue_proportion:
                            green_quantity -= adjustment
                        elif red_proportion > blue_proportion:
                            red_quantity -= adjustment
                        else:
                            blue_quantity -= adjustment
                total_ml -=100
                # Add the mixed potion to the plan
                plan.append({"potion_type": [red_quantity, green_quantity, blue_quantity, 0], "quantity": 1})

        return plan 
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.
    
if __name__ == "__main__":
    print(get_bottle_plan())