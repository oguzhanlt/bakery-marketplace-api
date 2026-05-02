from fastapi import FastAPI
from .database import engine, Base
from . import models
from .database import SessionLocal
from .schemas import UserCreate, OrderCreate, UserLogin, OrderStatusUpdate, BakeryCreate
from .models import User, Order, Bakery
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)

def create_access_token(data: dict):
	to_encode = data.copy()

	expire = datetime.utcnow() + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode.update({"exp": expire})
	
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

	return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		user_email = payload.get("sub")
		user_id = payload.get("user_id")
		user_role = payload.get("role")		

		if user_email is None:
			raise HTTPException(status_code=401, detail="Invalid token")

		return {"email": user_email, "user_id":user_id, "role": user_role}

	except:
		raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
	db = SessionLocal()

	user = db.query(User).filter(User.id == current_user["user_id"]).first()

	db.close()

	return {"id":user.id, "username":user.username, "email":user.email}

@app.get("/")
def home():
	return {"message": "backend running"}


@app.post("/users")
def create_user(user: UserCreate):
	db = SessionLocal()
	existing_user = db.query(User).filter(User.email == user.email).first()
	if existing_user:
		db.close()
		return {"message": "this email already exists"}
	
	new_user = User(	
		username=user.username,
		email=user.email,
		hashed_password = pwd_context.hash(user.password),
		role = user.role
	) 

	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	db.close()

	return new_user

@app.get("/users")
def get_users():
	db = SessionLocal()

	users = db.query(User).all()

	db.close()
	return users

@app.get("/users/{user_id}")
def get_user(user_id: int):
	db = SessionLocal()

	user = db.query(User).filter(User.id == user_id).first()

	db.close()

	return user

@app.delete("/users/{user_id}")
def delete_user(user_id : int):
	db = SessionLocal()

	user = db.query(User).filter(User.id == user_id).first()
	if user:
		db.delete(user)
		db.commit()
		db.close()
		return {"message": "user deleted"}

	db.close()
	return {"message": "user not found"}

@app.put("/users/{user_id}")
def update_user(user_id: int, updated_user: UserCreate):
	db = SessionLocal()

	user = db.query(User).filter(User.id == user_id).first()

	if user:
		user.username = updated_user.username
		user.email = updated_user.email
		
		db.commit()
		db.refresh(user)
		db.close()
		return user
	
	db.close()
	return {"message": "user not found"}


@app.post("/orders")
def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
	db = SessionLocal()
	
	new_order = Order(item_name=order.item_name, user_id=current_user["user_id"], bakery_id = order.bakery_id)
	
	db.add(new_order)
	db.commit()
	db.refresh(new_order)
	db.close()
	return new_order


@app.get("/users/{user_id}/orders")
def get_user_orders(user_id: int):
	db= SessionLocal()

	orders = db.query(Order).filter(Order.user_id == user_id).all()

	db.close()

	return orders

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
	db=SessionLocal()
	user = db.query(User).filter(User.email == form_data.username).first()
	
	if not user:
		db.close()
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	password_ok = pwd_context.verify(form_data.password, user.hashed_password)
	db.close()
	
	if not password_ok:
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	access_token = create_access_token(data={"sub": user.email, "user_id": user.id, "role": user.role.value})	

	return {
		"access_token":access_token,
		"token_type": "bearer"
	}


@app.get("/my-orders")
def get_my_orders(current_user: dict = Depends(get_current_user)):
	db = SessionLocal()
	
	if current_user["role"] != "customer":
		raise HTTPException(status_code=403)

	orders = db.query(Order).filter(Order.user_id == current_user["user_id"]).all()

	db.close()

	return orders

#@app.post("/menu-items")
#def create_menu_item()


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status_update: OrderStatusUpdate, current_user: dict= Depends(get_current_user)):
	db = SessionLocal()

	if current_user["role"] != "bakery_owner":
		db.close()
		raise HTTPException(status_code=403)
	
	order = db.query(Order).filter(Order.id == order_id).first()

	if not order:
		db.close()
		raise HTTPException(status_code=404, detail="Order not found")
	if order.bakery.owner_id != current_user["user_id"]: # I would like to note that this is not a good design principle
		db.close()
		raise HTTPException(status_code=403, detail="Not your order")

	order.status = status_update.status
	
	db.commit()
	db.refresh(order)
	db.close()

	return order

@app.get("/incoming-orders")
def get_incoming_orders(current_user: dict = Depends(get_current_user)):
	db = SessionLocal()

	if current_user["role"] != "bakery_owner":
		raise HTTPException(status_code = 403)

	orders = db.query(Order).join(Bakery).filter(Bakery.owner_id == current_user["user_id"]).all()

	db.close()

	return orders

@app.post("/bakery")
def create_bakery(bakery: BakeryCreate, current_user: dict = Depends(get_current_user)):
	db = SessionLocal()

	if current_user["role"] != "bakery_owner":
		db.close()
		raise HTTPException(status_code = 403)

	new_bakery = Bakery(name = bakery.name, description= bakery.description,
		 location = bakery.location, owner_id=current_user["user_id"])

	db.add(new_bakery)
	db.commit()
	db.refresh(new_bakery)
	db.close()	
	
	return new_bakery
	
	
	
