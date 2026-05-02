from pydantic import BaseModel
from .models import UserRole, OrderStatus


class UserCreate(BaseModel):
	username: str
	email: str
	password: str
	role: UserRole	

class OrderCreate(BaseModel):
	item_name: str
	bakery_id: int

class UserLogin(BaseModel):
	email: str
	password: str


class OrderStatusUpdate(BaseModel):
	status: OrderStatus


class BakeryCreate(BaseModel):
	name: str
	description: str
	location: str
