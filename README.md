# FashionHub

A Django e-commerce app. Users can browse products, add them to a cart, place orders, and pay through the eSewa sandbox.

## Features

- User registration, login, and password reset
- Product catalog with reviews
- Shopping cart
- Checkout and order placement
- Order history
- eSewa sandbox payment integration
- Django admin for managing products and orders

## Tech Stack

Python, Django, HTML templates, eSewa ePay (sandbox)

## Project Structure

```
fashionhub/   project settings and root URLs
accounts/     registration, login, password reset
base/         shared base model (UUID primary keys)
home/         landing pages
products/     products and reviews
cart/         shopping cart
orders/       orders, checkout, payment
templates/    shared templates
```

## Run Locally

```bash
git clone https://github.com/Sujana-deve/Shopiing-app.git
cd Shopiing-app

python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. Log in at `/admin/` and add some products first, since the store starts empty.

## Notes

- Payments run in eSewa sandbox mode only. No real money moves.
- Not deployed. Runs locally.

---

Built by [Sujana Sharma](https://github.com/Sujana-deve).
