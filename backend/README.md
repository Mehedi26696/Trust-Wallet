# TrustWallet MVP Backend

A production-grade FastAPI backend for a digital wallet application with NID verification and fraud detection, specifically designed for the Bangladesh market.

## Features

###  User Management
- **Secure Registration**: Email-based registration with strong password requirements
- **NID Validation**: Bangladesh National ID format validation (10, 13, 17 digits)
- **JWT Authentication**: Secure token-based authentication
- **Profile Management**: Complete user profile management

### Wallet Operations  
- **Balance Management**: Real-time wallet balance tracking
- **Money Transfers**: Secure peer-to-peer money transfers
- **Transaction History**: Complete transaction logging and history

### Fraud Detection
- **Real-time Monitoring**: Automatic fraud detection during transactions
- **High-value Transaction Alerts**: Transactions > 100,000 BDT flagged
- **Velocity Checks**: Multiple high-value transactions in short time periods
- **Admin Dashboard**: Fraud alert management for administrators

### Security Features
- **bcrypt Password Hashing**: Industry-standard password security
- **JWT Token Authentication**: Secure API access
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Clean error responses without stack traces

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: Type-safe SQL database interactions
- **Supabase**: PostgreSQL database with real-time features (recommended)
- **SQLite**: Alternative lightweight database for local development
- **Pydantic**: Data validation using Python type annotations
- **Passlib**: Password hashing utilities
- **Python-Jose**: JWT token handling
- **Uvicorn**: ASGI server for running the application

##  Prerequisites

- Python 3.9+
- pip (Python package manager)

## Quick Start

### Option A: With Supabase (Recommended)

1. **Set up Supabase Database**:
   - Follow the detailed guide in [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
   - Create a Supabase project and get your credentials

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Test Supabase Connection**:
   ```bash
   python test_supabase.py
   ```

5. **Run the Application**:
   ```bash
   python main.py
   ```

### Option B: With Local SQLite

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "nid": "1234567890123"
}
```

#### Login
```http
POST /api/v1/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

#### Get Profile
```http
GET /api/v1/profile
Authorization: Bearer <jwt_token>
```

### Wallet Endpoints (Preview + Confirm)

#### Get Balance
```http
GET /api/v1/wallet
Authorization: Bearer <jwt_token>
```

#### Preview Send
```http
POST /api/v1/wallet/preview-send
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
   "receiver_phone": "+8801712345678",
   "amount": 1000.0
}
```

Response (includes fees and risk)
```json
{
   "sender_balance": 5000.0,
   "receiver_name": "John Doe",
   "receiver_phone": "+8801712345678",
   "amount": 1000.0,
   "fee": 10.0,
   "vat": 5.0,
   "total_deducted": 1015.0,
   "new_balance": 3985.0,
   "risk_check": {
      "risk_level": "medium",
      "risk_score": 0.62,
      "threshold": 0.5,
      "can_proceed": true,
      "warnings": ["Moderate fraud risk detected"],
      "details": {}
   },
   "can_proceed": true
}
```

#### Confirm Send
```http
POST /api/v1/wallet/confirm-send
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
   "receiver_phone": "+8801712345678",
   "amount": 1000.0
}
```

Frontend behavior: if preview risk score > 0.5 (50%), the app performs face verification before calling confirm.

---

### Fees & Charges

- Transaction Fee: ৳10 per ৳1000 (1.0%)
- Service VAT: ৳5 per ৳1000 (0.5%)
- Total deducted = amount + fee + vat

The preview endpoint returns `fee`, `vat`, and `total_deducted` for display. The confirm endpoint deducts the total from the sender; the receiver gets the base `amount`.

### Transaction Endpoints

#### Get Transaction History
```http
GET /api/v1/transactions?page=1&page_size=10
Authorization: Bearer <jwt_token>
```

#### Get Transaction Details
```http
GET /api/v1/transactions/{transaction_id}
Authorization: Bearer <jwt_token>
```

### Admin Endpoints

