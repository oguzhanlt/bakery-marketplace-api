import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class UserRole(enum.Enum):
	customer = "customer"
	bakery_owner = "bakery_owner"

class OrderStatus(enum.Enum):
	pending = "pending"
	accepted = "accepted"
	denied = "denied"
	preparing = "preparing"
	ready = "ready"
	completed = "completed"

class User(Base):
	__tablename__ = "users"
	
	id = Column(Integer, primary_key = True, index=True)
	username = Column(String, nullable=False)
	email = Column(String, nullable=False, unique=True)
	hashed_password = Column(String, nullable=False)
	role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
	
	customer_orders = relationship("Order", back_populates="customer", foreign_keys="Order.user_id")

	bakeries = relationship("Bakery", back_populates="owner")

class Order(Base):
	__tablename__ = "orders"

	id = Column(Integer, primary_key=True, index=True)
	menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
	quantity = Column(Integer)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)#customer ordered
	bakery_id = Column(Integer, ForeignKey("bakeries.id"), nullable=False)#bakery received
	created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
	status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
	price_at_order = Column(Integer, nullable=False)
	customer = relationship("User", back_populates="customer_orders",foreign_keys=[user_id])

	bakery  = relationship("Bakery", back_populates="orders")
	menu_item = relationship("MenuItem")

class Bakery(Base):
	__tablename__ = "bakeries"

	id=Column(Integer, primary_key=True, index=True)
	name=Column(String, nullable=False)
	description=Column(String)
	location=Column(String)

	owner_id = Column(Integer, ForeignKey("users.id"))

	owner = relationship("User", back_populates="bakeries")
	orders = relationship("Order", back_populates="bakery")

	menu_items = relationship("MenuItem", back_populates="bakery")

class MenuItem(Base):
	__tablename__ = "menu_items"

	id = Column(Integer, primary_key=True, index=True)
	bakery_id = Column(Integer, ForeignKey("bakeries.id"), nullable=False)
	name = Column(String, nullable=False)
	description= Column(String)
	price=Column(Integer, nullable=False)

	bakery = relationship("Bakery", back_populates="menu_items")

	
