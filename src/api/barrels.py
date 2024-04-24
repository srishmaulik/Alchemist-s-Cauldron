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

            if potion_type == [0, 1, 0, 0]:  # Check for green potion type
                sql_update_quantity = f"UPDATE global_inventory SET num_green_ml = num_green_ml + {barrel.ml_per_barrel * barrel.quantity}"
            elif potion_type == [1, 0, 0, 0]:  # Check for red potion type
                sql_update_quantity = f"UPDATE global_inventory SET num_red_ml = num_red_ml + {barrel.ml_per_barrel * barrel.quantity}"
            elif potion_type == [0, 0, 1, 0]:  # Check for blue potion type (example)
                sql_update_quantity = f"UPDATE global_inventory SET num_blue_ml = num_blue_ml + {barrel.ml_per_barrel * barrel.quantity}"
            else:
            #     # Handle unexpected potion type (optional)
                raise Exception("invalid potion type")

            connection.execute(sqlalchemy.text(sql_update_quantity))

            sql_update_gold= f"UPDATE global_inventory SET gold = gold - {barrel.price*barrel.quantity}"
            connection.execute(sqlalchemy.text(sql_update_gold))

    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    purchase_plan = []
    
    with db.engine.begin() as connection:
        
        gold = "SELECT gold FROM global_inventory"
        
        gold_result = connection.execute(sqlalchemy.text(gold))
       
        total_gold = gold_result.fetchone()[0]

        for barrel in wholesale_catalog:
            barrel_name = barrel.sku
            
            if barrel.price <= total_gold and total_gold>0:
                   
                purchase_plan.append({
                    "sku": barrel_name,
                    "quantity": 1
                })
                total_gold -= barrel.price
                        


    print(wholesale_catalog)
    return purchase_plan
