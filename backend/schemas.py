from pydantic import BaseModel
from .models import UserRole, OrderStatus


class UserCreate(BaseModel):
	username: str
	email: str
	password: str
	role: UserRole

class OrderCreate(BaseModel):
	bakery_id: int
	menu_item_id: int
	quantity: int

class UserLogin(BaseModel):
	email: str
	password: str


class OrderStatusUpdate(BaseModel):
	status: OrderStatus


class BakeryCreate(BaseModel):
	name: str
	description: str
	location: str


class MenuItemCreate(BaseModel):
	bakery_id: int
	name: str
	description: str
	price: float
