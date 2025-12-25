# TrustWallet - Secure Digital Payment Service Platform

<div align="center">

![TrustWallet](https://img.shields.io/badge/TrustWallet-v1.0.0-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120.3-green)
![Flutter](https://img.shields.io/badge/Flutter-3.8.1-02569B?logo=flutter)
![Python](https://img.shields.io/badge/Python-3.9+-yellow?logo=python)

**A production-grade digital wallet application with advanced fraud detection, NID verification, and seamless money transfer capabilities for the Bangladesh market.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [API Documentation](#-api-documentation) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Documentation](#-api-documentation)
- [Security Features](#-security-features)
- [Machine Learning Models](#-machine-learning-models)
- [Database Schema](#-database-schema)
- [Environment Configuration](#-environment-configuration)
- [Testing](#-testing)
- [Dataset](#dataset)
- [Contributing](#-contributing)
- [Reporting Bugs](#-reporting-bugs)
- [License](#-license)

---

## Overview

TrustWallet is a comprehensive digital wallet solution built for the Bangladesh market, featuring secure money transfers, real-time fraud detection using machine learning, and Bangladesh National ID (NID) verification. The platform consists of a robust FastAPI backend and a beautiful Flutter mobile application.

### Why TrustWallet?

- **Bank-grade Security**: Multi-layered security with JWT authentication and bcrypt password hashing
- **AI-Powered Fraud Detection**: XGBoost models for real-time transaction monitoring with 95%+ accuracy
- **Groq AI Integration**: LLaMA 3.3 70B for intelligent, context-aware risk messaging
- **DeepFace Biometric Security**: Advanced facial recognition for high-risk transaction verification
- **Bangladesh-specific**: NID validation supporting 10, 13, and 17-digit formats
- **Modern Mobile App**: Beautiful Flutter UI with real-time fee calculation
- **Real-time Updates**: Supabase integration for instant transaction notifications
- **Compliance Ready**: Transaction logging and audit trails for regulatory compliance
- **Smart Fee Structure**: Transparent ৳10/1000 transaction fee + ৳5/1000 VAT

---

## Features

### User Management

- **Secure Registration & Authentication**
  - Email-based registration with strong password requirements
  - Phone number verification (Bangladesh format)
  - JWT token-based authentication
  - Password hashing with bcrypt
  - Secure token storage with Flutter Secure Storage
- **Bangladesh NID Verification**
  - Validates 10, 13, and 17-digit NID formats
  - Year validation for extended NIDs (1900-2025)
  - Format and checksum validation
- **Biometric Security**
  - Face registration during account setup
  - DeepFace-powered face verification
  - Multiple AI model support (VGG-Face, Facenet, ArcFace, etc.)
  - Secure face data storage with encryption
  - Step-up authentication for high-risk transactions
  - Real-time verification via mobile camera

### Wallet Operations

- **Balance Management**
  - Real-time wallet balance tracking
  - Secure balance updates
  - Transaction history with pagination
- **Money Transfers**
  - Peer-to-peer money transfers via phone number
  - Two-step transaction flow: preview then confirm
  - Transaction preview before confirmation
  - Multi-step transaction verification
  - Risk assessment before transfer
  - Clear fees and VAT applied on preview (see Fees & Charges)
  - Smart fee calculation: ৳10 per ৳1000 (1%) + ৳5 per ৳1000 (0.5% VAT)
  - Total deduction transparency (amount + fee + VAT)

### Advanced Fraud Detection

#### XGBoost-based ML Detection

- Real-time transaction pattern analysis
- Velocity checks (multiple high-value transactions)
- Risk scoring system (0-100% scale)
- Historical behavior analysis
- Feature engineering with 20+ transaction attributes
- Model performance: 95%+ accuracy on test data
- Step-up verification: If risk score > 50%, face verification is required on confirm screen

#### Rule-based Fraud Prevention

- High-value transaction alerts (>100,000 BDT)
- Velocity rules (3+ transactions ≥50,000 BDT in 5 minutes)
- Automatic transaction blocking for suspicious activities
- Granular severity levels: critical, high, medium-high, medium, medium-low, low
- Smart blocking: only medium severity and above are blocked
- User-friendly warnings for low-severity alerts

#### Groq AI-Powered Message Enhancement

- **Intelligent Risk Communication**
  - AI-enhanced fraud warnings using Groq LLaMA 3.3 70B model
  - Context-aware messages based on risk level and transaction details
  - User-friendly explanations instead of technical jargon
  - Actionable guidance for users on how to proceed safely
  - Multilingual support capability
  - Fallback to default messages if AI unavailable

#### DeepFace Biometric Verification

- **Facial Recognition Security**
  - Face registration during account setup
  - Face verification for high-risk transactions (risk score > 50%)
  - DeepFace library with multiple model options (VGG-Face, Facenet, OpenFace, DeepID, ArcFace, Dlib, SFace)
  - Real-time face matching with stored user profiles
  - Anti-spoofing measures
  - Secure face data storage in media/faces directory
  - Camera integration in Flutter app for seamless verification
  - Fallback mechanisms for camera unavailability



### Mobile Features

- **Beautiful UI**
  - Custom Instrument Sans typography
  - Intuitive navigation with go_router
  - Smooth animations and transitions
  - Material Design 3 components
  - Responsive layouts for all screen sizes
  - Dark/light theme support (planned)
- **Core Screens**
  - Dashboard with balance overview and quick actions
  - Transaction history with filtering and search
  - Send money interface with real-time risk assessment
  - Receipt generation with QR codes
  - Merchant payment scanning (QR code support)
  - Cash in/out operations
  - Settings management
  - Top shops and offers with promotions
- **Advanced UX Features**
  - Real-time fee calculation as you type
  - Risk indicators with color-coded alerts
  - Face verification camera integration
  - Informational dialogs for risk warnings (non-blocking)
  - Step-up authentication flow for high-risk transactions
  - Transaction preview with all costs shown upfront
  - Quick amount buttons (৳100, ৳500, ৳1000, ৳2000)
  - Contact integration for easy recipient selection
  - Offline-first capability with sync (planned)

---

## Tech Stack

### Backend

| Technology         | Purpose                         | Version |
| ------------------ | ------------------------------- | ------- |
| **FastAPI**  | Modern Python web framework     | 0.120.3 |
| **SQLModel** | Type-safe SQL database ORM      | 2.0.44  |
| **Supabase** | PostgreSQL database + real-time | 2.22.4  |
| **Pydantic** | Data validation                 | 2.12.3  |
| **JWT**      | Authentication tokens           | -       |
| **bcrypt**   | Password hashing                | 5.0.0   |
| **Uvicorn**  | ASGI server                     | 0.38.0  |
| **Alembic**  | Database migrations             | -       |
| **Pillow**   | Image processing                | Latest  |
| **httpx**    | Async HTTP client (Groq API)    | Latest  |

### Machine Learning & AI

| Technology             | Purpose                          | Version |
| ---------------------- | -------------------------------- | ------- |
| **XGBoost**      | Fraud detection classifier       | Latest  |
| **scikit-learn** | ML pipeline & preprocessing      | 1.6.1   |
| **pandas**       | Data manipulation                | Latest  |
| **numpy**        | Numerical computations           | Latest  |
| **joblib**       | Model serialization              | Latest  |
| **DeepFace**     | Face recognition & verification  | Latest  |
| **Groq SDK**     | AI message enhancement (LLaMA 3) | Latest  |
| **TensorFlow**   | Deep learning backend (DeepFace) | Latest  |

### Frontend

| Technology                       | Purpose                         | Version |
| -------------------------------- | ------------------------------- | ------- |
| **Flutter**                | Cross-platform mobile framework | 3.8.1   |
| **Dart**                   | Programming language            | 3.8.1+  |
| **Riverpod**               | State management                | 2.6.1   |
| **go_router**              | Navigation & routing            | 14.6.2  |
| **http**                   | API communication               | 1.2.2   |
| **flutter_secure_storage** | Secure token storage            | 9.0.0   |
| **image_picker**           | Camera integration for face verification | Latest |
| **intl**                   | Internationalization & formatting | Latest |

---

## Project Structure

```
TrustWallet/
├── backend/                          # FastAPI Backend
│   ├── main.py                      # Application entry point
│   ├── requirements.txt             # Python dependencies
│   ├── alembic.ini                  # Database migration config
│   ├── .env.example                 # Environment template
│   ├── media/                       # User-uploaded media
│   │   └── faces/                  # Face verification images (DeepFace)
│   ├── models/                      # Trained ML models
│   │   └── xgboost_pipeline_fraud.pkl
│   ├── alembic/                     # Database migrations
│   │   └── versions/
│   ├── scripts/                     # Training scripts
│   │   └── train_anomaly_model.py
│   └── src/
│       ├── __init__.py             # FastAPI app initialization
│       ├── config.py               # Configuration management
│       ├── auth/                   # Authentication services
│       │   └── auth_service.py
│       ├── models/                 # SQLModel database models
│       │   ├── user.py
│       │   ├── transaction.py
│       │   └── fraud_alert.py
│       ├── schemas/                # Pydantic validation schemas
│       │   ├── auth_schemas.py
│       │   ├── user_schemas.py
│       │   ├── transaction_schemas.py
│       │   ├── wallet_schemas.py
│       │   └── anomaly_schemas.py
│       ├── services/               # Business logic layer
│       │   ├── user_service.py
│       │   └── wallet_service.py
│       ├── users/                  # User endpoints
│       │   ├── user_routes.py
│       │   └── face_routes.py      # Face verification endpoints
│       ├── transactions/           # Transaction endpoints
│       │   └── transaction_routes.py
│       ├── admin/                  # Admin endpoints
│       │   └── admin_routes.py
│       └── utils/                  # Utility functions
│           ├── database.py
│           ├── password_utils.py
│           ├── nid_validator.py
│           ├── fraud_detector.py
│           ├── xgboost_fraud_detector.py
│           ├── autoencoder_model.py
│           ├── anomaly_model.py
│           ├── groq_message_enhancer.py  # Groq AI for enhanced messages
│           └── supabase_client.py
│
└── frontend/                         # Flutter Mobile App
    ├── pubspec.yaml                 # Flutter dependencies
    ├── analysis_options.yaml        # Dart analyzer config
    ├── assets/                      # App assets
    │   ├── images/
    │   └── fonts/
    │       └── Instrument_Sans/
    ├── lib/
    │   ├── main.dart               # App entry point
    │   └── src/
    │       ├── api.dart            # API endpoints configuration
    │       ├── app/                # App-level configuration
    │       │   ├── app.dart
    │       │   └── router.dart
    │       ├── core/               # Core utilities
    │       │   ├── theme.dart
    │       │   └── l10n.dart
    │       ├── mock/               # Mock data for development
    │       └── features/           # Feature modules
    │           ├── auth/           # Authentication screens
    │           │   ├── splash_screen.dart
    │           │   ├── onboarding_screen.dart
    │           │   ├── signin_screen.dart
    │           │   └── signup_screen.dart
    │           ├── dashboard/      # Home dashboard
    │           │   └── home_screen.dart
    │           ├── send/           # Send money flow
    │           │   ├── send_entry_screen.dart
    │           │   └── send_confirm_screen.dart
    │           ├── history/        # Transaction history
    │           │   └── history_screen.dart
    │           ├── receipt/        # Transaction receipts
    │           │   └── receipt_screen.dart
    │           ├── merchant/       # Merchant payments
    │           │   ├── scan_screen.dart
    │           │   ├── merchant_profile_screen.dart
    │           │   └── pay_confirm_screen.dart
    │           ├── cashin/         # Cash in operations
    │           │   └── cash_in_screen.dart
    │           ├── cashout/        # Cash out operations
    │           │   └── cash_out_screen.dart
    │           ├── offers/         # Offers and promotions
    │           │   └── top_shops_screen.dart
    │           └── settings/       # User settings
    │               └── settings_screen.dart
    ├── android/                    # Android-specific files
    ├── ios/                        # iOS-specific files
    ├── web/                        # Web support files
    ├── linux/                      # Linux desktop files
    ├── macos/                      # macOS files
    └── windows/                    # Windows files
```

---

## Getting Started

### Prerequisites

#### Backend Requirements

- Python 3.11 (recommended) or Python 3.9+
- pip (Python package manager)
- PostgreSQL (optional, SQLite included for development)
- Git

#### Frontend Requirements

- Flutter SDK 3.8.1 or higher
- Dart SDK 3.8.1 or higher
- Android Studio / Xcode (for mobile development)
- VS Code or Android Studio (recommended IDEs)

### Backend Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/TrustWallet.git
   cd TrustWallet/backend
   ```
2. **Create Virtual Environment**

   ```bash
   # Recommended: Use Python 3.11 for best compatibility
   py -3.11 -m venv venv

   # Alternative: Use default Python version
   # python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```
3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Configuration**

   ```bash
   # Copy the example environment file
   copy .env.example .env

   # Edit .env with your configuration
   # See Environment Configuration section for details
   ```
5. **Database Setup**

   **Option A: SQLite (Development)**

   ```bash
   # SQLite database is created automatically
   # Just run the application
   ```

   **Option B: Supabase (Recommended for Production)**

   ```bash
   # 1. Create a Supabase project at https://supabase.com
   # 2. Get your credentials from Project Settings > API
   # 3. Update .env with Supabase credentials
   # 4. Run migrations

   alembic upgrade head
   ```
6. **Train ML Models (Optional)**

   ```bash
   # Train the fraud detection model
   python scripts/train_anomaly_model.py

   # The model will be saved to models/xgboost_pipeline_fraud.pkl
   ```
7. **Run the Backend**

   ```bash
   python main.py
   ```

   The API will be available at:

   - Main API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
8. **Verify Setup**

   ```bash
   # Test the API
   curl http://localhost:8000/health

   # Expected response:
   # {"status":"healthy","timestamp":"...","service":"trustwallet-backend","version":"1.0.0"}
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**

   ```bash
   cd frontend
   ```
2. **Install Flutter Dependencies**

   ```bash
   flutter pub get
   ```
3. **Configure API Endpoint**

   ```dart
   // Edit lib/src/api.dart
   String BASE_URL_LOCAL = "http://YOUR_IP_ADDRESS:8000";

   // For Android Emulator use: http://10.0.2.2:8000
   // For iOS Simulator use: http://localhost:8000
   // For physical device use your computer's IP address
   ```
4. **Send Flow & Risk UX**

- On Send Entry, you can preview a transaction. Risk dialogs (high/medium) are informational and do not block navigation.
- On Confirm screen, if the backend risk score is > 50%, face verification is required before sending.
- Fees and VAT display on both Entry and Confirm screens.

4. **Check Flutter Setup**

   ```bash
   flutter doctor
   ```
5. **Run the App**

   ```bash
   # List available devices
   flutter devices

   # Run on connected device/emulator
   flutter run

   # Run on specific device
   flutter run -d <device_id>

   # Run in release mode
   flutter run --release
   ```
6. **Build APK (Android)**

   ```bash
   flutter build apk --release
   # APK will be at: build/app/outputs/flutter-apk/app-release.apk
   ```
7. **Build iOS App**

   ```bash
   flutter build ios --release
   # Open in Xcode for signing and deployment
   ```

---

## API Documentation

### Key Endpoints (Wallet)

- Preview send

  ```http
  POST /api/v1/wallet/preview-send
  Authorization: Bearer <jwt>
  Content-Type: application/json

  {
    "receiver_phone": "+8801712345678",
    "amount": 1000
  }
  ```

  Response

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
      "risk_score": 0.62,   // 0..1
      "threshold": 0.5,
      "can_proceed": true,
      "warnings": ["Moderate fraud risk detected"],
      "details": {}
    },
    "can_proceed": true
  }
  ```
- Confirm send

  ```http
  POST /api/v1/wallet/confirm-send
  Authorization: Bearer <jwt>
  Content-Type: application/json

  {
    "receiver_phone": "+8801712345678",
    "amount": 1000
  }
  ```

  - If risk score > 50%, the mobile app must perform face verification before calling this endpoint.
  - Server may still block for rule-based high severity or ML if configured.

---

## Fees & Charges

- **Transaction Fee**: ৳10 per ৳1000 (1.0%)
- **Service VAT**: ৳5 per ৳1000 (0.5%)
- **Total Deducted**: `amount + fee + vat`

Notes:

- The preview endpoint returns `fee`, `vat`, and `total_deducted` so the UI can display exact amounts.
- The confirm/send endpoint deducts the total from sender; receiver receives the base `amount`.

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

#### Register User

```http
POST /register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "nid": "1990123456789"
}
```

**Response (200)**

```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "full_name": "John Doe",
    "email": "john@example.com",
    "nid": "1990123456789",
    "wallet_balance": 0,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Login

```http
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (200)**

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "full_name": "John Doe",
    "email": "john@example.com",
    "wallet_balance": 5000.0
  }
}
```

### Wallet Operations

#### Get Balance

```http
GET /wallet
Authorization: Bearer <token>
```

**Response (200)**

```json
{
  "balance": 5000.0,
  "user_id": "uuid",
  "currency": "BDT"
}
```

#### Check Transaction Risk

```http
POST /wallet/check-risk
Authorization: Bearer <token>
Content-Type: application/json

{
  "receiver_email": "receiver@example.com",
  "amount": 75000.0
}
```

**Response (200)**

```json
{
  "is_risky": true,
  "risk_score": 0.85,
  "risk_level": "high",
  "warnings": [
    "High transaction amount detected",
    "Multiple recent high-value transactions"
  ],
  "can_proceed": false
}
```

#### Preview Transaction

```http
POST /wallet/preview-send
Authorization: Bearer <token>
Content-Type: application/json

{
  "receiver_email": "receiver@example.com",
  "amount": 1000.0
}
```

**Response (200)**

```json
{
  "sender": {
    "name": "John Doe",
    "email": "john@example.com",
    "current_balance": 5000.0
  },
  "receiver": {
    "name": "Jane Smith",
    "email": "receiver@example.com"
  },
  "amount": 1000.0,
  "fees": 0.0,
  "total_deducted": 1000.0,
  "new_balance": 4000.0,
  "estimated_time": "Instant",
  "risk_check": {
    "is_risky": false,
    "risk_score": 0.15,
    "risk_level": "low"
  }
}
```

#### Confirm Transaction

```http
POST /wallet/confirm-send
Authorization: Bearer <token>
Content-Type: application/json

{
  "receiver_email": "receiver@example.com",
  "amount": 1000.0,
  "preview_confirmed": true
}
```

**Response (200)**

```json
{
  "message": "Transaction completed successfully",
  "transaction": {
    "id": "uuid",
    "sender_id": "uuid",
    "receiver_id": "uuid",
    "amount": 1000.0,
    "status": "completed",
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "new_balance": 4000.0,
  "anomaly_warning": null
}
```

### Transaction History

#### Get Transactions

```http
GET /transactions?page=1&page_size=10
Authorization: Bearer <token>
```

**Response (200)**

```json
{
  "transactions": [
    {
      "id": "uuid",
      "sender_email": "john@example.com",
      "receiver_email": "receiver@example.com",
      "amount": 1000.0,
      "status": "completed",
      "timestamp": "2024-01-01T12:00:00Z",
      "description": "Money transfer"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

#### Get Transaction Details

```http
GET /transactions/{transaction_id}
Authorization: Bearer <token>
```

### Admin Endpoints

#### Get Fraud Alerts

```http
GET /admin/fraud-alerts?page=1&page_size=20
Authorization: Bearer <admin_token>
```

**Response (200)**

```json
{
  "alerts": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "user_email": "suspicious@example.com",
      "reason": "High-value transaction attempt",
      "timestamp": "2024-01-01T12:00:00Z",
      "severity": "high",
      "resolved": false
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

#### Add Funds to User

```http
POST /admin/users/{user_id}/add-funds?amount=5000
Authorization: Bearer <admin_token>
```

For complete API documentation, visit the interactive docs at `/docs` when running the backend.

---

## Security Features

### Authentication & Authorization

- **JWT Token Authentication**: Secure, stateless authentication
- **Token Expiration**: Configurable token lifetime (default: 60 minutes)
- **Password Security**: bcrypt hashing with salt rounds
- **Secure Storage**: Flutter Secure Storage for token management

### Biometric Security

- **DeepFace Integration**: State-of-the-art facial recognition
- **Face Registration**: User face captured and stored during signup
- **Face Verification**: Required for transactions with risk score > 50%
- **Multiple AI Models**: Support for VGG-Face, Facenet, ArcFace, OpenFace, DeepID, Dlib, SFace
- **Anti-Spoofing**: Liveness detection capabilities (planned)
- **Secure Storage**: Encrypted face data in isolated media directory

### Input Validation

- **Pydantic Schemas**: Type-safe request/response validation
- **NID Format Validation**: Multi-format Bangladesh NID support
- **Phone Number Validation**: Bangladesh phone format (+880/0 prefix validation)
- **Email Validation**: RFC-compliant email verification
- **Amount Validation**: Minimum/maximum transaction limits

### Fraud Prevention

- **Real-time Risk Assessment**: Every transaction is scored (0-100%)
- **Multi-layer Detection**: Rule-based + ML-based detection
- **Groq AI Enhancement**: Intelligent, context-aware risk messages using LLaMA 3.3 70B
- **Automatic Blocking**: High-risk transactions blocked instantly
- **Step-up Authentication**: Face verification for risk > 50%
- **Admin Alerts**: Suspicious activities flagged for review
- **Granular Severity**: 6-level severity system (critical to low)

### Data Protection

- **SQL Injection Prevention**: SQLModel parameterized queries
- **XSS Protection**: Input sanitization
- **CORS Configuration**: Restricted cross-origin access
- **Environment Variables**: Sensitive data never hardcoded
- **Secure Media Storage**: User images isolated with proper permissions

---

## Machine Learning Models

### XGBoost Fraud Detection

**Purpose**: Primary fraud detection using gradient boosting classifier

**Features Used**:

- **Transaction amount**: Amount being transferred
- **Transaction type**: PAYMENT, TRANSFER, CASH_OUT, CASH_IN, DEBIT
- **Payer debited**: Amount deducted from sender's balance
- **Receiver credited**: Amount credited to receiver's balance
- **Time features**: Hour of day, day of week, date
- **User types**: Payer type (Customer/Merchant), Receiver type (Customer/Merchant)

**Pipeline Components**:

1. **Preprocessing**:
   - Numeric features: StandardScaler for normalization
   - Categorical features: OneHotEncoder for encoding
   - Missing value imputation
2. **XGBoost Classifier**:
   - 400+ trees for robust prediction
   - Class weight balancing for imbalanced data
   - Optimized learning rate and tree depth
   - Cross-validation for hyperparameter tuning

**Model Performance**:

- ROC-AUC: ~0.95+
- Precision: High precision to minimize false positives
- Recall: Balanced to catch actual fraud
- Handles class imbalance effectively

**Model Location**: `backend/models/xgboost_pipeline_fraud.pkl`

**Real-time Prediction**:

```python
# The model returns:
{
  "isFraud": 0 or 1,
  "fraud_probability": 0.0 to 1.0
}
```

### Training Your Own Model

1. **Prepare Training Data**:

   The training script expects a `Fraud.csv` dataset with columns:

   - `type`, `amount`, `nameOrig`, `nameDest`
   - `oldbalanceOrg`, `newbalanceOrig`
   - `oldbalanceDest`, `newbalanceDest`
   - `isFraud` (target label)
   - `step` (time unit)
2. **Run Training Script**:

   ```bash
   cd backend/scripts
   python fraud_training.py
   ```

   The script will:

   - Load and clean the fraud dataset
   - Engineer features (debited/credited amounts, time features, user types)
   - Build preprocessing pipeline
   - Train XGBoost classifier
   - Save the complete pipeline
3. **Model Artifacts**:

   - `xgboost_pipeline_fraud.pkl`: Complete trained pipeline (preprocessor + classifier)
   - Training logs and performance metrics printed to console
   - Model ready for real-time predictions

### DeepFace Biometric System

**Purpose**: Facial recognition for user verification and high-risk transaction authentication

**Supported Models**:

- **VGG-Face**: Deep CNN trained on 2.6M images (default)
- **Facenet**: Google's triplet loss model
- **OpenFace**: Lightweight model for real-time processing
- **DeepID**: Multi-scale deep learning approach
- **ArcFace**: Additive angular margin loss for better discrimination
- **Dlib**: Classic computer vision approach
- **SFace**: Spherical face embedding

**Features**:

- **Face Registration**: 
  - User face captured during signup
  - Multiple face angles stored for robustness
  - Images stored in `media/faces/{user_id}/`
  
- **Face Verification**:
  - Real-time matching against stored profile
  - Cosine similarity threshold: 0.6 (adjustable)
  - Sub-second verification time
  - Automatic face detection and alignment
  
- **Security**:
  - Encrypted face data storage
  - No cloud storage - all on-premises
  - GDPR-compliant data handling
  - Face images isolated per user

**API Endpoints**:

```python
# Register face
POST /api/v1/users/register-face
Content-Type: multipart/form-data
File: face image (JPG/PNG)

# Verify face (for high-risk transactions)
POST /api/v1/users/verify-face
Content-Type: multipart/form-data
File: face image (JPG/PNG)
Authorization: Bearer <jwt_token>

Response: {"verified": true, "confidence": 0.95}
```

**Integration with Fraud Detection**:

- Automatically triggered when risk score > 50%
- Required before confirm-send endpoint
- Seamless mobile camera integration
- Fallback to OTP if face verification fails (planned)

### Groq AI Message Enhancement

**Purpose**: Transform technical fraud alerts into user-friendly, actionable messages

**Model**: LLaMA 3.3 70B Versatile (Groq's optimized inference)

**Features**:

- **Context-Aware Messages**:
  - Considers transaction amount, risk level, and severity
  - Adapts tone based on risk (informative vs urgent)
  - Provides specific next steps for users
  
- **Smart Fallback**:
  - Uses default messages if API unavailable
  - No blocking if Groq service down
  - Cached responses for common patterns
  
- **Performance**:
  - Ultra-fast response time (< 500ms)
  - Async processing doesn't block transactions
  - Rate limit aware (30 req/min free tier)

**Example Enhancement**:

```python
# Original: "Transaction flagged for review"
# Enhanced: "We've detected unusual activity on this transaction. 
#            For your security, please verify your identity with 
#            face recognition before proceeding. This helps protect 
#            your account from unauthorized access."
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nid VARCHAR(17) UNIQUE NOT NULL,
    wallet_balance DECIMAL(15, 2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table

```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID REFERENCES users(id),
    receiver_id UUID REFERENCES users(id),
    amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT positive_amount CHECK (amount > 0)
);
```

### Fraud Alerts Table

```sql
CREATE TABLE fraud_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    transaction_id UUID REFERENCES transactions(id),
    reason TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by UUID REFERENCES users(id)
);
```

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Environment Configuration

### Backend (.env)

```bash
# Database
DATABASE_URL=sqlite:///./wallet_app.db
# For Supabase: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# Supabase (Optional)
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=[YOUR_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[YOUR_SERVICE_ROLE_KEY]

# Security
SECRET_KEY=your-super-secret-key-min-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application
DEBUG=True
APP_NAME=TrustWallet MVP Backend
APP_VERSION=1.0.0

# CORS (comma-separated origins)
ALLOWED_ORIGINS=*
# Production: ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Fraud Detection
MAX_TRANSACTION_AMOUNT=100000
HIGH_VALUE_THRESHOLD=50000
HIGH_VALUE_TIME_WINDOW_MINUTES=5
MAX_HIGH_VALUE_TRANSACTIONS=3
BLOCK_ML_ANOMALY=False  # Set to True to block ML-detected fraud

# Groq AI (for enhanced risk messages)
GROQ_API_KEY=your-groq-api-key-here  # Get from https://console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_ENABLED=True  # Set to False to disable AI enhancement

# NID Validation
ENABLE_NID_API_VALIDATION=False

# Logging
LOG_LEVEL=INFO

# Media Storage
MEDIA_ROOT=./media
FACES_DIR=./media/faces
```

### Groq API Setup

1. **Get API Key**:
   - Visit [Groq Console](https://console.groq.com)
   - Sign up for free account
   - Generate API key from dashboard
   - Add to `.env` file

2. **Features**:
   - Free tier: 30 requests/minute
   - Models: LLaMA 3.3 70B, LLaMA 3.1 8B, Mixtral, Gemma
   - Ultra-fast inference (~500 tokens/second)

3. **Benefits**:
   - User-friendly fraud warnings instead of technical messages
   - Context-aware explanations based on transaction details
   - Multilingual capability
   - Actionable security advice

### Frontend (lib/src/api.dart)

```dart
// Development
String BASE_URL_LOCAL = "http://192.168.1.100:8000";

// Production
// String BASE_URL_LOCAL = "https://api.trustwallet.com";

// API Endpoints
final String login_endpoint = "$BASE_URL_LOCAL/api/v1/login";
final String register_endpoint = "$BASE_URL_LOCAL/api/v1/register";
final String profile_endpoint = "$BASE_URL_LOCAL/api/v1/profile";
final String wallet_endpoint = "$BASE_URL_LOCAL/api/v1/wallet";
final String preview_send_endpoint = "$BASE_URL_LOCAL/api/v1/wallet/preview-send";
final String confirm_send_endpoint = "$BASE_URL_LOCAL/api/v1/wallet/confirm-send";
final String verify_face_endpoint = "$BASE_URL_LOCAL/api/v1/users/verify-face";
final String register_face_endpoint = "$BASE_URL_LOCAL/api/v1/users/register-face";
```

---

## Send Money Flow (Complete Workflow)

### Step 1: Send Entry Screen

1. **User Input**:
   - Enter recipient phone number (Bangladesh format: +880 or 0)
   - Enter amount (with quick buttons: ৳100, ৳500, ৳1000, ৳2000)
   - Select payment method (wallet default)

2. **Real-time Validation**:
   - Phone number format check
   - Amount range validation (min: ৳1, max: ৳500,000)
   - Balance sufficiency check (client-side preview)

3. **Fee Calculation** (as you type):
   - Transaction Fee: ৳10 per ৳1000 (1.0%)
   - Service VAT: ৳5 per ৳1000 (0.5%)
   - Total Payable: amount + fee + VAT
   - Displayed in real-time fee summary

4. **Press Continue**:
   - Calls `POST /api/v1/wallet/preview-send`
   - Backend runs fraud checks (XGBoost + Rules)
   - Risk banner appears with score and level
   - Risk dialogs shown but don't block navigation

### Step 2: Risk Assessment & Dialogs

**Backend Processing**:

```python
# XGBoost ML prediction
risk_score = 0.62  # 0.0 to 1.0 (62%)
risk_level = "medium"  # low, medium, high

# Rule-based checks
severity = "medium-high"  # If velocity or high-value triggers
can_proceed = True  # Only block for medium+ severity

# Groq AI enhancement (if enabled)
enhanced_message = "We've detected moderate risk. For your security, 
                    you'll need to verify your face on the next screen."
```

**Frontend Dialogs**:

- **can_proceed=false**: "Transaction Flagged" → Shows warning but allows "Review & Continue"
- **risk_score > 50%**: "Face Verification Required" → Informational, user clicks Continue
- **high risk**: "High Risk Detected" → Informational alert with enhanced Groq message

**Key UX**: All dialogs are informational. User can always proceed to confirm screen.

### Step 3: Confirm Screen

1. **Display Summary**:
   - Recipient name and phone
   - Transaction amount (large, prominent)
   - Transaction Fee: ৳10
   - Service Fee (VAT): ৳5
   - Total Payable: ৳1,015
   - Date, time, payment type
   - Risk indicator with score badge

2. **Face Verification Gating** (if risk > 50%):
   ```dart
   if (risk_score > 50%) {
     // Show face verification banner
     "High risk detected (62%). Verify your face to proceed."
     
     // User clicks "Verify Face"
     // Opens front camera
     final image = await ImagePicker().pickImage(source: camera);
     
     // Calls POST /api/v1/users/verify-face
     // DeepFace compares with stored face
     final verified = response['verified'];  // true/false
     
     // If verified, enable Confirm button
     // If failed, show error and retry option
   }
   ```

3. **Press Confirm & Send**:
   - Calls `POST /api/v1/wallet/confirm-send`
   - Backend deducts total (amount + fee + VAT) from sender
   - Receiver gets base amount only
   - Creates transaction record
   - Returns success with transaction ID

4. **Success Dialog**:
   - Checkmark animation
   - "Transaction Successful!"
   - Amount and recipient shown
   - Transaction ID displayed
   - Any ML warnings (if non-blocking fraud detected)
   - Button to return to home

### Complete API Flow

```mermaid
sequenceDiagram
    participant User
    participant App
    participant Backend
    participant XGBoost
    participant Groq
    participant DeepFace

    User->>App: Enter phone & amount
    App->>App: Calculate fees (local)
    User->>App: Press Continue
    App->>Backend: POST /preview-send
    Backend->>XGBoost: Check fraud risk
    XGBoost-->>Backend: risk_score=0.62
    Backend->>Groq: Enhance message (if >50%)
    Groq-->>Backend: Enhanced warning
    Backend-->>App: Preview response + risk
    App->>User: Show risk dialogs (non-blocking)
    User->>App: Continue to confirm
    App->>User: Display summary
    
    alt Risk > 50%
        User->>App: Click Verify Face
        App->>User: Open camera
        User->>App: Capture face
        App->>Backend: POST /verify-face
        Backend->>DeepFace: Compare faces
        DeepFace-->>Backend: verified=true
        Backend-->>App: Success
        App->>User: Enable Confirm button
    end
    
    User->>App: Press Confirm & Send
    App->>Backend: POST /confirm-send
    Backend->>Backend: Deduct total from sender
    Backend->>Backend: Credit amount to receiver
    Backend-->>App: Transaction created
    App->>User: Success dialog
```

### Error Handling

- **Receiver not found**: 404 error, snackbar message
- **Insufficient balance**: 400 error, snackbar message
- **Face verification failed**: Retry option, or contact support
- **Network error**: Retry with exponential backoff
- **Server blocked (high severity)**: 409 Conflict, transaction blocked message

---

## Testing

### Backend Tests

#### Run All Tests

```bash
cd backend
python -m pytest
```

#### Test Specific Module

```bash
# Test user authentication
python -m pytest tests/test_auth.py

# Test transactions
python -m pytest tests/test_transactions.py

# Test fraud detection
python -m pytest tests/test_fraud_detection.py
```

#### Test XGBoost Model

```bash
python test_xgboost_model.py
```

#### Manual API Testing

```bash
# Start the server
python main.py

# Use interactive docs
# Navigate to: http://localhost:8000/docs
```

### Frontend Tests

#### Run Widget Tests

```bash
cd frontend
flutter test
```

#### Run Integration Tests

```bash
flutter test integration_test/
```

#### Test on Device

```bash
flutter run --debug
```

---
### Dataset

The project uses the [Fraudulent Transactions Data](https://www.kaggle.com/datasets/chitwanmanchanda/fraudulent-transactions-data) dataset from Kaggle
---
### Contributing

We welcome contributions to TrustWallet! To contribute, please follow these steps:

1. **Fork the repository**  
   Click the "Fork" button at the top-right of this page.

2. **Clone your fork**  `
   ```bash
   https://github.com/Mehedi26696/Trust-Wallet.git
   cd TrustWallet
3.Create a branch for your feature or bugfix
```
git checkout -b feature/your-feature-name
```
4.Make Your Changes

- Follow the existing code style to keep the project consistent.  
- Add tests for any new features or bug fixes to ensure stability.  
5. Commit and push your changes
  ```
  git add .
  git commit -m "Add description of changes"
  git push origin feature/your-feature-name
  ```
6. Open a Pull Request (PR)
- Describe the problem and your solution clearly.
- Reference any related issues with #issue_number.
- Wait for review and feedback.

### Reporting Bugs

When reporting bugs, please include:

1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Screenshots (if applicable)
5. Environment (OS, Python/Flutter version, etc.)

---
## License

This project is open source and licensed under the Apache License 2.0.

Copyright © 2025 DU_Genmorphix

You are free to use, modify, and distribute this software under the terms of the license.



---



<div align="center">

**Built for the Bangladesh digital payment ecosystem**

[Back to Top](#trustwallet---secure-digital-payment-service-platform)

</div>
