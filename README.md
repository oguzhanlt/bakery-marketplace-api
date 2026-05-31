# 🥐 Bakery Marketplace API

A full-stack marketplace platform where customers can browse 
and order from local bakeries — and bakery owners can manage 
their incoming orders in real time.

Built with FastAPI (Python) on the backend and React on the 
frontend. Designed with role-based access so customers and 
bakery owners each have their own experience.

## Tech Stack
- **Backend:** Python · FastAPI · SQLAlchemy · PostgreSQL
- **Frontend:** React · JavaScript · CSS
- **Auth:** JWT Authentication · Role-Based Access Control (RBAC)
- **Tools:** Git · Passlib / bcrypt
- 
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

### Class Diagram

<div align="center">
  <img width="750" alt="Class Diagram" src="https://github.com/user-attachments/assets/965d5fc7-a922-4361-b31e-ea7557493c14" />
</div>

