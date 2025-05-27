from typing import List, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import uvicorn
from passlib.context import CryptContext



app = FastAPI(title='Local Food Ordering API')

# hashing model
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# in-memory databases
menu_items : Dict[str, dict] = {}
orders: Dict[str, dict] = {}
users_db: Dict[str, dict] = {}

# Role constants
class Role:
  ADMIN = 'admin'
  MANAGER = 'manager'
  USER = 'user'

# Pydantic Data models

class MenuItem(BaseModel):
  id: str
  name: str
  price: float

class MenuItemCreate(BaseModel):
  name: str
  price: float

class OrderItem(BaseModel):
  menu_item_id: str
  quantity: int

class Order(BaseModel):
  id: str
  items: List[OrderItem]
  total_price: float

class OrderCreate(BaseModel):
  items: List[OrderItem]

class RegisterUser(BaseModel):
  username: str
  password: str
  role: str = Role.USER #default role

class LoginUser(BaseModel):
  username: str
  password: str



@app.get("/")
def read_root():
    return {"message": "Your FastAPI app is running!"}

# Menu endpoints
@app.get('/menu/', response_model=List[MenuItem])
def get_menu():
  return list(menu_items.values())

@app.post('/menu/', response_model=MenuItem)
def create_menu_item(item: MenuItemCreate):
  item_id = str(uuid4())
  menu_item = MenuItem(id=item_id, name=item.name, price=item.price)
  menu_items[item_id] = menu_item
  return menu_item

# Order endpoints
@app.post('/orders/', response_model=Order)
def create_order(order: OrderCreate):
  total_price = 0.0
  for item in order.items:
    if item.menu_item_id not in menu_items:
      raise HTTPException(status_code=404, detail=f'Menu item {item.menu_item_id} not found')
    total_price += menu_items[item.menu_item_id].price * item.quantity

  order_id = str(uuid4())
  new_order = Order(id=order_id, items=order.items, total_price=total_price)
  orders[order_id] = new_order
  return new_order

@app.get('/orders/', response_model=List[Order])
def list_orders():
  return list(orders.values())

@app.get('orders/order_id', response_model=Order)
def get_order(order_id: str):
  if order_id not in orders:
    if order_id not in orders:
      raise HTTPException(status_code=404, detail='Order not found')
    return orders[order_id]
  


# Authentication Routes
@app.post('/register/')
def register_user(user: RegisterUser):
  if user.username in users_db:
    raise HTTPException(status_code=400, detail='User already exists')
  
  if user.role not in [Role.ADMIN, Role.MANAGER, Role.USER]:
    raise HTTPException(status_code=400, detail='Invalid role')
  
  #password hashing
  hashed_password = pwd_context.hash(user.password)

  #creating records
  users_db[user.username] = {
    'username': user.username,
    'hashed_password': hashed_password,
    'role': user.role
  }

  return {
    'msg': f"User '{user.username}' created successfully",
    'role': user.role
  }

@app.post('/login/')
def login_user(user: LoginUser):
  if user.username in users_db:
    hashed_password = pwd_context.hash(user.password)
    if users_db[user.password] == hashed_password:
      #login user
      return {
        'msg': 'Login successful'
      }
  else:
    return {
      'msg': 'Login unsuccessful'
    }
  

# if __name__ == '__main__':
#   uvicorn.run('main:app', reload=True)