# Django E-commerce Backend

## Description
This is a **backend system for an E-commerce platform** built with **Django** and **Django REST Framework**.  
It supports **products, orders, users**, and **Stripe payments**. This project focuses only on the backend and can be connected to any frontend via APIs.

---

## Features
- User signup, login, and authentication  
- CRUD operations for products  
- Place and manage orders  
- Secure payment processing using **Stripe**  

---

## Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Run server
python manage.py runserver
