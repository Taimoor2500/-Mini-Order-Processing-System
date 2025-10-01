# Mini Order Processing System

A robust, scalable FastAPI-based order processing system designed for handling vendor orders with priority-based processing, rate limiting, and background task management.

## Features

### Core Functionality
- **Order Management**: Create, retrieve, and track orders with comprehensive status updates
- **Vendor Management**: Register and manage vendors
- **Priority Processing**: Three-tier priority system (LOW, MEDIUM, HIGH) with different processing speeds
- **Background Processing**: Asynchronous order processing with detailed logging
- **Rate Limiting**: Built-in rate limiting to prevent API abuse (5 orders/minute per vendor)
- **Pagination**: Efficient pagination for large order datasets
- **Order Filtering**: Filter orders by date range, priority, and vendor
- **Order Summaries**: Get comprehensive statistics for vendors

### Technical Features
- **FastAPI Framework**
- **SQLAlchemy ORM**
- **SQLite Database**
- **Docker Support**
- **Comprehensive Logging**
- **Input Validation**
- **Error Handling**


## Installation & Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Docker & Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd -Mini-Order-Processing-System
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - API: http://localhost:8000

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - API: http://localhost:8000
   - Database file: `app.db` (mounted as volume)

## API Documentation

### Base URL
```
http://localhost:8000
```
```
mini-order-processing-system-production.up.railway.app
```

### Authentication
Currently, the API does not require authentication. Rate limiting is applied per vendor.

### Endpoints
**Create Order**
```
curl --request POST \
  --url http://127.0.0.1:8000/orders/ \
  --header 'content-type: application/json' \
  --data '{
  "order_id": "ORD1233434",
  "vendor_id": 1,
  "priority": "HIGH",
  "items": [
    {"item_name": "Item A", "quantity": 2},
    {"item_name": "Item B", "quantity": 1}
  ],
  "address": "123 Street",
  "city": "Karachi",
  "state": "Sindh",
  "postal_code": "7400"
}
'
```

**Get Vendor Order**
```
curl --request GET \
  --url 'http://127.0.0.1:8000/orders/1?start_date=2025-09-27&end_fate=2025-09-28'
```

**Get Order By Number**
```
curl --request GET \
  --url http://127.0.0.1:8000/orders/status/ORD12345
```
**Get Order Summary**
```
curl --request GET \
  --url http://127.0.0.1:8000/orders/summary/1
```

**Create Vendor**
```
curl --request POST \
  --url http://localhost:8000/vendors/ \
  --header 'content-type: application/json' \
  --data '{
  "name": "Test Vendor",
  "email": "test@vendor.com"
}'
```

**Get Vendors**
```
curl --request GET \
  --url http://localhost:8000/vendors
```

## Order Processing Flow

### Standard Orders (LOW/MEDIUM Priority)
1. Order created and queued for background processing
2. Status updated to "PROCESSING"
3. Sequential processing steps:
   - Validate order details
   - Check inventory availability
   - Calculate shipping costs
   - Process payment authorization
   - Send confirmation email
   - Update status to "PROCESSED"

### High Priority Orders
1. Order created and queued for priority processing
2. Expedited processing with faster execution
3. Priority-specific steps:
   - Expedited validation
   - Priority inventory allocation
   - Express shipping calculation
   - Immediate payment processing
   - Priority shipping label generation
   - Urgent customer notification

## Database Schema

### Orders Table
- `id`: Primary key
- `order_id`: Unique order identifier
- `vendor_id`: Foreign key to vendors table
- `priority`: Order priority (LOW, MEDIUM, HIGH)
- `status`: Order status (PENDING, PROCESSING, PROCESSED, FAILED, CANCELLED)
- `address`, `city`, `state`, `postal_code`: Shipping information
- `created_at`, `updated_at`: Timestamps

### Order Items Table
- `id`: Primary key
- `order_id`: Foreign key to orders table
- `item_name`: Name of the item
- `quantity`: Quantity ordered

### Vendors Table
- `id`: Primary key
- `name`: Vendor name (unique)
- `email`: Vendor email address

## Testing
Test files:
- `test_order_creation.py`: Order creation and validation tests
- `test_rate_limiting.py`: Rate limiting functionality tests
---

**Built with FastAPI, SQLAlchemy, and Python**
