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

	bakery_orders = relationship("Order", back_populates="owner", foreign_keys="Order.owner_id")

class Order(Base):
	__tablename__ = "orders"

	id = Column(Integer, primary_key=True, index=True)
	item_name = Column(String, nullable=False)
	user_id = Column(Integer, ForeignKey("users.id"))#customer ordered
	owner_id = Column(Integer, ForeignKey("users.id"))#bakery received
	created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
	status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)

	customer = relationship("User", back_populates="customer_orders",foreign_keys=[user_id])

	owner = relationship("User", back_populates="bakery_orders", foreign_keys=[owner_id])

class Bakery(Base):
	__tablename__ = "bakeries"

	id=Column(Integer, primary_key=True, index=True)
	name=Column(String, nullable=False)
	description=Column(String)
	location=Column(String)

	owner_id = Column(Integer, ForeignKey("users.id"))
