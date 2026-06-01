from .database import engine
from . import models
from .database import SessionLocal
from .schemas import UserCreate, OrderCreate, UserLogin, OrderStatusUpdate, BakeryCreate, MenuItemCreate
from .models import User, Order, Bakery, MenuItem
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import requests
from sqlalchemy.orm import Session

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

models.Base.metadata.create_all(bind=engine)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

def create_access_token(data: dict):
	to_encode = data.copy()

	expire = datetime.now(timezone.utc) + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode.update({"exp": expire})
	
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

	return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		user_email = payload.get("sub")
		user_id = payload.get("user_id")
		user_role = payload.get("role")		

		#if user_email is None:
		#	raise HTTPException(status_code=401, detail="Invalid token") # already covered by pydantic BaseModel validation

		return {"email": user_email, "user_id":user_id, "role": user_role}

	except:
		raise HTTPException(status_code=401, detail="Invalid token")


def required_role(required_role: str):
	def role_checker(current_user: dict = Depends(get_current_user)):
		if current_user["role"] != required_role:
			raise HTTPException(status_code=403, detail="You do not have permission.")
		return current_user
	return role_checker

@app.get("/me")
def read_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

	user = db.query(User).filter(User.id == current_user["user_id"]).first()

	return {"id":user.id, "username":user.username, "email":user.email}

@app.get("/")
def home():
	return {"message": "backend running"}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
	existing_user = db.query(User).filter(User.email == user.email).first()
	if existing_user:
		db.close()
		raise HTTPException(status_code=400, detail="Email already registered")
	
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
def get_users(db: Session = Depends(get_db)):
	users = db.query(User).all()
	return users

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):

	user = db.query(User).filter(User.id == user_id).first()

	if not user:
		raise HTTPException(status_code=404, detail="User not found")

	return user

@app.delete("/users/{user_id}")
def delete_user(user_id : int, db: Session = Depends(get_db)):

	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	
	db.delete(user)
	db.commit()

	return {"message": "user deleted"}

@app.put("/users/{user_id}")
def update_user(user_id: int, updated_user: UserCreate):
	db = SessionLocal()

	user = db.query(User).filter(User.id == user_id).first()

	if not user:
		raise HTTPException(status_code=404, detail="User not found")

	user.username = updated_user.username
	user.email = updated_user.email
	
	db.commit()
	db.refresh(user)
	return user


@app.post("/orders")
def create_order(order: OrderCreate, current_user: dict = Depends(required_role("customer")), db: Session = Depends(get_db)):
	
	bakery = db.query(Bakery).filter(Bakery.id == order.bakery_id).first()
	
	if order.quantity < 1 :
		raise HTTPException(status_code=400, detail="Quantity must be at least 1")

	if not bakery:
		raise HTTPException(status_code=404, detail="Bakery not found")	
	
	menu_item = db.query(MenuItem).filter(MenuItem.id==order.menu_item_id, MenuItem.bakery_id==order.bakery_id).first()

	if not menu_item:
		raise HTTPException(status_code = 404, detail = "Menu item not found")

	new_order = Order(menu_item_id=menu_item.id, user_id=current_user["user_id"], bakery_id = order.bakery_id, quantity=order.quantity, price_at_order = menu_item.price)
	
	db.add(new_order)
	db.commit()
	db.refresh(new_order)
	return new_order

@app.get("/bakeries/{bakery_id}/manage-menu")
def get_menu_items(bakery_id: int, current_user: dict = Depends(required_role("bakery_owner")), db: Session = Depends(get_db)):
	bakery = db.query(Bakery).filter(Bakery.id == bakery_id).first()
	if not bakery:
		raise HTTPException(status_code=404, detail="Bakery not found")
	if bakery.owner_id != current_user["user_id"]:
		raise HTTPException(status_code=403, detail="Not your bakery")
	
	items = db.query(MenuItem).filter(MenuItem.bakery_id == bakery_id).all()

	return items

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
	user = db.query(User).filter(User.email == form_data.username).first()
	
	if not user:
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	password_ok = pwd_context.verify(form_data.password, user.hashed_password)
	
	if not password_ok:
		raise HTTPException(status_code=401, detail="Invalid email or password")
	
	access_token = create_access_token(data={"sub": user.email, "user_id": user.id, "role": user.role.value})	

	return {
		"access_token":access_token,
		"token_type": "bearer",
		"role": user.role
	}


