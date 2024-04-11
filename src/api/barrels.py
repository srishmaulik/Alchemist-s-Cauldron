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
            # Update the quantity of delivered barrels in the database
            sql_update_quantity = f"UPDATE global_inventory SET num_green_ml = num_green_ml + {barrel.ml_per_barrel * barrel.quantity}"
            connection.execute(sqlalchemy.text(sql_update_quantity))
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    purchase_plan = []
    
    with db.engine.begin() as connection:
        # Fetch the current inventory of green ml from the global inventory table
        sql_green_ml = "SELECT num_green_ml FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql_green_ml))
        
        # Iterate over each row in the result
        for row in result:
            num_green_ml = row[0]

            # Mix all available green ml
            # Example: Always mix all available green ml if any exists

            # Check if the inventory of green ml is less than 10
    if num_green_ml < 10:
                # If inventory is less than 10, create a purchase plan for a new small green potion barrel
                purchase_plan.append({
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1
                })
    print(wholesale_catalog)

    return purchase_plan

