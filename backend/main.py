from fastapi import FastAPI
from .database import engine, Base
from . import models
from .database import SessionLocal
from .schemas import UserCreate, OrderCreate, UserLogin, OrderStatusUpdate, BakeryCreate, MenuItemCreate
from .models import User, Order, Bakery, MenuItem
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
	
	bakery = db.query(Bakery).filter(Bakery.id == order.bakery_id).first()
	
	if order.quantity < 1 :
		db.close()
		raise HTTPException(status_code=403)

	if not bakery:
		db.close()
		raise HTTPException(status_code=404, detail="Bakery not found")	
	
	menu_item = db.query(MenuItem).filter(MenuItem.id==order.menu_item_id, MenuItem.bakery_id==order.bakery_id).first()

	if not menu_item:
		db.close()
		raise HTTPException(status_code = 404, detail = "Menu item not found")

	new_order = Order(menu_item_id=menu_item.id, user_id=current_user["user_id"], bakery_id = order.bakery_id, quantity=order.quantity, price_at_order = menu_item.price)
	
	db.add(new_order)
	db.commit()
	db.refresh(new_order)
	db.close()
	return new_order

@app.get("/bakeries/{bakery_id}/menu-items")
def get_menu_items(bakery_id: int):
	db = SessionLocal()
	
	items = db.query(MenuItem).filter(MenuItem.bakery_id == bakery_id).all()

	db.close()
	return items

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
		db.close()
		raise HTTPException(status_code=403)

	orders = db.query(Order).filter(Order.user_id == current_user["user_id"]).all()
	
	result = []

	for order in orders:
        	result.append({
            	"order_id": order.id,
		"bakery": order.bakery.name,
		"menu_item": order.menu_item.name,
            	"quantity": order.quantity,
            	"status": order.status,
            	"created_at": order.created_at,
		"price_at_order": order.price_at_order,
		"total_price": order.price_at_order * order.quantity})	

	db.close()

	return result

def get_bakeries(user_id : int):
	db = SessionLocal()

	bakeries = db.query(Bakery).filter(Bakery.owner_id == user_id).all()
	db.close()
	return bakeries

@app.post("/menu-items")
def create_menu_item(menuitem: MenuItemCreate, current_user: dict = Depends(get_current_user)):
	db = SessionLocal()
	
	if current_user["role"]!= "bakery_owner":
		db.close()
		raise HTTPException(status_code=403)

	user_bakeries = get_bakeries(current_user["user_id"])
	if menuitem.bakery_id not in [b.id for b in user_bakeries]:
		db.close()
		raise HTTPException(status_code=403, detail="Not your bakery")

	new_menuitem = MenuItem(bakery_id=menuitem.bakery_id, name=menuitem.name, description = menuitem.description, price=menuitem.price)

	db.add(new_menuitem)
	db.commit()
	db.refresh(new_menuitem)
	db.close()
	
	return new_menuitem


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
		db.close()
		raise HTTPException(status_code = 403)

	orders = db.query(Order).join(Bakery).filter(Bakery.owner_id == current_user["user_id"]).all()
	
	result = []

	for order in orders:
		result.append({
		"order_id":order.id,
		"customer":order.customer.username,
		"bakery":order.bakery.name,
		"menu_item":order.menu_item.name,
		"quantity":order.quantity,
		"status":order.status,
		"created_at":order.created_at,
		"price_at_order":order.price_at_order,
		"total_price":order.price_at_order * order.quantity})

	db.close()

	return result

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
	
	
	
