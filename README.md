# 🛒 ShopEasy — Full Stack E-Commerce Platform

A production-ready e-commerce web application built with Django, designed to simulate real-world online shopping platforms like Flipkart and Amazon.

It supports complete user flows including authentication, product browsing, cart management, checkout, payments, and order handling.

---

## 🚀 Features

### 🔐 Authentication System

* User registration & login
* Secure logout handling
* Password reset via email (token-based)
* Session handling & protected routes

---

### 🛍️ Product System

* Product listing with images, pricing & discounts
* “New Arrivals” based dynamic homepage
* Seller fallback display ("ShopEasy" if missing)
* Product detail pages

---

### 🛒 Cart System

* Add/remove products
* Quantity increment/decrement (AJAX-based)
* Real-time subtotal updates
* Persistent cart per user

---

### 📦 Checkout Flow (Accordion Based)

* Step 1: Login / Signup (if not authenticated)
* Step 2: Address selection
* Step 3: Order summary (dynamic updates)
* Step 4: Payment selection

---

### 🏠 Address Management

* Add / Edit / Delete address (modal-based UI)
* Set default address
* Horizontal scrollable address cards
* Live selection preview

---

### 💳 Payment Integration

* Cash on Delivery (COD)
* Razorpay integration for online payments
* Dynamic total calculation before payment
* Secure backend verification

---

### 📑 Order Management

* Order creation & tracking
* Order details page
* Price breakdown (MRP, discount, total)
* Cancel selected items functionality

---

### 👤 Profile System

* Editable user profile (inline Edit → Save toggle)
* Gender, name, phone management
* Email display (linked to auth system)

---

### 🎨 UI / UX

* Flipkart-inspired layout
* Responsive design
* Clean card-based UI
* Flash messages (success/error/warning)
* Navbar with dropdown user menu
* Modal-driven interactions
* Smooth accordion transitions

---

## 🛠️ Tech Stack

### Backend
* Python
* Django
* Django Authentication System
* Django Messages Framework

### Frontend

* HTML5
* Tailwind CSS
* Vanilla JavaScript

### Database

* SQLite (dev) → PostgreSQL (production ready)

### Payments

* Razorpay API

### Deployment Ready Features

* CSRF Protection
* Secure password reset tokens (time-limited)
* Session-based authentication
* Environment-based configs (recommended)

---

## 📁 Project Structure

```
project/
│
├── accounts/        # Authentication & user management
├── products/        # Product & listing logic
├── orders/          # Cart, checkout, orders
├── contacts/        # User relationships (phonebook logic)
├── templates/       # HTML templates
├── static/          # CSS, JS, assets
└── config/          # Settings, ASGI, routing
```

---

## ⚡ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/souryaghosh23/ShopEasy.git
cd ShopEasy
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```
SECRET_KEY=your_secret_key
DEBUG=True

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_app_password

RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
```

---

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Run Server

```bash
python manage.py runserver
```


---

## 📸 Screenshots (Recommended)

* Homepage
* Checkout Flow
* Chat Dashboard

---

## ⚠️ Known Limitations

* Seller marketplace system is partially implemented
* Homepage recommendation system is basic (new arrivals only)

---

## 🚀 Future Improvements

* Full seller marketplace system
* AI-based product recommendations
* Advanced chat features (read receipts, typing indicators)
* RAG-based intelligent assistant integration
* Improved homepage personalization

---

## 🧑‍💻 Author

Sourya
Backend-focused developer building real-world systems with Django, WebSockets, and AI-driven architectures.

---

## 📜 License

This project is for educational and portfolio purposes.