@app.get("/my-orders")
def get_my_orders(current_user: dict = Depends(required_role("customer")), db: Session = Depends(get_db)):
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
				"total_price": order.price_at_order * order.quantity
				})	
	return result

@app.get("/bakeries")
def get_all_bakeries(db: Session = Depends(get_db)):
	bakeries = db.query(Bakery).all()
	return bakeries

@app.get("/bakeries-of-{user_id}")
def get_bakeries(user_id : int, db: Session = Depends(get_db)):
	bakeries = db.query(Bakery).filter(Bakery.owner_id == user_id).all()
	return bakeries

@app.post("/manage-menu")
def add_menu_item(menuitem: MenuItemCreate, current_user: dict = Depends(required_role("bakery_owner")), db: Session = Depends(get_db)):

	user_bakeries = get_bakeries(current_user["user_id"], db)
	if menuitem.bakery_id not in [b.id for b in user_bakeries]:
		raise HTTPException(status_code=403, detail="Not your bakery")

	new_menuitem = MenuItem(bakery_id=menuitem.bakery_id, name=menuitem.name, description = menuitem.description, price=menuitem.price)

	db.add(new_menuitem)
	db.commit()
	db.refresh(new_menuitem)
	
	return new_menuitem

@app.delete("/manage-menu")
def delete_menu_item(menu_item_id: int, current_user: dict = Depends(required_role("bakery_owner")), db: Session = Depends(get_db)):

	menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()

	if not menu_item:
		raise HTTPException(status_code=404, detail="Menu item not found")

	if menu_item.bakery.owner_id != current_user["user_id"]:
		raise HTTPException(status_code=403, detail="Not your bakery")

	db.delete(menu_item)
	db.commit()

	return {"message": "Menu item deleted"}

@app.patch("/manage-menu")
def update_menu_item(menu_item_id: int, updated_item: MenuItemCreate, current_user: dict = Depends(required_role("bakery_owner")), db: Session = Depends(get_db)):

	menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()

	if not menu_item:
		raise HTTPException(status_code=404, detail="Menu item not found")

	if menu_item.bakery.owner_id != current_user["user_id"]:
		raise HTTPException(status_code=403, detail="Not your bakery")
	
	if updated_item.price < 1:
		raise HTTPException(status_code=400, detail="Price must be at least 1")

	menu_item.name = updated_item.name
	menu_item.description = updated_item.description
	menu_item.price = updated_item.price

	db.commit()
	db.refresh(menu_item)

	return menu_item


@app.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status_update: OrderStatusUpdate, current_user: dict= Depends(required_role("bakery_owner")), db: Session = Depends(get_db)):
	
	order = db.query(Order).filter(Order.id == order_id).first()

	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	if order.bakery.owner_id != current_user["user_id"]: # I would like to note that this is not a good design principle (against one dot rule)
		raise HTTPException(status_code=403, detail="Not your order")

	order.status = status_update.status
	
	db.commit()
	db.refresh(order)

	return order

@app.get("/incoming-orders")
def get_incoming_orders(current_user: dict = Depends(required_role("bakery_owner")), db: Session = Depends(get_db)):
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

	return result

@app.post("/bakery")
def create_bakery(bakery: BakeryCreate, current_user: dict = Depends(required_role("bakery_owner")), db: Session = Depends(get_db)):
	new_bakery = Bakery(name = bakery.name, description= bakery.description,
		 location = bakery.location, owner_id=current_user["user_id"])

	db.add(new_bakery)
	db.commit()
	db.refresh(new_bakery)
	
	return new_bakery

@app.get("/external/weather")
def get_weather(lat: float, lon: float):
    if not WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key is not configured")
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        )

        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=data
            )

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "weather": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Weather API request failed: {str(e)}"
        )

# Currency rates endpoint
@app.get("/external/currency")
def get_currency_rate():
    try:
        url = "https://api.frankfurter.app/latest?from=EUR&to=USD,TRY"
        response = requests.get(url, timeout=10)
        data = response.json()

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=data
            )

        return {
            "base": data["base"],
            "date": data["date"],
            "usd": data["rates"]["USD"],
            "try": data["rates"]["TRY"]
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Currency API request failed: {str(e)}"
        )