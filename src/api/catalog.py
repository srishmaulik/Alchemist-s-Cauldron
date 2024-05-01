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
        # Query to sum the quantity for each potion type
        potion_quantities_query = """
        SELECT potion_id, SUM(quantity) AS total_quantity
        FROM potion_ledger_entries
        GROUP BY potion_id
        """

        # Fetch the results
        potion_quantities = connection.execute(sqlalchemy.text(potion_quantities_query)).fetchall()

        
        for potion_quantity in potion_quantities:
            potion_id, total_quantity = potion_quantity

            # Check if the total quantity is greater than 0
            if total_quantity > 0:
                # Retrieve potion details based on potion_id
                potion_details_query = sqlalchemy.text(
                    "SELECT item_sku, price, red_ml, green_ml, blue_ml FROM potions WHERE potion_id = :potion_id"
                )
                potion_details = connection.execute(potion_details_query, {"potion_id": potion_id}).fetchone()

                # Append potion to catalog
                if potion_details:
                    item_sku, price, red_ml, green_ml, blue_ml = potion_details
                    catalog.append({
                        "sku": item_sku,
                        "name": item_sku,
                        "quantity": total_quantity,
                        "price": price,
                        "potion_type": [red_ml, green_ml, blue_ml, 0]
                    })
    return catalog
       