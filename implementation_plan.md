# 🌿 FreshRoute — ERPNext v15 Implementation Plan
**Farm-to-Customer Distribution Platform**

> **Custom App:** `freshroute` | **Framework:** Frappe v15 | **ERP:** ERPNext v15
> **Version:** 1.0 | **Date:** April 2026 | *For Vegetable & Fruit Distributor*

---

## Table of Contents

1. [Executive Summary & Business Overview](#1-executive-summary--business-overview)
2. [System Architecture & Technology Stack](#2-system-architecture--technology-stack)
3. [Custom App Structure (freshroute)](#3-custom-app-structure--freshroute)
4. [DocType Design — Master Data](#4-doctype-design--master-data)
5. [DocType Design — Transactions](#5-doctype-design--transactions)
6. [DocType Design — Cold Storage & Inventory](#6-doctype-design--cold-storage--inventory)
7. [DocType Design — Payments & Ledger](#7-doctype-design--payments--ledger)
8. [Farmer Portal — Features & Implementation](#8-farmer-portal--features--implementation)
9. [Customer Portal — Features & Implementation](#9-customer-portal--features--implementation)
10. [Reports & Dashboards](#10-reports--dashboards)
11. [Workflows & Automation](#11-workflows--automation)
12. [ERPNext v15 Native Module Integrations](#12-erpnext-v15-native-module-integrations)
13. [Phased Implementation Roadmap](#13-phased-implementation-roadmap)
14. [Key Files Reference Guide](#14-key-files-reference-guide)
15. [Testing, Deployment & Go-Live Checklist](#15-testing-deployment--go-live-checklist)

---

## 1. Executive Summary & Business Overview

FreshRoute is a purpose-built ERPNext v15 custom application that digitises the end-to-end supply chain of a fresh produce distributor — from field procurement by agents, through cold-storage management, to last-mile delivery for Swiggy, Zomato, supermarkets, and other customers.

The system is layered on top of the Frappe framework so that all standard ERPNext modules (Accounts, Stock, HR, Buying, Selling) continue to function natively while domain-specific logic is added through a dedicated custom app named **freshroute**.

### Key Business Actors

| Actor | Role | Primary Portal / Module |
|---|---|---|
| **Farmer** | Supplies produce; receives payment after quality check | Farmer Portal (Web) |
| **Field Agent** | Buys from farmer, records quality, dispatches to cold storage | Mobile App / ERPNext |
| **Cold Storage Manager** | Manages inbound/outbound stock, temperature logs | ERPNext Stock Module |
| **Operations Manager** | Plans daily dispatch, routes, vehicle assignment | ERPNext + Custom DocTypes |
| **Customer** (Swiggy / Zomato / Supermarket) | Places orders, tracks delivery, views invoices | Customer Portal (Web) |
| **Accounts Team** | Reconciles payments, farmer dues, GST filing | ERPNext Accounts |
| **Admin / Owner** | Full visibility dashboards & reports | ERPNext Dashboard |

### Business Flow Summary

```
Farmer → Field Agent (Procurement) → Quality Check → Cold Storage Inward
→ Stock Ledger → Customer Order → Dispatch Order → Delivery Note
→ Sales Invoice → Payment Entry
```

---

## 2. System Architecture & Technology Stack

### Technology Stack

| Layer | Technology | Version / Notes |
|---|---|---|
| Backend Framework | Frappe | v15 (Python 3.11+) |
| ERP Core | ERPNext | v15 (latest stable) |
| Custom App | freshroute | Built on Frappe |
| Database | MariaDB | 10.6+ |
| Cache / Queue | Redis | 6+ (background jobs via RQ) |
| Web Server | Nginx + Gunicorn | Production via bench |
| Farmer Portal | Frappe Web Forms + Jinja | Responsive HTML5 |
| Customer Portal | Frappe Web Forms + Jinja | Responsive HTML5 |
| Mobile (Agent) | ERPNext PWA / Frappe Go | Android / iOS |
| Notifications | Frappe Email + WhatsApp hook | Via Twilio / Gupshup |
| Reports | Frappe Query Report + Script Report | Custom + Standard |
| Deployment | bench (Frappe bench) | Docker optional |
| Version Control | Git + GitHub | CI via GitHub Actions |

### High-Level Data Flow

```
┌─────────────┐    Procurement     ┌─────────────────┐    QC Pass     ┌──────────────────┐
│   Farmer    │ ────────────────►  │  Farmer Proc.   │ ─────────────► │  Cold Storage    │
└─────────────┘                    └─────────────────┘                 │  Inward + Stock  │
                                                                        └────────┬─────────┘
                                                                                 │
┌─────────────┐    Sales Order     ┌─────────────────┐   Dispatch     ┌────────▼─────────┐
│  Customer   │ ────────────────►  │  Dispatch Order │ ─────────────► │  Cold Storage    │
└─────────────┘                    └─────────────────┘                 │  Outward + Stock │
       ▲                                    │                           └──────────────────┘
       │                                    │ Delivery Note
       │           Sales Invoice            ▼
       └──────────────────────────  Delivery + POD
```

---

## 3. Custom App Structure — `freshroute`

### Create the App

```bash
bench new-app freshroute
bench --site yoursite.com install-app freshroute
```

### Complete Folder Tree

```
freshroute/
├── freshroute/
│   ├── __init__.py
│   ├── hooks.py                          # App hooks (scheduler, portals, overrides)
│   ├── config/
│   │   ├── desktop.py                    # Module icons on ERPNext desk
│   │   └── docs.py
│   ├── public/
│   │   ├── js/                           # Client-side scripts per DocType
│   │   ├── css/                          # Portal custom styles
│   │   └── images/
│   ├── templates/
│   │   ├── pages/                        # Farmer & Customer portal HTML pages
│   │   └── emails/                       # Jinja email templates
│   └── freshroute/                       # Module folder
│       ├── doctype/
│       │   ├── farmer/
│       │   ├── farmer_procurement/
│       │   ├── quality_check/
│       │   ├── cold_storage_inward/
│       │   ├── cold_storage_outward/
│       │   ├── cold_storage_location/
│       │   ├── dispatch_order/
│       │   ├── vehicle_master/
│       │   ├── delivery_route/
│       │   ├── farmer_payment/
│       │   ├── customer_portal_settings/
│       │   └── freshroute_settings/
│       ├── report/
│       │   ├── farmer_ledger/
│       │   ├── daily_procurement_summary/
│       │   ├── cold_storage_stock_report/
│       │   ├── customer_sales_report/
│       │   ├── dispatch_report/
│       │   └── payment_reconciliation/
│       ├── page/
│       │   ├── freshroute_dashboard/
│       │   └── cold_storage_live/
│       └── workspace/
│           └── freshroute.json
├── api/
│   ├── farmer_portal.py                  # Whitelisted REST endpoints
│   ├── customer_portal.py
│   └── integrations.py
├── utils/
│   ├── notifications.py
│   ├── pricing.py
│   └── reports_helper.py
├── requirements.txt
└── setup.py
```

### hooks.py Key Sections

```python
app_name = "freshroute"
app_title = "FreshRoute"
app_publisher = "Your Company"
app_description = "Farm to Customer Distribution Platform"

# Scheduler Events
scheduler_events = {
    "daily": [
        "freshroute.utils.notifications.daily_procurement_alert",
        "freshroute.utils.notifications.expiry_check",
    ],
    "hourly": [
        "freshroute.utils.notifications.cold_storage_temp_check",
    ],
    "cron": {
        "0 6 * * *":  ["freshroute.utils.notifications.update_market_prices"],
        "0 7 * * *":  ["freshroute.utils.notifications.dispatch_reminder"],
        "0 0 * * 0":  ["freshroute.utils.notifications.farmer_payment_due_report"],
        "0 0 1 * *":  ["freshroute.utils.notifications.generate_gst_register"],
    }
}

# Website Route Rules
website_route_rules = [
    {"from_route": "/farmer-portal/<path:name>", "to_route": "farmer_portal"},
    {"from_route": "/customer-portal/<path:name>", "to_route": "customer_portal"},
]

# DocType Events
doc_events = {
    "Quality Check": {
        "on_submit": "freshroute.freshroute.doctype.quality_check.quality_check.on_submit"
    },
    "Farmer Procurement": {
        "on_submit": "freshroute.freshroute.doctype.farmer_procurement.farmer_procurement.on_submit"
    },
    "Dispatch Order": {
        "on_submit": "freshroute.freshroute.doctype.dispatch_order.dispatch_order.on_submit"
    }
}

# Fixtures (custom fields injected on install)
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "FreshRoute"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "FreshRoute"]]},
]
```

---

## 4. DocType Design — Master Data

### 4.1 Farmer (Master)

**Naming Series:** `FR-.YYYY.-.####`
**Module:** FreshRoute
**Is Submittable:** No

| Field Name | Type | Required | Description |
|---|---|---|---|
| `farmer_name` | Data | ✅ | Full name of the farmer |
| `farmer_code` | Data | Auto | Auto-generated unique ID (FR-0001) |
| `mobile_number` | Phone | ✅ | Primary mobile for OTP/WhatsApp |
| `alternate_mobile` | Phone | — | Secondary contact |
| `email_id` | Data | — | Portal login email |
| `portal_user` | Link → User | Auto | Created on Save for portal access |
| `aadhar_number` | Data | — | Masked after save |
| `pan_number` | Data | — | For TDS deduction |
| `bank_account_name` | Data | ✅ | For payment transfer |
| `bank_account_number` | Data | ✅ | Encrypted at rest |
| `ifsc_code` | Data | ✅ | Bank IFSC |
| `village` | Data | ✅ | Village / locality |
| `taluka` | Data | — | Taluka / block |
| `district` | Data | ✅ | District |
| `state` | Link → State | ✅ | State master |
| `pincode` | Data | — | 6-digit PIN |
| `gps_coordinates` | Geolocation | — | Farm location |
| `farm_size_acres` | Float | — | Total farm size |
| `primary_produce` | Table Multiselect → Item | — | Usual crops |
| `kyc_status` | Select | ✅ | Pending / Verified / Rejected |
| `kyc_documents` | Attach | — | Aadhaar / land record scan |
| `agent` | Link → Agent | — | Assigned field agent |
| `active` | Check | ✅ | Is farmer active |
| `total_outstanding` | Currency | Auto | Computed from Farmer Payment |
| `supplier` | Link → Supplier | Auto | Created on KYC verify |

**Controller Logic (`farmer.py`):**
```python
def after_insert(self):
    self.create_portal_user()   # Create frappe.User with role 'Farmer Portal'
    self.create_supplier()      # Create ERPNext Supplier for payment accounting

def validate(self):
    self.mask_aadhar()          # Show only last 4 digits
    self.validate_ifsc()        # Validate IFSC format
```

---

### 4.2 Item (Produce Master) — ERPNext Item + Custom Fields

Standard ERPNext Item DocType is used. Custom fields are injected via fixtures on app install.

| Custom Field | Type | Description |
|---|---|---|
| `produce_category` | Select | Vegetable / Fruit / Herb / Exotic |
| `perishability_days` | Int | Expected shelf life in days |
| `min_purchase_qty_kg` | Float | Minimum procurement per trip |
| `market_price_per_kg` | Currency | Today's mandi rate (auto-updated daily) |
| `grading_standards` | Small Text | A / B / C grade criteria |
| `cold_storage_temp_c` | Float | Ideal storage temperature (°C) |
| `is_seasonal` | Check | Mark if seasonal produce |
| `season_months` | Data | Comma-separated month numbers |

---

### 4.3 Vehicle Master

**Naming Series:** `VH-.####`

| Field | Type | Description |
|---|---|---|
| `vehicle_number` | Data | Registration plate (Primary Key) |
| `vehicle_type` | Select | Mini Truck / Tempo / Refrigerated Van / Bike |
| `capacity_kg` | Float | Max payload in kg |
| `refrigerated` | Check | Has cold chain capability |
| `driver_name` | Link → Employee | Assigned driver |
| `driver_mobile` | Phone | Quick contact |
| `gps_device_id` | Data | For live tracking integration |
| `insurance_expiry` | Date | Alert 30 days before expiry |
| `fitness_expiry` | Date | Alert 30 days before expiry |
| `status` | Select | Available / On Route / Maintenance |

---

### 4.4 Delivery Route (Master)

| Field | Type | Description |
|---|---|---|
| `route_name` | Data | E.g. "North Bangalore – Route A" |
| `stops_table` | Table → Route Stop | Ordered list of delivery stops |
| `estimated_km` | Float | Total route distance |
| `estimated_time_hrs` | Float | Expected travel time |
| `assigned_vehicle` | Link → Vehicle Master | Default vehicle |

---

## 5. DocType Design — Transactions

### 5.1 Farmer Procurement

**Naming Series:** `FP-.YYYY.-.#####`
**Is Submittable:** Yes

| Field | Type | Description |
|---|---|---|
| `procurement_id` | Data | Auto: FP-2026-00001 |
| `procurement_date` | Date | Date of purchase at farm |
| `farmer` | Link → Farmer | Source farmer |
| `agent` | Link → Agent | Buying agent |
| `vehicle` | Link → Vehicle Master | Transport vehicle |
| `items_table` | Table → Procurement Item | Child table |
| `total_weight_kg` | Float | Sum from items (read-only) |
| `total_amount` | Currency | Sum from items (read-only) |
| `payment_mode` | Select | Cash / Bank Transfer / Credit |
| `payment_status` | Select | Unpaid / Partial / Paid |
| `quality_check_status` | Select | Pending / Passed / Partial Reject |
| `linked_quality_check` | Link → Quality Check | Set after QC |
| `cold_storage` | Link → Cold Storage Location | Destination storage |
| `inward_entry` | Link → Cold Storage Inward | Set on accept |
| `purchase_invoice` | Link → Purchase Invoice | ERPNext PI auto-created |
| `remarks` | Small Text | Any notes |

**Child DocType: Procurement Item**

| Field | Type | Description |
|---|---|---|
| `item_code` | Link → Item | Produce item |
| `grade` | Select | A / B / C |
| `quantity_kg` | Float | Procured quantity |
| `rate_per_kg` | Currency | Negotiated rate |
| `amount` | Currency | Auto = qty × rate |
| `bags_crates` | Int | Physical packaging count |
| `market_rate_at_time` | Currency | Fetched from Item for reference |

---

### 5.2 Quality Check

**Naming Series:** `QC-.YYYY.-.#####`
**Is Submittable:** Yes

| Field | Type | Description |
|---|---|---|
| `qc_id` | Data | Auto: QC-2026-00001 |
| `procurement` | Link → Farmer Procurement | Source procurement |
| `qc_date` | Datetime | Inspection timestamp |
| `inspector` | Link → Employee | QC inspector |
| `items_table` | Table → QC Item | Per-item results |
| `overall_result` | Select | Pass / Partial Reject / Full Reject |
| `rejection_reason` | Small Text | If rejected |
| `photos` | Attach Multiple | Evidence images |
| `accepted_weight_kg` | Float | Net accepted weight |
| `rejected_weight_kg` | Float | Returned / discarded weight |

**On Submit Logic:**
- If **Pass / Partial** → create Cold Storage Inward → create Stock Entry → create Farmer Payment
- If **Full Reject** → cancel Farmer Procurement, notify farmer via WhatsApp

---

### 5.3 Dispatch Order

**Naming Series:** `DO-.YYYY.-.#####`
**Is Submittable:** Yes

| Field | Type | Description |
|---|---|---|
| `dispatch_id` | Data | Auto: DO-2026-00001 |
| `dispatch_date` | Date | Planned dispatch date |
| `customer` | Link → Customer | Delivery recipient |
| `customer_order` | Link → Sales Order | ERPNext SO linked |
| `vehicle` | Link → Vehicle Master | Delivery vehicle |
| `delivery_route` | Link → Delivery Route | Route master |
| `items_table` | Table → Dispatch Item | Products to dispatch |
| `total_weight_kg` | Float | Read-only sum |
| `cold_storage_outward` | Link → CS Outward | Stock out reference |
| `delivery_note` | Link → Delivery Note | Auto-created on submit |
| `status` | Select | Planned / Dispatched / Delivered / Failed |
| `actual_delivery_time` | Datetime | Captured by agent |
| `proof_of_delivery` | Attach | Customer signature / photo |
| `temperature_log` | Table → Temp Log | During transit readings |

---

## 6. DocType Design — Cold Storage & Inventory

### 6.1 Cold Storage Location (Master)

| Field | Type | Description |
|---|---|---|
| `location_name` | Data | E.g. "Godown A – Chamber 1" |
| `warehouse` | Link → Warehouse | ERPNext warehouse mapping |
| `capacity_kg` | Float | Max storage capacity |
| `current_stock_kg` | Float | Real-time (computed from Bin) |
| `min_temp_c` | Float | Minimum temperature setting |
| `max_temp_c` | Float | Maximum temperature setting |
| `current_temp_c` | Float | Latest IoT reading |
| `humidity_pct` | Float | Latest humidity reading |
| `iot_device_id` | Data | Sensor device identifier |
| `suitable_produce` | Table Multiselect → Item | Recommended items |
| `is_active` | Check | Is in use |

---

### 6.2 Cold Storage Inward

**Naming Series:** `CSI-.YYYY.-.#####`
**Is Submittable:** Yes

| Field | Type | Description |
|---|---|---|
| `inward_id` | Data | Auto: CSI-2026-00001 |
| `inward_date` | Datetime | Actual arrival timestamp |
| `procurement` | Link → Farmer Procurement | Source |
| `cold_storage` | Link → Cold Storage Location | Target location |
| `items_table` | Table → Inward Item | Items & quantities |
| `stock_entry` | Link → Stock Entry | ERPNext SE (Material Receipt) |
| `temperature_at_arrival` | Float | Recorded temp °C |
| `handling_notes` | Small Text | Special handling info |
| `expiry_date` | Date | Estimated expiry (auto from perishability_days) |

---

### 6.3 Cold Storage Outward

**Naming Series:** `CSO-.YYYY.-.#####`
**Is Submittable:** Yes

| Field | Type | Description |
|---|---|---|
| `outward_id` | Data | Auto: CSO-2026-00001 |
| `outward_date` | Datetime | Dispatch timestamp |
| `dispatch_order` | Link → Dispatch Order | Source |
| `cold_storage` | Link → Cold Storage Location | Source location |
| `items_table` | Table → Outward Item | Items & quantities |
| `stock_entry` | Link → Stock Entry | ERPNext SE (Material Issue) |
| `temperature_at_dispatch` | Float | Recorded temp °C |

---

## 7. DocType Design — Payments & Ledger

### 7.1 Farmer Payment

**Naming Series:** `FPY-.YYYY.-.#####`
**Is Submittable:** Yes

| Field | Type | Description |
|---|---|---|
| `payment_id` | Data | Auto: FPY-2026-00001 |
| `farmer` | Link → Farmer | Payable farmer |
| `procurement` | Link → Farmer Procurement | Source transaction |
| `due_amount` | Currency | Original payable |
| `deductions_table` | Table → Deduction | TDS / advances / damages |
| `net_payable` | Currency | due_amount minus deductions |
| `payment_mode` | Select | Bank Transfer / Cash / UPI |
| `utr_number` | Data | Bank transaction reference |
| `payment_date` | Date | Actual disbursement date |
| `payment_entry` | Link → Payment Entry | ERPNext PE linked |
| `status` | Select | Pending / Processed / Failed |
| `remarks` | Small Text | Narration |

### 7.2 ERPNext Accounts Integration Points

| Flow | ERPNext Document | Notes |
|---|---|---|
| Farmer as Supplier | Supplier | Auto-created on KYC verify |
| Procurement → Payable | Purchase Invoice | Submitted on procurement accept |
| Farmer Payment | Payment Entry | Linked from Farmer Payment |
| Customer Order → Receivable | Sales Invoice | Auto from Delivery Note |
| Customer Payment | Payment Entry | Linked from portal / manual |
| Stock Movement | Stock Ledger Entry | Every inward / outward |
| GST Compliance | GST Settings + e-Invoice | HSN from Item master |

---

## 8. Farmer Portal — Features & Implementation

**URL:** `https://yourdomain.com/farmer-portal`
**Auth:** Mobile OTP (Frappe OTP / Twilio)
**Tech:** Frappe Jinja templates + whitelisted Python API

### Portal Pages

| Page / URL | Feature | Data Source |
|---|---|---|
| `/farmer-portal` | Landing + OTP Login | `frappe.auth` |
| `/farmer-portal/dashboard` | Today's procurement, pending payment, YTD earnings | Farmer Payment + Procurement |
| `/farmer-portal/procurements` | List of all procurement entries with status | Farmer Procurement |
| `/farmer-portal/procurements/<id>` | Detail view: items, QC result, agent name | Farmer Procurement + QC |
| `/farmer-portal/payments` | Payment history with UTR, amount, date | Farmer Payment |
| `/farmer-portal/payments/pending` | Pending dues breakdown | Farmer Payment |
| `/farmer-portal/price-board` | Today's mandi rates for produce they grow | Item.market_price_per_kg |
| `/farmer-portal/profile` | Update bank account, contact info | Farmer DocType |
| `/farmer-portal/support` | Raise query to agent / admin | Issue DocType |

### Sample API Method (farmer_portal.py)

```python
import frappe

@frappe.whitelist()
def get_dashboard_data(farmer_id):
    farmer = frappe.get_doc("Farmer", farmer_id)
    today_procurement = frappe.db.sql("""
        SELECT SUM(total_amount), SUM(total_weight_kg)
        FROM `tabFarmer Procurement`
        WHERE farmer = %s AND procurement_date = CURDATE()
        AND docstatus = 1
    """, farmer_id, as_dict=True)

    pending_payment = frappe.db.sql("""
        SELECT SUM(net_payable)
        FROM `tabFarmer Payment`
        WHERE farmer = %s AND status = 'Pending'
    """, farmer_id, as_dict=True)

    return {
        "today_procurement": today_procurement[0],
        "pending_payment": pending_payment[0],
        "farmer": farmer.as_dict()
    }
```

### Implementation Notes

- OTP login via Frappe Email/SMS OTP or Twilio Verify
- Portal is mobile-first (Bootstrap 5 + custom CSS)
- Farmers can download payment receipts as PDF (WeasyPrint / ReportLab)
- Push notifications via WhatsApp API for payment credits
- Language support: English + regional language (i18n via Frappe translate)
- Role: `Farmer Portal` — read-only access to own records only

---

## 9. Customer Portal — Features & Implementation

**URL:** `https://yourdomain.com/customer-portal`
**Auth:** Email + Password (Frappe standard)
**Tech:** Frappe Jinja templates + REST API for integrations

### Portal Pages

| Page / URL | Feature | Data Source |
|---|---|---|
| `/customer-portal` | Login / Register | `frappe.auth` + Customer |
| `/customer-portal/dashboard` | Today's orders, delivery status, outstanding balance | Sales Order + Delivery Note |
| `/customer-portal/orders` | Full order history with filters | Sales Order |
| `/customer-portal/orders/new` | Place new order: item, qty, delivery date | Sales Order creation |
| `/customer-portal/orders/<id>` | Order detail: items, dispatch, tracking, POD | Dispatch Order + Delivery Note |
| `/customer-portal/invoices` | Sales invoices list + download PDF | Sales Invoice |
| `/customer-portal/payments` | Payment history and outstanding dues | Payment Entry |
| `/customer-portal/price-list` | Current pricing per item / grade | Price List (Customer-specific) |
| `/customer-portal/products` | Browse available produce with stock info | Item + Bin |
| `/customer-portal/reports` | Download purchase reports (CSV/PDF) | Custom API |
| `/customer-portal/profile` | Manage delivery addresses, contacts, GSTIN | Customer + Address |

### REST API for Swiggy / Zomato / Hyperpure Integration

```
POST /api/method/freshroute.api.customer_portal.create_order
GET  /api/method/freshroute.api.customer_portal.get_order_status
GET  /api/method/freshroute.api.customer_portal.get_price_list
GET  /api/method/freshroute.api.customer_portal.get_available_stock
POST /api/method/freshroute.api.customer_portal.cancel_order
```

**Authentication:** API Key + Secret (Frappe built-in)
**Format:** JSON
**Rate Limit:** 1000 requests/hour per customer

### Sample API (customer_portal.py)

```python
@frappe.whitelist(allow_guest=False)
def create_order(customer, items, delivery_date, delivery_address):
    so = frappe.new_doc("Sales Order")
    so.customer = customer
    so.delivery_date = delivery_date
    for item in frappe.parse_json(items):
        so.append("items", {
            "item_code": item["item_code"],
            "qty": item["qty"],
            "rate": get_customer_rate(customer, item["item_code"])
        })
    so.insert()
    so.submit()
    return {"order_id": so.name, "status": "Confirmed"}
```

---

## 10. Reports & Dashboards

### Custom Reports

| Report Name | Type | Key Columns | Used By |
|---|---|---|---|
| Daily Procurement Summary | Script Report | Date, Farmer, Item, Qty, Rate, Amount, Agent | Ops, Accounts |
| Farmer Ledger | Script Report | Farmer, Procurement, Due, Paid, Balance, Last Payment | Accounts, Farmer Portal |
| Cold Storage Stock Report | Query Report | Location, Item, Qty, Entry Date, Expiry, Age(Days), Temp | Warehouse, Ops |
| Customer Sales Report | Script Report | Customer, Item, Qty, Rate, Amount, Invoice, Payment Status | Accounts, Customer Portal |
| Dispatch Report | Script Report | Date, Customer, Vehicle, Driver, Items, Weight, Status, POD | Ops Manager |
| Payment Reconciliation | Script Report | Farmer/Customer, Invoice, Payment, Outstanding, Mode, UTR | Accounts |
| Produce Wastage Report | Query Report | Item, Procured Qty, Sold Qty, Expired Qty, Wastage %, Cost | Management |
| Agent Performance | Script Report | Agent, Trips, Total Procured, Total Value, Avg Rate, Farmers | Management |
| Cold Storage Temp Log | Query Report | Location, Timestamp, Temp, Humidity, Alert Flag | Cold Storage |
| GST Purchase Register | Script Report | Supplier, GSTIN, HSN, Qty, Taxable, GST, Total | Accounts / CA |
| GST Sales Register | Script Report | Customer, GSTIN, Invoice, HSN, Qty, Taxable, GST, Total | Accounts / CA |
| Mandi Rate vs Purchase Price | Chart Report | Item, Market Rate, Procured Rate, Variance, Date | Management |

### Dashboard Widgets

| Widget | Chart Type | Metric |
|---|---|---|
| Today's Procurement (kg & ₹) | Number Card | Sum of today's procurement |
| Cold Storage Utilisation | Donut Chart | Current stock vs capacity per location |
| Daily Dispatch Progress | Progress Bar | Dispatched / Total planned for today |
| Pending Farmer Payments | Number Card | Sum of unpaid Farmer Payments |
| Customer Outstanding | Number Card | Sum of unpaid Sales Invoices |
| Revenue vs Target (MTD) | Bar Chart | Month-to-date sales vs target |
| Wastage Trend (30 days) | Line Chart | Daily wastage kg over 30 days |
| Top 5 Customers by Volume | Bar Chart | Customer-wise kg dispatched this month |
| Agent Procurement Map | Heatmap iframe | Geographic distribution via GPS |
| Temperature Alerts Today | Number Card | Count of out-of-range temp events |

---

## 11. Workflows & Automation

### 11.1 Farmer Procurement Workflow

```
Draft
  │
  ▼ (Agent submits)
Submitted ──► WhatsApp alert to QC team
  │
  ▼ (QC Inspector opens linked Quality Check)
QC In Progress
  │
  ├─► [Pass]     ──► Cold Storage Inward auto-created
  │                   Stock Entry (Material Receipt) posted
  │                   Farmer Payment created (Pending)
  │
  ├─► [Partial]  ──► Adjust accepted qty
  │                   Partial Stock Entry posted
  │                   Farmer Payment for accepted qty
  │
  └─► [Reject]   ──► Notify farmer via WhatsApp
                      Procurement cancelled
```

### 11.2 Customer Order to Delivery Workflow

```
Customer Portal / API
  │ Place Order
  ▼
Sales Order (Draft)
  │
  ▼ (Ops confirms)
Sales Order (Submitted)
  │
  ▼ (Ops creates)
Dispatch Order (Draft)
  │
  ▼ (Submit)
Dispatch Order (Submitted)
  ├── Cold Storage Outward auto-created
  ├── Stock Entry (Material Issue) posted
  └── WhatsApp to driver with route & load
  │
  ▼ (Driver picks up)
Dispatch Order → "Dispatched"
  │
  ▼ (Delivery confirmed + POD)
Delivery Note (Submitted)
  │
  ▼ (Auto)
Sales Invoice (Submitted)
  │
  ▼ (Customer pays / Accounts records)
Payment Entry → Invoice Marked Paid
  │
  ▼
Customer Portal updated — receipt downloadable
```

### 11.3 Scheduled Automation

```python
# hooks.py — scheduler_events
scheduler_events = {
    "cron": {
        "0 6 * * *": ["freshroute.utils.notifications.daily_procurement_alert"],
        "0 8 * * *": ["freshroute.utils.notifications.update_market_prices"],
        "0 * * * *": ["freshroute.utils.notifications.cold_storage_temp_check"],
        "0 23 * * *": ["freshroute.utils.notifications.expiry_check"],
        "0 7 * * *": ["freshroute.utils.notifications.dispatch_reminder"],
        "0 0 * * 0": ["freshroute.utils.notifications.farmer_payment_due_report"],
        "0 0 1 * *": ["freshroute.utils.notifications.generate_gst_register"],
    }
}
```

| Frequency | Job | Action |
|---|---|---|
| Daily 6 AM | daily_procurement_alert | Email Ops Manager list of scheduled farm pickups |
| Daily 8 AM | update_market_prices | Fetch mandi rates API and update `Item.market_price_per_kg` |
| Hourly | cold_storage_temp_check | Read IoT sensor; alert if temp out of range |
| Daily 11 PM | expiry_check | Flag items within 2 days of expiry; notify warehouse |
| Daily 7 AM | dispatch_reminder | WhatsApp driver with today's route & load list |
| Weekly Sunday | farmer_payment_due_report | Email Accounts team pending farmer dues |
| Monthly 1st | generate_gst_register | Auto-generate GST Purchase & Sales Register |

---

## 12. ERPNext v15 Native Module Integrations

| ERPNext Module | How FreshRoute Uses It | Key DocTypes Used |
|---|---|---|
| **Stock / Inventory** | All produce movements post Stock Entries against mapped Warehouses | Stock Entry, Bin, Stock Ledger Entry, Warehouse |
| **Buying** | Each Farmer Procurement creates a Purchase Invoice (Farmer as Supplier) | Supplier, Purchase Order, Purchase Invoice |
| **Selling** | Customer orders: Sales Order → Delivery Note → Sales Invoice | Customer, Sales Order, Delivery Note, Sales Invoice |
| **Accounts** | Full P&L, Balance Sheet, Trial Balance | Journal Entry, Payment Entry, Cost Center |
| **HR & Payroll** | Field agents and drivers as Employees; incentive payroll | Employee, Salary Slip, Expense Claim |
| **Quality Management** | Custom QC hooks into ERPNext Quality Inspection | Quality Inspection, Quality Inspection Reading |
| **CRM** | Customer accounts, communication logs, complaint management | Customer, Contact, Lead, Issue |
| **Assets** | Cold storage equipment, vehicles as fixed assets | Asset, Asset Maintenance |
| **GST (India)** | GSTIN, HSN codes; auto e-invoice for B2B customers | GST Settings, e-Invoice Log, GSTR-1 |
| **Email & Notifications** | All workflow alerts via Frappe Email Queue + SMS | Email Queue, Notification, SMS Center |
| **Frappe Web Forms** | Farmer KYC public form, customer registration | Web Form |

---

## 13. Phased Implementation Roadmap

### Phase 1 — Foundation & ERPNext Setup *(Weeks 1–3)*

- Set up Ubuntu 22.04 server (16 GB RAM, 4 vCPU, 200 GB SSD)
- Install bench, ERPNext v15, MariaDB, Redis, Nginx
- Configure HTTPS (Let's Encrypt), domain DNS
- Install freshroute app: `bench get-app` + `bench install-app`
- Configure ERPNext: Company, Chart of Accounts, Fiscal Year, GST
- Set up Warehouses mapping cold storage locations
- Import Item master (produce), Customer masters from existing data

### Phase 2 — Master DocTypes & Farmer Module *(Weeks 4–6)*

- Build Farmer DocType (all fields, permissions, naming series)
- Build Vehicle Master, Delivery Route master
- Custom fields on Item (produce category, perishability, temp, grading)
- Farmer KYC Web Form (public, no login required)
- Farmer portal skeleton (OTP login, dashboard, profile)
- Agent mobile view for Farmer Procurement entry
- Farmer Payment DocType + payment workflow

### Phase 3 — Cold Storage & Procurement Flow *(Weeks 7–9)*

- Cold Storage Location, Inward, Outward DocTypes
- Quality Check DocType + QC → Procurement linkage
- Auto Stock Entry creation on QC pass (hooks)
- Cold storage live dashboard (temp, humidity, utilisation)
- IoT sensor integration (MQTT / REST adapter) for temperature
- Expiry alert scheduler job
- Farmer Payment auto-creation on QC pass

### Phase 4 — Customer Module & Portals *(Weeks 10–13)*

- Dispatch Order DocType + Dispatch Item child
- Auto Delivery Note creation on dispatch submit
- Auto Sales Invoice from Delivery Note
- Customer portal: login, orders, invoices, payments, price board
- REST API endpoints for Swiggy / Zomato integration
- Customer-specific price lists in ERPNext
- WhatsApp notifications: order confirmed, dispatched, delivered

### Phase 5 — Reports, Dashboards & Workflows *(Weeks 14–16)*

- All 12 custom reports (Script + Query type)
- ERPNext Dashboard with 10 widgets
- GST Purchase + Sales Register
- Frappe Workflows (Procurement, Dispatch)
- Scheduled jobs (market price, expiry, payment due)
- Role-based permissions review for all DocTypes
- Print formats: Invoice, Delivery Challan, Procurement Receipt

### Phase 6 — Testing, UAT & Training *(Weeks 17–19)*

- Unit tests (`frappe.tests`) for all API methods
- Integration tests: full procurement → payment flow
- UAT with actual farmers, agents, and customers
- Load testing: 1000 concurrent portal users
- Bug fix sprints (2 × 1-week cycles)
- End-user training (Farmer app, Agent mobile, Ops, Accounts)
- Training videos + user manual (PDF)

### Phase 7 — Go-Live & Hypercare *(Weeks 20–22)*

- Production go-live cutover (data migration from Excel/existing system)
- Hypercare support (14 days: on-call developer)
- Performance monitoring (Frappe error logs, server metrics)
- Weekly review calls with business team
- Minor change requests (CR) — 10 hrs buffer included
- Post go-live documentation handover
- Source code handover to client GitHub

### Timeline Summary

```
Week:  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22
       [──Phase 1──][──Phase 2──][──Phase 3──][───Phase 4───][─Ph5─][─Ph6─][─Ph7─]
```

---

## 14. Key Files Reference Guide

| File Path | Purpose |
|---|---|
| `freshroute/hooks.py` | App hooks: scheduler_events, website_route_rules, fixtures, doc_events |
| `freshroute/freshroute/doctype/farmer/farmer.py` | Farmer controller: auto-create portal user, validate Aadhaar mask |
| `freshroute/freshroute/doctype/farmer_procurement/farmer_procurement.py` | Procurement controller: total calc, QC linking, Stock Entry creation |
| `freshroute/freshroute/doctype/quality_check/quality_check.py` | QC controller: accepted qty calc, trigger Farmer Payment creation |
| `freshroute/freshroute/doctype/cold_storage_inward/cold_storage_inward.py` | Create Stock Entry (Material Receipt) on submit |
| `freshroute/freshroute/doctype/cold_storage_outward/cold_storage_outward.py` | Create Stock Entry (Material Issue) on submit, update bin |
| `freshroute/freshroute/doctype/dispatch_order/dispatch_order.py` | Create Delivery Note + CS Outward on submit |
| `freshroute/freshroute/doctype/farmer_payment/farmer_payment.py` | Net payable calc, Payment Entry creation, WhatsApp hook |
| `freshroute/api/farmer_portal.py` | Whitelisted methods: get_dashboard, get_procurements, get_payments |
| `freshroute/api/customer_portal.py` | Whitelisted methods: place_order, get_order_status, get_invoices |
| `freshroute/api/integrations.py` | Swiggy / Zomato REST adapter methods |
| `freshroute/utils/notifications.py` | WhatsApp, Email, SMS helper functions |
| `freshroute/utils/pricing.py` | Dynamic pricing logic (grade, season, customer tier) |
| `freshroute/templates/pages/farmer_portal.html` | Farmer portal main Jinja template |
| `freshroute/templates/pages/customer_portal.html` | Customer portal main Jinja template |
| `freshroute/public/js/farmer_procurement.js` | Client script: auto-fill rate from market price, grade validation |
| `freshroute/public/js/dispatch_order.js` | Client script: vehicle capacity check, route auto-fill |
| `freshroute/freshroute/report/daily_procurement_summary/daily_procurement_summary.py` | Script report Python logic |
| `freshroute/freshroute/report/farmer_ledger/farmer_ledger.py` | Farmer payment ledger report |
| `freshroute/freshroute/page/freshroute_dashboard/freshroute_dashboard.js` | Custom desk page JS |
| `freshroute/freshroute/workspace/freshroute.json` | Sidebar workspace definition |
| `freshroute/patches.txt` | Database migration patches for upgrades |
| `freshroute/requirements.txt` | Python dependencies (requests, twilio, paho-mqtt, etc.) |

### requirements.txt

```
requests>=2.28.0
twilio>=8.0.0
paho-mqtt>=1.6.0
reportlab>=4.0.0
weasyprint>=59.0
pandas>=2.0.0
openpyxl>=3.1.0
```

---

## 15. Testing, Deployment & Go-Live Checklist

### ☐ Server & Infrastructure

- [ ] Ubuntu 22.04 LTS server hardened (fail2ban, UFW, SSH key-only)
- [ ] SSL certificate active (auto-renew via certbot)
- [ ] Daily database backup to remote S3 / Backblaze B2
- [ ] Monitoring: UptimeRobot + Frappe error email alerts
- [ ] Redis max memory policy set (`allkeys-lru`)
- [ ] Nginx rate limiting configured

### ☐ ERPNext Configuration

- [ ] Company, Chart of Accounts, Fiscal Year set up
- [ ] GST settings: GSTIN, tax templates (0%, 5%, 12% for produce)
- [ ] All Warehouses created and mapped to Cold Storage Locations
- [ ] Item master complete: HSN codes, UOM, storage temp, perishability
- [ ] Customer and Supplier (Farmer) masters imported / verified
- [ ] Price Lists created per customer tier (Swiggy, Zomato, Retail)
- [ ] User roles assigned: Agent, QC Inspector, Ops Manager, Accounts, Admin

### ☐ FreshRoute App

- [ ] All DocType forms tested end-to-end (Draft → Submit → Cancel)
- [ ] Naming series configured for all DocTypes
- [ ] Farmer portal OTP login tested on mobile (Android + iOS)
- [ ] Customer portal order placement tested (manual + API)
- [ ] All scheduled jobs tested in staging environment
- [ ] WhatsApp notifications tested for all workflow steps
- [ ] IoT temperature integration verified (if applicable at launch)
- [ ] All 12 reports generate correct data with test dataset
- [ ] Print formats: Invoice, Challan, Procurement Receipt — verified PDF output
- [ ] REST API endpoints tested with Postman (Swiggy/Zomato flows)

### ☐ Data Migration

- [ ] Farmer master data imported and portal users created
- [ ] Customer master imported with credit limits and price lists
- [ ] Opening stock balance entered in ERPNext (cold storage items)
- [ ] Outstanding farmer payments entered as opening balances
- [ ] Customer outstanding invoices entered as opening balances

### ☐ Training Completed

- [ ] Field Agent: mobile procurement entry, quality check, dispatch scan
- [ ] Cold Storage: inward/outward entry, temperature logging
- [ ] Ops Manager: dispatch planning, vehicle assignment, route management
- [ ] Accounts: farmer payment, sales invoice reconciliation, GST reports
- [ ] Admin: user management, system settings, report access

### ☐ Go-Live Sign-Off

- [ ] UAT sign-off from business owner
- [ ] Data backup taken before cutover
- [ ] DNS cutover done (old system → new system)
- [ ] Parallel run for 1 week (old + new simultaneously)
- [ ] Developer on call for first 14 days post go-live

---

## Appendix: Useful bench Commands

```bash
# Start development server
bench start

# Run database migrations
bench --site yoursite.com migrate

# Clear cache
bench --site yoursite.com clear-cache

# Run background jobs
bench worker

# Console access
bench --site yoursite.com console

# Install / reinstall app
bench --site yoursite.com install-app freshroute
bench --site yoursite.com uninstall-app freshroute

# Export fixtures (after configuring in hooks.py)
bench --site yoursite.com export-fixtures

# Run tests
bench --site yoursite.com run-tests --app freshroute

# Backup
bench --site yoursite.com backup --with-files

# Restore
bench --site yoursite.com restore /path/to/backup.sql.gz
```

---

*Document Version: 1.0 | April 2026 | FreshRoute Tech Team*
*For internal use and implementation team reference only.*
