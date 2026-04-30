# Bakery Marketplace API

Backend API for a bakery marketplace platform where customers can place orders and bakery owners can manage incoming requests.

## Features

- User registration & login
- JWT authentication
- Role-based access control (RBAC)
- Customer & bakery owner accounts
- Order creation
- Incoming orders for bakery owners
- Order status workflow
- PostgreSQL database
- SQLAlchemy ORM
- Protected routes

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- Passlib / bcrypt

## Roles

### Customer
- Register/login
- Create orders
- View own orders
- Track order status

### Bakery Owner
- Register/login
- View incoming orders
- Update order status
- Manage bakery workflow

## Order Status Flow

```text
pending → accepted → preparing → ready → completed
