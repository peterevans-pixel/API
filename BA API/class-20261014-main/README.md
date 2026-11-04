# DATA 4000 — Python + Supabase API Lab
Fairfield University · Illya Mowerman, Ph.D.

## Start here
Build a fictional campus store database, upload CSV records with Python, and use
an API to read and change records. Plan for 75–90 minutes with accounts created
before class. Python fundamentals (functions, lists, dictionaries, imports) are assumed.
Use Python 3.11 or newer and VS Code. No actual customer data is used.

## What is happening?
Python reads CSV text into dictionaries. The Supabase Python library sends those
dictionaries as JSON over HTTPS to Supabase's Data API. The API reads/writes
PostgreSQL tables and sends JSON back. `.execute()` triggers a request; `.data`
contains the returned Python records. This lab does NOT use a PostgreSQL connection
string, database password, or Django ORM.

CSV → Python → HTTPS Data API → Supabase PostgreSQL.
Later: Streamlit widget or Django view → the same Python functions → Data API.

## Files and order
| File | Purpose |
|---|---|
| data/customers.csv | 20 fictional customers |
| data/products.csv | 12 products |
| data/orders.csv | 60 one-product orders |
| sql/01_create_tables.sql | Tables, constraints, and restricted access |
| config.py | Read local configuration |
| database.py | Reusable API functions |
| 01_check_connection.py | Check access before uploading |
| 02_import_data.py | Validate and upload CSV records |
| 03_query_data.py | Read, filter, join, calculate revenue |
| 04_modify_data.py | Insert, update, delete demonstration |
| 05_raw_api.py | Optional HTTP request without the client library |
| app_streamlit.py | Optional local application bridge |
| exercises.py / solutions.py | Student practice and worked answers |
| EXPECTED_RESULTS.md | Baseline results for verification |
| INSTRUCTOR_GUIDE.md | Lesson flow and discussion prompts |

## 1. Create your own Supabase project
Create a dedicated classroom project at https://supabase.com/dashboard and wait
for it to finish provisioning. Each student should use their own project. Do not
share the instructor's administrative credentials with students.
Open SQL Editor, paste sql/01_create_tables.sql, and run it once.
The script creates public.customers, public.products, and public.orders.
Check Table Editor: all three tables should exist and initially be empty.
If you already have tables with these names, use a new project; this script does
not overwrite them. SQL defines the structure; the later Python script loads data.
Ensure the Data API is enabled and the public schema is exposed in project API settings.

