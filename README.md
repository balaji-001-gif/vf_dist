# 🌿 FreshRoute

**Farm-to-Customer Distribution Platform**
*Built on Frappe & ERPNext v15*

FreshRoute is a purpose-built ERPNext v15 custom application that digitises the end-to-end supply chain of a fresh produce distributor. It manages workflows from field procurement by agents, through cold-storage management, to last-mile delivery for Swiggy, Zomato, supermarkets, and B2B customers.

## 🚀 Key Features

### 👨‍🌾 Farmer Management & Procurement
- **Farmer Profiles & KYC**: Digital onboarding with land details, KYC verification, and bank accounts.
- **Farmer Procurement Entry**: Direct field agent portal to log fresh produce purchases.
- **Quality Check (QC)**: Dedicated QC workflows allowing pass, partial-reject, and full-reject parameters to ensure grade compliance.
- **Farmer Portal**: Specific online portal to view past procurements, pending payment dues, and real-time mandi prices.
- **Farmer Ledger**: Streamlined auto-generation of ERPNext Purchase Invoices and custom Farmer Payments docs for precise tracking.

### ❄️ Cold Storage & Warehousing
- **Cold Storage Location Masters**: Mapped natively to ERPNext warehouses for seamless tracking.
- **Inward/Outward Logs**: Automated Material Receipts and Issue matching stock entries directly from procurement acceptances and dispatch workflows.
- **Temperature / IoT Alerts**: Daily scheduled hooks to maintain optimal temperatures and alert constraints (via notifications/reports).

### 🚚 Customer Portal & Dispatches
- **B2B Web Portal**: Customers directly place orders, browse produce, track dispatch, and download GST invoices.
- **Dispatch Order Processing**: Connects `Vehicle Master`, `Delivery Route`, and `Sales Orders` to optimise load and travel time.
- **Automated Bookkeeping**: Completing a Dispatch automatically posts the corresponding ERPNext Delivery Note and Sales Invoices.

## 🛠️ Technology Setup

- **Backend / Core**: Frappe Framework & ERPNext (v15)
- **Database**: MariaDB
- **Languages**: Python 3.11+, JavaScript, Jinja
- **Integrations**: Twilio/WhatsApp notification hooks, RQ Background Jobs

## 📦 Core DocTypes

| Category | DocTypes |
| --- | --- |
| **Master Data** | `Farmer`, `Delivery Route`, `Vehicle Master`, `Cold Storage Location` |
| **Transactions** | `Farmer Procurement`, `Quality Check`, `Dispatch Order`, `Farmer Payment` |
| **Stock Tracking** | `Cold Storage Inward`, `Cold Storage Outward` |

## ⚙️ Installation Guide

Follow standard Frappe bench commands to pull and install FreshRoute:

```bash
# 1. Fetch the application into your bench
bench get-app freshroute https://github.com/your-username/freshroute.git

# 2. Install it onto your site
bench --site [your-site-name] install-app freshroute

# 3. Migrate and build to apply custom fields & schemas
bench --site [your-site-name] migrate
bench build --app freshroute
```

*Ensure ERPNext v15 is correctly installed and configured prior to execution.*

## 📈 Reports & Analytics
A comprehensive array of out-of-the-box reports:
- **Operations**: Daily Procurement Summary, Cold Storage Stock Report, Dispatch Report.
- **Financial**: Farmer Ledger, Customer Sales Report, Payment Reconciliation.
- **Management**: Produce Wastage, Mandi vs Purchase Price Variance.

---
*For support or integration questions, please open an issue in the repository.*
