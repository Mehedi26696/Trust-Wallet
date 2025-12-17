# TrustWallet Frontend (Flutter)

Flutter mobile app for TrustWallet with send flow, risk checks, and face verification.

## Run

```bash
flutter pub get
flutter run
```

Configure API base URL in `lib/src/api.dart`:

```dart
// For emulator/simulator or device
String BASE_URL_LOCAL = "http://YOUR_IP_OR_10.0.2.2:8000";
```

## Send Flow

- Entry screen: enter recipient phone and amount, then Continue to preview.
- Risk banner/dialogs are informational; navigation proceeds to Confirm.
- Confirm screen: if risk score > 50%, face verification is required before sending.
- Backend may block for high severity rule checks even after confirm.

## Fees & Totals

- Transaction Fee: ৳10 per ৳1000 (1.0%)
- Service VAT: ৳5 per ৳1000 (0.5%)
- Total Payable = `amount + fee + vat`

The preview API returns `fee`, `vat`, and `total_deducted`. The UI displays fees on Entry and Confirm screens.