## 2. Open the extracted folder in VS Code
Open the whole supabase_class folder, then open its terminal.
Create a virtual environment:

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```
Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place
of `python` for installation and scripts; activation is not essential.
In VS Code use Python: Select Interpreter and choose the .venv interpreter.
Dependencies use compatible major-version ranges, not a fully locked environment.

## 3. Set configuration
In Supabase, find your project URL in the Connect dialog and a secret API key in
Settings → API Keys. Create a secret key if needed. Edit the local .env file:
```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=sb_secret_your_actual_key
```
Use the project API URL, not the browser dashboard address. The secret key is not
the database password. This kit expects the current sb_secret_ key format.

This is a private, local administrative exercise: each person uses their own
secret key. Row Level Security is enabled, with no public access policies, and
anon/authenticated table privileges are revoked. The secret key uses service_role,
which bypasses RLS. A publishable key therefore cannot substitute for this key.
Never put .env in GitHub, slides, screenshots, AI prompts, or student submissions.
The included .gitignore excludes it. If exposed, rotate the key in Supabase.

## 4. Validate, connect, and upload
```bash
python 02_import_data.py --check-only
python 01_check_connection.py
python 02_import_data.py
python 01_check_connection.py
```
The offline check does not need packages or credentials. Expect 20 customers,
12 products, and 60 orders. The connection check reports 0 products before import
and 12 afterward. Refresh Table Editor to see the records.
The loader converts CSV strings to integers where required and validates keys,
quantities, dates, and prices before calling the API. Prices are sent as decimal
strings and stored as PostgreSQL numeric values.

Customers and products must load before orders because orders contain foreign keys.
The loader uses upsert: an existing primary key is updated, otherwise inserted.
Re-running restores the seeded values, including catalog prices. It does not remove
extra records created during exercises. Uploads are three separate requests, not
one all-or-nothing transaction. If a request fails, fix the issue and rerun.

## 5. Query and modify
```bash
python 03_query_data.py
python 04_modify_data.py
python 05_raw_api.py
```
Read database.py beside each example. The modify script requires typing YES,
adds one fictional demo customer, changes a product price, creates/deletes one
order, and restores the product price in a finally block. An abrupt process stop
can leave partial changes: inspect the tables and rerun the importer to restore
seed prices. Additional demo customers are intentionally retained.
Use an equality filter for every targeted update/delete. A foreign key prevents
an order from referring to a nonexistent customer or product.

The raw HTTP example returns status 200 and a JSON list. Its apikey request header
identifies the calling component. The library normally handles HTTP details for us.

## 6. Practice
Read exercises.py, complete the TODOs, and run:
```bash
python exercises.py
```
Use solutions.py after attempting the exercises. Run baseline comparisons before
adding orders. See EXPECTED_RESULTS.md.

## 7. Optional Streamlit bridge
```bash
python -m pip install -r requirements-app.txt
python -m streamlit run app_streamlit.py --server.address 127.0.0.1
```
Open the local address printed in the terminal. The app shows the product catalog,
records purchases, and reads saved orders using database.py. Every successful
submission creates a new order. This is an unauthenticated LOCAL admin demo;
do not publish it as-is. Server-held credentials do not by themselves authorize
visitors to change data. Before public deployment add user authentication and
per-user authorization, with appropriately scoped RLS policies and user sessions,
or a carefully authorized backend. Store deployment secrets in the hosting
platform's secret manager.

For Django, a view can import `get_products` or `create_order` from database.py.
A POST form needs Django CSRF protection, input validation, authentication, and
authorization before calling write functions. Using this API approach is different
from configuring Django's PostgreSQL ORM. A full Django project is a later lesson.

## 8. Order entry assignment
With the tables created and customers/products loaded, run the interactive order
program from this project directory:
```bash
python order_entry.py
```
The script loads customers and products from Supabase, validates the selected IDs
and quantity, and shows an order summary before asking for Y/N confirmation.
Confirming inserts the order through `database.py`; Supabase generates the order
ID and the program makes a separate query to retrieve and display the saved row.
Declining does not insert an order. The displayed total uses the saved unit price.

For a fresh setup, copy `.env.example` to `.env` and enter your own project URL
and secret API key in `.env`. Never submit `.env`; `.gitignore` excludes it.

Testing results: syntax and mocked-input checks passed for valid input, invalid
input retries, confirmation, cancellation, successful save, and verification
failure. These tests do not contact Supabase; run the program with your own
configured project to verify the live database connection.

## Data dictionary and design
| Table | Column | Type / meaning |
|---|---|---|
| customers | customer_id | Integer primary key |
| customers | name, email, city | Text; email is unique |
| products | product_id | Integer primary key |
| products | product_name, category | Text |
| products | price | Current catalog price, dollars, 2 decimals |
| orders | order_id | Integer primary key |
| orders | customer_id, product_id | Foreign keys to the parent tables |
| orders | quantity | Positive integer |
| orders | order_date | ISO date YYYY-MM-DD |
| orders | unit_price | Price per unit at purchase time |

One customer can have many orders; one product can appear in many orders.
Each order contains ONE product, possibly multiple units. A full shopping cart
would usually separate orders from order_items, adding a fourth table.
Seed IDs are below 1000; generated IDs start at 1000 to avoid sequence collisions
when new rows are inserted. All names are fictional and emails use example.com.
The data is fixed, reproducible, and dated September 2026.

## Scope of the teaching example
The read functions use one API response. Supabase commonly limits responses to
1000 records; use pagination for larger datasets. Revenue is labeled as the total
of returned rows. Recording an order reads a product price and then inserts the
order in separate requests. A production checkout should enforce authoritative
pricing, inventory, and atomicity in a database function/transaction. This lesson
has no payments, inventory, taxes, shipping, or production checkout guarantees.

## Troubleshooting
| Symptom | What to check |
|---|---|
| ModuleNotFoundError | Install requirements with the same Python interpreter running the script. |
| Configuration ValueError | .env must sit beside config.py; replace both placeholders. Existing shell environment variables take precedence. |
| HTTP 401 / invalid API key | URL and secret key must belong to the same project; check key status. |
| Permission denied / empty public reads | Use your own secret key for this lab; public access is intentionally restricted. |
| Table not found / schema cache | Run SQL first, confirm public schema is exposed, then retry after the schema cache refreshes. |
| Foreign-key error | Upload parents first; customer/product IDs must exist. |
| Unique email error | Choose a new fictional email or inspect the existing customer. |
| Relation already exists | Setup SQL was already run; skip it or use a new project. |
| Counts exceed baseline | Demo customers or app orders remain; seed upsert does not delete them. |
| Network / project unavailable | Check internet access and that the Supabase project is running. |

## Reference documentation
API syntax and key guidance checked October 14, 2026:
- https://supabase.com/docs/reference/python/initializing
- https://supabase.com/docs/reference/python/select
- https://supabase.com/docs/reference/python/insert
- https://supabase.com/docs/reference/python/upsert
- https://supabase.com/docs/guides/getting-started/api-keys

Validation: CSV relationships and totals and Python syntax checked locally.
A live Supabase round-trip requires your project and credentials and was not run
when this kit was created. Run the connection/import checks before class.
