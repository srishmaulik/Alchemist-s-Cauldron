from fastapi import APIRouter
import sqlalchemy
from src import database as db
router = APIRouter()
from sqlalchemy import select





@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog = []
    with db.engine.begin() as connection:
        potions_to_sell = "SELECT* FROM potions"
        result = connection.execute(sqlalchemy.text(potions_to_sell)).fetchall()
        
        for potion in result:
            if potion.quantity>0:
                catalog.append({
                    "sku": potion.item_sku,  
                    "name":potion.item_sku,
                    "quantity": potion.quantity,
                    "price": potion.price,
                    "potion_type": [potion.red_ml, potion.green_ml, potion.blue_ml, 0]
                })
    return catalog
       