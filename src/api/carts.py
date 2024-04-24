from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db


global_cart_id = 0
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
    """Create a new cart."""
    with db.engine.begin() as connection:
        # Retrieve the last cart_id from the carts table
        last_cart_id = connection.execute(
            sqlalchemy.text("SELECT cart_id FROM carts ORDER BY cart_id DESC LIMIT 1")
        ).scalar()
        
        # Increment the last cart_id by one to get the new cart_id
        cart_id = last_cart_id + 1 if last_cart_id is not None else 1
        
        # Insert the new cart_id into the carts table
        connection.execute(
            sqlalchemy.text("INSERT INTO carts (cart_id) VALUES (:cart_id)"),
            {"cart_id": cart_id}
        )
        
        # Return the generated cart_id
        return {"cart_id": str(cart_id)}
    
   
class CartItem(BaseModel):
    quantity: int
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        # Check if the cart exists
        cart_exists = connection.execute(
            sqlalchemy.text("SELECT EXISTS(SELECT 1 FROM carts WHERE cart_id = :cart_id)"),
            {"cart_id": cart_id}
        ).fetchone()[0]
        
        # Query the maximum existing cart_item_id for the cart_id
        last_cart_id = connection.execute(
            sqlalchemy.text("SELECT cart_id FROM carts ORDER BY cart_id DESC LIMIT 1")
        ).scalar()
        
        # Increment the last cart_id by one to get the new cart_id
        cart_item_id = last_cart_id + 1 if last_cart_id is not None else 1
        
        # If no rows exist for the specified cart_id, set cart_item_id to 1
        
        
        # Query the potion_id based on the item_sku
        potion_id_query = sqlalchemy.text(
            "SELECT potion_id FROM potions WHERE item_sku = :item_sku"
        )
        potion_id_result = connection.execute(potion_id_query, {"item_sku": item_sku}).fetchone()
        potion_id = potion_id_result[0]
        
        # Insert the item into cart_items
        connection.execute(
            sqlalchemy.text(
                "INSERT INTO cart_items (cart_item_id, cart_id, potion_id, quantity) "
                "VALUES (:cart_item_id, :cart_id, :potion_id, :quantity)"
            ),
            {"cart_item_id": cart_item_id, "cart_id": cart_id, "potion_id": potion_id, "quantity": cart_item.quantity}
        )
        
    return f"Item {item_sku} added to cart {cart_id}"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    with db.engine.begin() as connection:
        # Fetch items from the cart
        items = connection.execute(
            sqlalchemy.text("SELECT * FROM cart_items WHERE cart_id = :cart_id"),
            {"cart_id": cart_id}
        ).fetchall()
        total_price = 0
        for item in items:
            quantity = item.quantity
            
            # Fetch potion details
            potion_details = connection.execute(
                sqlalchemy.text("SELECT * FROM potions WHERE potion_id = :potion_id"),
                {"potion_id": item.potion_id}  # Provide the potion_id value
            ).fetchone()

            total_price += potion_details.price * quantity
            
            # Update potion quantity
            connection.execute(
                sqlalchemy.text(
                    "UPDATE potions "
                    "SET quantity = quantity - :quantity "
                    "WHERE potion_id = :potion_id"
                ),
                {"quantity": quantity, "potion_id": item.potion_id}
            )
            
            # Remove items from the cart
            connection.execute(
                sqlalchemy.text("DELETE FROM cart_items WHERE cart_id = :cart_id"),
                {"cart_id": cart_id}
            )
            
            # Update global inventory
            sql_update_statement = f"""
                UPDATE global_inventory
                SET gold = gold + {potion_details.price * quantity}
            """
            connection.execute(sqlalchemy.text(sql_update_statement))

    return {"cart_id": cart_id, "total_price": total_price}
    