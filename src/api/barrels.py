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
                
                ml = "green_ml"
                connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers (green_ml)" "VALUES(:green_ml)" ), {"green_ml":barrel.ml_per_barrel * barrel.quantity})
            elif potion_type == [1, 0, 0, 0]:  # Check for red potion type
                ml = "red_ml"
                connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers (red_ml)" "VALUES(:red_ml)" ), {"red_ml":barrel.ml_per_barrel * barrel.quantity})
            elif potion_type == [0, 0, 1, 0]:  # Check for blue potion type (example)
                ml = "blue_ml"
                connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers (blue_ml)" "VALUES(:blue_ml)" ), {"blue_ml":barrel.ml_per_barrel * barrel.quantity})
            elif potion_type == [0,0,0,1]:
                ml = "dark_ml"
                connection.execute(sqlalchemy.text("INSERT INTO barrel_ledgers (dark_ml)" "VALUES(:dark_ml)" ), {"dark_ml":barrel.ml_per_barrel * barrel.quantity})
         
            

            
            account_id = connection.execute(sqlalchemy.text("SELECT account_id FROM accounts ORDER BY account_id DESC LIMIT 1")).scalar()
            description = f"bought {barrel.ml_per_barrel * barrel.quantity} {ml} for {barrel.price*barrel.quantity}"
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
        gold_balance_query = sqlalchemy.text(
            "SELECT SUM(change) FROM account_ledger_entries WHERE account_id IS NOT NULL"
        )
        gold = connection.execute(gold_balance_query).scalar_one()
        all_inventory = connection.execute(sqlalchemy.text("SELECT SUM(red_ml), SUM(green_ml), SUM(blue_ml), SUM(dark_ml) FROM barrel_ledgers")).fetchone()
        num_red_ml, num_green_ml, num_blue_ml, num_dark_ml = all_inventory
        all_potions_query = sqlalchemy.text(
                "SELECT p.item_sku, SUM(ple.quantity) AS total_quantity "
                "FROM potion_ledger_entries AS ple "
                "JOIN potions AS p ON ple.potion_id = p.potion_id "
                "GROUP BY p.item_sku"
            )
        #all_potions_result = connection.execute(all_potions_query)

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
                        if (barrel.potion_type == [1, 0, 0, 0] and num_red_ml < 100) or \
                            (barrel.potion_type == [0, 1, 0, 0] and num_green_ml < 100) or \
                            (barrel.potion_type == [0,0,0,1] and num_dark_ml<100) or \
                            (barrel.potion_type == [0, 0, 1, 0] and num_blue_ml < 100):
                            purchase_plan.append({
                                "sku": barrel.sku,
                                "quantity": 1
                            })
                            gold -= barrel.price
                else:
                    #if (barrel.potion_type == [1,0,0,0] and num_red_ml>500):
                    if barrel.price <= 500:
                        if (barrel.potion_type == [1,0,0,0] and num_red_ml>2000) or (barrel.potion_type == [0,1,0,0] and num_green_ml>2000) or (barrel.potion_type == [0,0,1,0] and num_blue_ml>2000):
                            continue
                        else:
                            purchase_plan.append({
                                "sku": barrel.sku,
                                "quantity": 1
                            })
                        gold -= barrel.price
                    else:
                        if (barrel.potion_type == [1,0,0,0] and num_red_ml>2000) or (barrel.potion_type == [0,1,0,0] and num_green_ml>2000) or (barrel.potion_type == [0,0,1,0] and num_blue_ml>2000):
                            continue
                        elif barrel.price<=(gold//2):
                            purchase_plan.append({
                            "sku": barrel.sku,
                            "quantity": 1
                        })
                            gold -=barrel.price
                            
                        else: 
                            continue
    print(wholesale_catalog)
    return purchase_plan

   
