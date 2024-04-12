from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            potion_type = barrel.potion_type

            if potion_type == [0, 100, 0, 0]:  # Check for green potion type
                sql_update_quantity = f"UPDATE global_inventory SET num_green_ml = num_green_ml + {barrel.ml_per_barrel * barrel.quantity}"
            elif potion_type == [100, 0, 0, 0]:  # Check for red potion type
                sql_update_quantity = f"UPDATE global_inventory SET num_red_ml = num_red_ml + {barrel.ml_per_barrel * barrel.quantity}"
            elif potion_type == [0, 0, 100, 0]:  # Check for blue potion type (example)
                sql_update_quantity = f"UPDATE global_inventory SET num_blue_ml = num_blue_ml + {barrel.ml_per_barrel * barrel.quantity}"
            else:
            #     # Handle unexpected potion type (optional)
                return {"error": "Invalid potion type"}

            connection.execute(sqlalchemy.text(sql_update_quantity))

    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    purchase_plan = []
    
    with db.engine.begin() as connection:
        # Fetch the current inventory of green ml from the global inventory table
        sql_green_ml = "SELECT num_green_ml FROM global_inventory"
        sql_red_ml = "SELECT num_red_ml FROM global_inventory"
        sql_blue_ml = "SELECT num_blue_ml FROM global_inventory"  # Add query for blue

        green_result = connection.execute(sqlalchemy.text(sql_green_ml))
        red_result = connection.execute(sqlalchemy.text(sql_red_ml))
        blue_result = connection.execute(sqlalchemy.text(sql_blue_ml))  # Execute new query

        num_green_ml = green_result.fetchone()[0]
        num_red_ml = red_result.fetchone()[0]
        num_blue_ml = blue_result.fetchone()[0]  # Access blue inventory

        if num_green_ml < 10:
            # Purchase plan for green potion barrel
            purchase_plan.append({
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1
            })

        if num_red_ml < 10:
            # Purchase plan for red potion barrel
            purchase_plan.append({
                "sku": "SMALL_RED_BARREL",
                "quantity": 1
            })

        if num_blue_ml < 10:  # Check for blue inventory
            # Purchase plan for blue potion barrel (example)
            purchase_plan.append({
                "sku": "SMALL_BLUE_BARREL",  
                "quantity": 1
            })


    print(wholesale_catalog)
    return purchase_plan