#### Get Fraud Alerts
```http
GET /api/v1/admin/fraud-alerts
Authorization: Bearer <admin_jwt_token>
```

#### Add Funds (Admin)
```http
POST /api/v1/admin/users/{user_id}/add-funds?amount=5000
Authorization: Bearer <admin_jwt_token>
```

## Database Schema

### Users Table
- `id`: Primary key
- `full_name`: User's full name
- `email`: Unique email address
- `password_hash`: Hashed password
- `nid`: National ID (validated)
- `wallet_balance`: Current balance in BDT
- `created_at`: Registration timestamp
- `is_active`: Account status

### Transactions Table
- `id`: Primary key
- `sender_id`: Foreign key to users
- `receiver_id`: Foreign key to users
- `amount`: Transaction amount
- `timestamp`: Transaction time
- `status`: Transaction status
- `description`: Optional description

### Fraud Alerts Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `reason`: Alert reason
- `timestamp`: Alert time
- `severity`: Alert severity level
- `resolved`: Resolution status

## NID Validation Rules

### Supported Formats
- **10 digits**: Basic NID format
- **13 digits**: Extended format with year prefix
- **17 digits**: Smart NID format with year prefix

### Validation Rules
1. Must contain only digits
2. Must be exactly 10, 13, or 17 characters
3. For 13/17-digit NIDs: First 4 digits must be valid year (1900-2025)

### Examples
```
Valid NIDs:
- 1234567890 (10 digits)
- 1990123456789 (13 digits, starts with valid year)
- 19901234567890123 (17 digits, starts with valid year)

Invalid NIDs:
- 123 (too short)
- 1890123456789 (invalid year - before 1900)
- 12345abcde (contains non-digits)
```

##  Fraud Detection Rules

### High-Value Transaction Rule
- Transactions > 100,000 BDT are automatically flagged
- Status: High severity alert
- Action: Transaction blocked

### Velocity Rule
- More than 3 transactions ≥ 50,000 BDT within 5 minutes
- Status: Critical severity alert  
- Action: User temporarily blocked

### Future Enhancements
- Machine learning-based pattern detection
- Geographic location verification
- Device fingerprinting
- Behavioral analysis

## Testing

### Run API Tests
```bash
python test_api.py
```

### Manual Testing
1. Start the server: `python main.py`
2. Open http://localhost:8000/docs
3. Use the interactive API documentation to test endpoints

### Test Scenarios
- ✅ User registration with valid NID
- ❌ User registration with invalid NID
- ✅ User login with correct credentials
- ❌ User login with incorrect credentials
- ✅ Money transfer with sufficient balance
- ❌ Money transfer with insufficient balance
- ❌ High-value transaction (fraud detection)
- ✅ Transaction history retrieval

## Production Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com

# Fraud Detection
MAX_TRANSACTION_AMOUNT=100000
HIGH_VALUE_THRESHOLD=50000
```

### Database Migration
For production, switch from SQLite to PostgreSQL:

```python
# Update DATABASE_URL in environment
DATABASE_URL=postgresql://username:password@localhost/wallet_db
```

### Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Configure proper CORS origins
- [ ] Set up HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up proper logging
- [ ] Configure database backups
- [ ] Set up monitoring and alerts

## Project Structure

```
backend/
├── src/
│   ├── auth/                 # Authentication services
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── users/               # User routes
│   ├── transactions/        # Transaction routes
│   ├── utils/               # Utility functions
│   ├── admin_routes.py      # Admin endpoints
│   ├── config.py           # Configuration
│   └── __init__.py         # FastAPI app
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── test_api.py            # API tests
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Support

For support and questions:
- Create an issue on GitHub


##  Changelog

### v1.0.0 (Current)
- Initial release
- User registration and authentication
- Wallet operations
- Transaction system
- Fraud detection
- Admin dashboard
- NID validation for Bangladesh

### Planned Features
- [ ] SMS notifications
- [ ] Email notifications  
- [ ] Mobile app integration
- [ ] Advanced fraud detection with ML
- [ ] Multi-currency support
- [ ] QR code payments
- [ ] Merchant integrations

---

