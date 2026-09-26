# BRAND NEW STORE 0.2 — Django Storefront

Responsive Bengali clothing-store starter with PostgreSQL-ready Django backend, product/category management, product gallery uploads, session cart, guest checkout, order records, stock decrement, order status management, store settings, and built-in Django staff admin.

## Run locally (free)
1. Install Python 3.11+ and PostgreSQL (or use SQLite for local trial).
2. Create a virtual environment and install:
   ```bash
   python -m venv .venv
   # Windows: .venv\\Scripts\\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`, set a long random `DJANGO_SECRET_KEY`. For PostgreSQL set `DATABASE_URL`.
4. Initialize and create the first administrator:
   ```bash
   python manage.py makemigrations store
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
5. Store: http://127.0.0.1:8000/ — Admin: http://127.0.0.1:8000/admin/

## Admin usage
Use the Django admin account for staff-only management. Add categories, products, multiple product images, and one StoreSettings row. Configure logo, store contact, WhatsApp, social links, delivery charges, payment numbers and hero image there. Customers do not need accounts and cannot access `/admin/` without staff credentials.

## Production
- Use managed PostgreSQL and a host that supports Django, persistent media storage, environment variables and HTTPS.
- Set `DJANGO_DEBUG=False`, a strong `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` to your domain, and production `DATABASE_URL`.
- Run `python manage.py migrate` and `python manage.py collectstatic --noinput`; serve with `gunicorn config.wsgi:application`.
- Set up backups, monitoring, email/SMS provider credentials, and persistent media storage. Do not commit `.env`.
- HTTPS security flags are enabled when DEBUG is False.

## Important limitations / before taking live orders
- This is a working foundation, not a fully audited payment/SMS integration. bKash/Nagad are currently recorded as selected payment methods; automated payment verification is not implemented. SMS variables are reserved but a provider-specific API adapter and tested credentials are required. Do not advertise SMS alerts as active until configured and tested.
- Delivery charge currently uses Dhaka as the inside area and other districts as outside; add your exact inside/outside area rule in settings/code before launch.
- Logo asset was not present in the request attachment. Upload the original logo in Store Settings; the site displays it without modifying the image.
- For reliable production ordering, configure PostgreSQL and verify stock/concurrency, backups, privacy notice, terms, and Bangladesh payment-provider requirements before launch.
