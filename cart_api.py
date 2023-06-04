from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()
security = HTTPBearer()


# Product and cart storage functions
class Product(BaseModel):
  product_id: int
  image: str
  name: str
  price: float
  quantity: int


products_db = {
  1:
  Product(product_id=1,
          image="image1.avif",
          name="Product 1",
          price=10.0,
          quantity=5),
  2:
  Product(product_id=2,
          image="image2.jpg",
          name="Product 2",
          price=20.0,
          quantity=10),
  3:
  Product(product_id=3,
          image="image3.jpg",
          name="Product 3",
          price=15.0,
          quantity=8)
}

cart_db = {}  # In-memory cart storage


def get_product(product_id: int):
  return products_db.get(product_id)


# CRUD APIs for cart management
@app.post("/cart/add/{product_id}")
def add_product_to_cart(
  product_id: int,
  quantity: int,
  credentials: HTTPAuthorizationCredentials = Depends(security)):
  token = credentials.credentials
  username = verify_token(token)
  if not username:
    raise HTTPException(status_code=401, detail="Invalid token")

  product = get_product(product_id)
  if not product:
    raise HTTPException(status_code=404, detail="Product not found")

  if product_id in cart_db:
    cart_db[product_id]["quantity"] += quantity
  else:
    cart_db[product_id] = {"product": product, "quantity": quantity}

  return {"message": "Product added to cart successfully"}


@app.put("/cart/update/{product_id}")
def update_product_quantity(
  product_id: int,
  quantity: int,
  credentials: HTTPAuthorizationCredentials = Depends(security)):
  token = credentials.credentials
  username = verify_token(token)
  if not username:
    raise HTTPException(status_code=401, detail="Invalid token")

  product = get_product(product_id)
  if not product:
    raise HTTPException(status_code=404, detail="Product not found")

  if product_id in cart_db:
    cart_db[product_id]["quantity"] = quantity
    return {"message": "Product quantity updated successfully"}

  raise HTTPException(status_code=404, detail="Product not found in cart")


@app.delete("/cart/delete/{product_id}")
def delete_product_from_cart(
  product_id: int,
  credentials: HTTPAuthorizationCredentials = Depends(security)):
  token = credentials.credentials
  username = verify_token(token)
  if not username:
    raise HTTPException(status_code=401, detail="Invalid token")

  if product_id in cart_db:
    del cart_db[product_id]
    return {"message": "Product deleted from cart successfully"}

  raise HTTPException(status_code=404, detail="Product not found in cart")


@app.get("/cart", response_model=Dict[int, Dict[str, int]])
def get_cart_details(
    credentials: HTTPAuthorizationCredentials = Depends(security)):
  token = credentials.credentials
  username = verify_token(token)
  if not username:
    raise HTTPException(status_code=401, detail="Invalid token")

  total_price = 0
  total_quantity = 0
  cart_items = {}

  for product_id, cart_item in cart_db.items():
    product = cart_item["product"]
    quantity = cart_item["quantity"]
    cart_items[product_id] = {"name": product.name, "quantity": quantity}
    total_price += product.price * quantity
    total_quantity += quantity

  cart_info = {
    "total_price": total_price,
    "total_quantity": total_quantity,
    "cart_items": cart_items
  }
  return cart_info


# Protected API endpoints using authentication
def verify_token(token: str):
  try:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload["sub"]
  except jwt.ExpiredSignatureError:
    return None
  except jwt.InvalidTokenError:
    return None


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8001)
