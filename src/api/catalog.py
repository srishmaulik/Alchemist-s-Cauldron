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
    with db.engine.begin() as connection:
        result1 = "SELECT num_green_potions FROM global_inventory"
        green_result = connection.execute(sqlalchemy.text(result1))
        result2 = "SELECT num_red_potions FROM global_inventory"
        red_result = connection.execute(sqlalchemy.text(result2))
        result3 = "SELECT num_blue_potions FROM global_inventory"
        blue_result = connection.execute(sqlalchemy.text(result3))

    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": green_result,
                "price": 200,
                "potion_type": [0, 100, 0, 0]
            }
        ],[{ "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": red_result,
                "price": 200,
                "potion_type": [100, 0, 0, 0]}
                ],[{ "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": blue_result,
                "price": 200,
                "potion_type": [0, 0, 100, 0]}]
        