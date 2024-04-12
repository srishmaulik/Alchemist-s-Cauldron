from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
   
 
    # Execute SQL statement
    


    return {"cart_id": 1}


class CartItem(BaseModel):
    quantity: int

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
   
                           
    return "OK"




class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    new_gold = 100  # Adjust this value based on your requirements
    potion_subtracted = 1  # Adjust this value based on your requirements
    total_potions_subtracted = 0
    total_gold = 0
    with db.engine.begin() as connection:
        sql_green = "SELECT num_green_potions FROM global_inventory"
        sql_red = "SELECT num_red_potions FROM global_inventory"
        sql_blue = "SELECT num_blue_potions FROM global_inventory"  # Add query for blue

        green_result = connection.execute(sqlalchemy.text(sql_green))
        red_result = connection.execute(sqlalchemy.text(sql_red))
        blue_result = connection.execute(sqlalchemy.text(sql_blue))  # Execute new query

        num_green = green_result.fetchone()[0]
        num_red = red_result.fetchone()[0]
        num_blue = blue_result.fetchone()[0]  # Access blue inventory
        if num_green<0:
            sql_update_statement4 = f"""
                UPDATE global_inventory
                SET 
                    num_green_potions = num_green_potions + {potion_subtracted}
            """
            connection.execute(sqlalchemy.text(sql_update_statement4))
        if num_green>0:
            total_gold+=100
            total_potions_subtracted+=1
            sql_update_statement = f"""
                UPDATE global_inventory
                SET gold = gold + {new_gold},
                    num_green_potions = num_green_potions - {potion_subtracted}
            """

            connection.execute(sqlalchemy.text(sql_update_statement))
        if num_red>0:
            total_gold+=100
            total_potions_subtracted+=1
            sql_update_statement2 = f"""
                UPDATE global_inventory
                SET gold = gold + {new_gold},
                    num_red_potions = num_red_potions - {potion_subtracted}
            """
            connection.execute(sqlalchemy.text(sql_update_statement2))
        if num_blue>0:
            total_gold+=100
            total_potions_subtracted+=1
            sql_update_statement3 = f"""
                UPDATE global_inventory
                SET gold = gold + {new_gold},
                    num_blue_potions = num_blue_potions - {potion_subtracted}
            """
            connection.execute(sqlalchemy.text(sql_update_statement3))

  
    return {"total_potions_bought": total_potions_subtracted , "total_gold_paid":total_gold }
