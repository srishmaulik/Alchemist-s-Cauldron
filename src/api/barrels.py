from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import datetime
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
            ml = ""
            if potion_type == [0, 1, 0, 0]:  # Check for green potion type
                sql_update_quantity = f"UPDATE global_inventory SET num_green_ml = num_green_ml + {barrel.ml_per_barrel * barrel.quantity}"
                ml = "green_ml"
                connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers (green_ml)" "VALUES(:green_ml)" ), {"green_ml":barrel.ml_per_barrel * barrel.quantity})
            elif potion_type == [1, 0, 0, 0]:  # Check for red potion type
                sql_update_quantity = f"UPDATE global_inventory SET num_red_ml = num_red_ml + {barrel.ml_per_barrel * barrel.quantity}"
                ml = "red_ml"
                connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers (red_ml)" "VALUES(:red_ml)" ), {"red_ml":barrel.ml_per_barrel * barrel.quantity})
            elif potion_type == [0, 0, 1, 0]:  # Check for blue potion type (example)
                sql_update_quantity = f"UPDATE global_inventory SET num_blue_ml = num_blue_ml + {barrel.ml_per_barrel * barrel.quantity}"
                ml = "blue_ml"
                connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers (blue_ml)" "VALUES(:blue_ml)" ), {"blue_ml":barrel.ml_per_barrel * barrel.quantity})
            else:
            #     # Handle unexpected potion type (optional)
                raise Exception("invalid potion type")

            connection.execute(sqlalchemy.text(sql_update_quantity))

            sql_update_gold= f"UPDATE global_inventory SET gold = gold - {barrel.price*barrel.quantity}"
            connection.execute(sqlalchemy.text(sql_update_gold))
            account_id = connection.execute(sqlalchemy.text("SELECT account_id FROM accounts ORDER BY account_id DESC LIMIT 1")).scalar()
            description = f"bought {barrel.ml_per_barrel * barrel.quantity}{ml} for {barrel.price*barrel.quantity}"
            transaction_id = connection.execute(
            sqlalchemy.text("INSERT INTO account_transactions (created_at, description) "
                            "VALUES (:created_at, :description) RETURNING id"),
            {"created_at": datetime.datetime.now(), "description": description}
        ).scalar_one()

            connection.execute(
            sqlalchemy.text("INSERT INTO account_ledger_entries (account_id, account_transaction_id, change) "
                            "VALUES (:account_id, :transaction_id, :change)"),
            {"account_id": account_id, "transaction_id": transaction_id, "change": -barrel.price*barrel.quantity}
        )
            
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")
    return "OK"
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    purchase_plan = []
    with db.engine.begin() as connection:
        all_inventory = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory")).fetchone()
        
        num_red_ml, num_green_ml, num_blue_ml, gold = all_inventory
        for barrel in wholesale_catalog:
            if gold >= barrel.price:
                if gold <= 200:
                    if barrel.sku[:4] == "MINI":
                        purchase_plan.append({
                            "sku": barrel.sku,
                            "quantity": 1
                        })
                        gold -=barrel.price
                    elif barrel.sku[:5] == "SMALL":
                        if (barrel.potion_type == [1, 0, 0, 0] and num_red_ml <= 100) or \
                            (barrel.potion_type == [0, 1, 0, 0] and num_green_ml < 150) or \
                            (barrel.potion_type == [0, 0, 1, 0] and num_blue_ml < 200):
                            purchase_plan.append({
                                "sku": barrel.sku,
                                "quantity": 1
                            })
                            gold -= barrel.price
                else:
                    if barrel.price <= (gold // 2):
                        purchase_plan.append({
                            "sku": barrel.sku,
                            "quantity": 1
                        })
                        gold -= barrel.price
            else:
                continue
    print(wholesale_catalog)
    return purchase_plan

   


# def purchase_plan(barrels:list[Barrel]):
#     purchase_plan = []
#     with db.engine.begin() as connection:
#         all_inventory = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, gold FROM global_inventory"))         
#         num_red_ml,num_green_ml, num_blue_ml, gold  = all_inventory[0].fetchone()[0], all_inventory[1].fetchone()[0], all_inventory[2].fetchone()[0], all_inventory[3].fetchone()[0]
#         for barrel in barrels:
#             if gold>= barrel.price:
#                 if gold<=200:
#                     if barrel.sku[:4] == 'MINI':
#                         purchase_plan.append({
#                             "sku": barrel.sku,
#                             "quantity": 1
#                         })
                        
#                     elif barrel.sku[:5] == 'SMALL':
#                         if (barrel.potion_type == [1,0,0,0] and num_red_ml<200) or (barrel.potion_type == [0,1,0,0] and num_green_ml<200) or (barrel.potion_type == [0,0,1,0] and num_blue_ml<200):
#                             purchase_plan.append({
#                             "sku": barrel.sku,
#                             "quantity": 1
#                         })
#                     gold -= barrel.price
#                 else:
#                     if barrel.price<=(gold//2):
#                         purchase_plan.append({
#                             "sku": barrel.sku,
#                             "quantity": 1
#                         })
#                     else:
#                         continue

#     print(wholesale_catalog)
#     return purchase_plan

                



                            
                            
                      
                

            
#  purchase_plan = []
    
#     with db.engine.begin() as connection:
        
#         gold = "SELECT gold FROM global_inventory"
        
#         gold_result = connection.execute(sqlalchemy.text(gold))
       
#         total_gold = gold_result.fetchone()[0]

#         for barrel in wholesale_catalog:
#             barrel_name = barrel.sku
            
#             if barrel.price <= total_gold and total_gold>0:
                   
#                 purchase_plan.append({
#                     "sku": barrel_name,
#                     "quantity": 1
#                 })
#                 total_gold -= barrel.price
                        


#     print(wholesale_catalog)
#     return purchase_plan