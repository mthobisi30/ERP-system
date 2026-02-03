# Complete ERP System API Documentation

Base URL: `https://your-app.vercel.app/api`

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Auth Endpoints

#### POST /api/auth/register
Register a new user
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```
Response: `201 Created`

#### POST /api/auth/login
Login to get access token
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```
Response: `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "user": { ... }
}
```

#### GET /api/auth/me
Get current user info (Protected)
Response: `200 OK`

#### POST /api/auth/logout
Logout current user (Protected)
Response: `200 OK`

---

## Users

#### GET /api/users
Get all users (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### GET /api/users/:id
Get specific user (Protected)
Response: `200 OK`

#### PUT /api/users/:id
Update user (Protected)
```json
{
  "first_name": "Jane",
  "phone": "+1234567890"
}
```
Response: `200 OK`

#### DELETE /api/users/:id
Delete user (Protected)
Response: `200 OK`

---

## Projects

#### GET /api/projects
Get all projects (Protected)
Query params: `page`, `per_page`, `status`
Response: `200 OK`

#### POST /api/projects
Create new project (Protected)
```json
{
  "name": "Website Redesign",
  "description": "Complete website overhaul",
  "status": "planning",
  "priority": "high",
  "start_date": "2024-01-01",
  "end_date": "2024-06-30",
  "budget": 50000
}
```
Response: `201 Created`

#### GET /api/projects/:id
Get specific project (Protected)
Response: `200 OK`

#### PUT /api/projects/:id
Update project (Protected)
Response: `200 OK`

#### DELETE /api/projects/:id
Delete project (Protected)
Response: `200 OK`

#### GET /api/projects/:id/milestones
Get project milestones (Protected)
Response: `200 OK`

#### POST /api/projects/:id/milestones
Create milestone (Protected)
```json
{
  "name": "Phase 1 Complete",
  "due_date": "2024-03-15",
  "status": "pending"
}
```
Response: `201 Created`

---

## Tasks

#### GET /api/tasks
Get all tasks (Protected)
Query params: `page`, `per_page`, `status`, `assigned_to`
Response: `200 OK`

#### POST /api/tasks
Create new task (Protected)
```json
{
  "title": "Design homepage mockup",
  "description": "Create initial design concepts",
  "project_id": "uuid-here",
  "assigned_to": "uuid-here",
  "status": "todo",
  "priority": "high",
  "due_date": "2024-02-15T17:00:00Z",
  "estimated_hours": 8
}
```
Response: `201 Created`

#### GET /api/tasks/:id
Get specific task (Protected)
Response: `200 OK`

#### PUT /api/tasks/:id
Update task (Protected)
Response: `200 OK`

#### DELETE /api/tasks/:id
Delete task (Protected)
Response: `200 OK`

#### GET /api/tasks/:id/comments
Get task comments (Protected)
Response: `200 OK`

#### POST /api/tasks/:id/comments
Add comment to task (Protected)
```json
{
  "comment": "Updated the design based on feedback"
}
```
Response: `201 Created`

---

## Customers (CRM)

#### GET /api/customers
Get all customers (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### POST /api/customers
Create new customer (Protected)
```json
{
  "customer_code": "CUST001",
  "company_name": "Acme Corp",
  "contact_person": "John Smith",
  "email": "john@acme.com",
  "phone": "+1234567890",
  "customer_type": "business",
  "status": "active"
}
```
Response: `201 Created`

#### GET /api/customers/:id
Get specific customer (Protected)
Response: `200 OK`

#### PUT /api/customers/:id
Update customer (Protected)
Response: `200 OK`

#### DELETE /api/customers/:id
Delete customer (Protected)
Response: `200 OK`

---

## Leads

#### GET /api/leads
Get all leads (Protected)
Query params: `page`, `per_page`, `status`
Response: `200 OK`

#### POST /api/leads
Create new lead (Protected)
```json
{
  "company_name": "Tech Startup Inc",
  "contact_name": "Jane Doe",
  "email": "jane@techstartup.com",
  "phone": "+1234567890",
  "source": "website",
  "status": "new",
  "interest_level": "hot",
  "estimated_value": 25000
}
```
Response: `201 Created`

#### GET /api/leads/:id
Get specific lead (Protected)
Response: `200 OK`

#### PUT /api/leads/:id
Update lead (Protected)
Response: `200 OK`

#### DELETE /api/leads/:id
Delete lead (Protected)
Response: `200 OK`

---

## Opportunities

#### GET /api/opportunities
Get all opportunities (Protected)
Response: `200 OK`

#### POST /api/opportunities
Create new opportunity (Protected)
```json
{
  "name": "Enterprise License Deal",
  "customer_id": "uuid-here",
  "stage": "prospecting",
  "estimated_value": 100000,
  "probability": 50,
  "expected_close_date": "2024-06-30"
}
```
Response: `201 Created`

#### GET /api/opportunities/:id
Get specific opportunity (Protected)
Response: `200 OK`

#### PUT /api/opportunities/:id
Update opportunity (Protected)
Response: `200 OK`

---

## Products

#### GET /api/products
Get all products (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### POST /api/products
Create new product (Protected)
```json
{
  "sku": "PROD-001",
  "name": "Premium Widget",
  "description": "High-quality widget",
  "category_id": "uuid-here",
  "cost_price": 50.00,
  "selling_price": 99.99,
  "unit_of_measure": "unit",
  "is_active": true
}
```
Response: `201 Created`

#### GET /api/products/:id
Get specific product (Protected)
Response: `200 OK`

#### PUT /api/products/:id
Update product (Protected)
Response: `200 OK`

#### DELETE /api/products/:id
Delete product (Protected)
Response: `200 OK`

---

## Inventory

#### GET /api/inventory
Get inventory levels (Protected)
Response: `200 OK`

#### GET /api/inventory/warehouses
Get all warehouses (Protected)
Response: `200 OK`

#### POST /api/inventory/warehouses
Create new warehouse (Protected)
```json
{
  "code": "WH-01",
  "name": "Main Warehouse",
  "manager_id": "uuid-here"
}
```
Response: `201 Created`

---

## Sales

#### GET /api/sales/orders
Get all sales orders (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### POST /api/sales/orders
Create new sales order (Protected)
```json
{
  "order_number": "SO-2024-001",
  "customer_id": "uuid-here",
  "order_date": "2024-02-03",
  "status": "pending",
  "payment_status": "unpaid",
  "total_amount": 1500.00
}
```
Response: `201 Created`

#### GET /api/sales/orders/:id
Get specific sales order (Protected)
Response: `200 OK`

#### GET /api/sales/quotations
Get all quotations (Protected)
Response: `200 OK`

#### POST /api/sales/quotations
Create new quotation (Protected)
```json
{
  "quote_number": "QT-2024-001",
  "customer_id": "uuid-here",
  "quote_date": "2024-02-03",
  "valid_until": "2024-03-03",
  "total_amount": 2500.00
}
```
Response: `201 Created`

---

## Procurement

#### GET /api/procurement/purchase-orders
Get all purchase orders (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### POST /api/procurement/purchase-orders
Create new purchase order (Protected)
```json
{
  "po_number": "PO-2024-001",
  "supplier_id": "uuid-here",
  "order_date": "2024-02-03",
  "status": "draft",
  "total_amount": 5000.00
}
```
Response: `201 Created`

#### GET /api/procurement/purchase-orders/:id
Get specific purchase order (Protected)
Response: `200 OK`

#### PUT /api/procurement/purchase-orders/:id
Update purchase order (Protected)
Response: `200 OK`

---

## Suppliers

#### GET /api/suppliers
Get all suppliers (Protected)
Response: `200 OK`

#### POST /api/suppliers
Create new supplier (Protected)
```json
{
  "supplier_code": "SUP-001",
  "company_name": "Parts Supplier Inc",
  "contact_person": "Bob Johnson",
  "email": "bob@supplier.com",
  "phone": "+1234567890"
}
```
Response: `201 Created`

#### GET /api/suppliers/:id
Get specific supplier (Protected)
Response: `200 OK`

---

## Accounting

#### GET /api/accounting/accounts
Get chart of accounts (Protected)
Response: `200 OK`

#### GET /api/accounting/journal-entries
Get journal entries (Protected)
Response: `200 OK`

#### POST /api/accounting/journal-entries
Create journal entry (Protected)
```json
{
  "entry_number": "JE-2024-001",
  "entry_date": "2024-02-03",
  "description": "Monthly closing entry"
}
```
Response: `201 Created`

---

## Invoices

#### GET /api/invoices
Get all invoices (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### POST /api/invoices
Create new invoice (Protected)
```json
{
  "invoice_number": "INV-2024-001",
  "customer_id": "uuid-here",
  "invoice_date": "2024-02-03",
  "due_date": "2024-03-03",
  "status": "draft",
  "total_amount": 1500.00
}
```
Response: `201 Created`

#### GET /api/invoices/:id
Get specific invoice (Protected)
Response: `200 OK`

---

## Payments

#### GET /api/payments
Get all payments (Protected)
Response: `200 OK`

#### POST /api/payments
Record new payment (Protected)
```json
{
  "payment_number": "PAY-2024-001",
  "payment_type": "received",
  "customer_id": "uuid-here",
  "invoice_id": "uuid-here",
  "payment_date": "2024-02-03",
  "amount": 1500.00,
  "payment_method": "bank-transfer"
}
```
Response: `201 Created`

---

## Expenses

#### GET /api/expenses
Get all expenses (Protected)
Response: `200 OK`

#### POST /api/expenses
Create new expense (Protected)
```json
{
  "expense_number": "EXP-2024-001",
  "expense_date": "2024-02-03",
  "category": "Office Supplies",
  "amount": 250.00,
  "description": "Printer ink and paper"
}
```
Response: `201 Created`

---

## HR

#### GET /api/hr/performance-reviews
Get performance reviews (Protected)
Response: `200 OK`

#### GET /api/hr/attendance
Get attendance records (Protected)
Response: `200 OK`

#### GET /api/hr/leaves
Get leave requests (Protected)
Response: `200 OK`

#### POST /api/hr/leaves
Create leave request (Protected)
```json
{
  "user_id": "uuid-here",
  "leave_type": "vacation",
  "start_date": "2024-03-01",
  "end_date": "2024-03-05",
  "reason": "Family vacation"
}
```
Response: `201 Created`

---

## Tickets (Customer Service)

#### GET /api/tickets
Get all support tickets (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### POST /api/tickets
Create new ticket (Protected)
```json
{
  "ticket_number": "TIC-2024-001",
  "customer_id": "uuid-here",
  "subject": "Login issue",
  "description": "Cannot access account",
  "priority": "high",
  "status": "open",
  "category": "Technical"
}
```
Response: `201 Created`

#### GET /api/tickets/:id
Get specific ticket (Protected)
Response: `200 OK`

#### PUT /api/tickets/:id
Update ticket (Protected)
Response: `200 OK`

---

## Dashboard

#### GET /api/dashboard/stats
Get dashboard statistics (Protected)
Response: `200 OK`
```json
{
  "projects": {"total": 45, "active": 12},
  "tasks": {"total": 234, "pending": 67},
  "customers": 89,
  "sales": 125000.00
}
```

#### GET /api/dashboard/recent-activity
Get recent activity (Protected)
Response: `200 OK`

---

## Schedule

#### GET /api/schedule
Get user schedule (Protected)
Response: `200 OK`

#### POST /api/schedule
Create schedule event (Protected)
```json
{
  "title": "Team Meeting",
  "description": "Weekly standup",
  "event_type": "meeting",
  "start_time": "2024-02-05T10:00:00Z",
  "end_time": "2024-02-05T11:00:00Z"
}
```
Response: `201 Created`

---

## Time Tracking

#### GET /api/time-tracking
Get time entries (Protected)
Response: `200 OK`

#### POST /api/time-tracking
Create time entry (Protected)
```json
{
  "task_id": "uuid-here",
  "project_id": "uuid-here",
  "description": "Worked on homepage design",
  "start_time": "2024-02-03T09:00:00Z",
  "end_time": "2024-02-03T12:00:00Z",
  "duration_minutes": 180
}
```
Response: `201 Created`

---

## Notifications

#### GET /api/notifications
Get user notifications (Protected)
Response: `200 OK`

#### PUT /api/notifications/:id/read
Mark notification as read (Protected)
Response: `200 OK`

---

## Documents

#### GET /api/documents
Get all documents (Protected)
Response: `200 OK`

#### POST /api/documents
Upload document (Protected)
```json
{
  "name": "Contract.pdf",
  "description": "Client contract",
  "file_url": "https://...",
  "file_type": "pdf",
  "category": "Contracts"
}
```
Response: `201 Created`

---

## Settings

#### GET /api/settings
Get company settings (Protected)
Response: `200 OK`

#### PUT /api/settings
Update company settings (Protected)
```json
{
  "company_name": "Updated Company Name",
  "email": "updated@company.com",
  "currency": "EUR"
}
```
Response: `200 OK`

---

## Logs

#### GET /api/logs/activity
Get activity logs (Protected)
Query params: `page`, `per_page`
Response: `200 OK`

#### GET /api/logs/system
Get system logs (Protected)
Response: `200 OK`

---

## Reports

#### GET /api/reports
Get available reports (Protected)
Response: `200 OK`

#### POST /api/reports
Create new report (Protected)
```json
{
  "name": "Monthly Sales Report",
  "description": "Sales summary for the month",
  "report_type": "sales"
}
```
Response: `201 Created`

#### GET /api/reports/sales-summary
Get sales summary report (Protected)
Response: `200 OK`
```json
{
  "total_sales": 125000.00,
  "total_orders": 234,
  "average_order_value": 534.19
}
```

---

## Error Responses

All error responses follow this format:
```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "status_code": 400
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

API is rate limited to:
- 200 requests per day
- 50 requests per hour

Rate limit headers:
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1612345678
```

---

## Pagination

Paginated responses include:
```json
{
  "items": [...],
  "total": 100,
  "pages": 5,
  "current_page": 1,
  "has_next": true,
  "has_prev": false
}
```

---

## Testing

Use tools like:
- Postman
- Insomnia
- cURL
- HTTPie

Example cURL request:
```bash
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

---

## Support

For API support:
- GitHub Issues
- Email: support@yourcompany.com
- Documentation: https://docs.yourapp.com
