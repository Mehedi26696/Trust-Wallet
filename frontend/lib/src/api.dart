String BASE_URL_LOCAL = "http://172.30.32.83:8000";

// Auth endpoints
String login_endpoint = BASE_URL_LOCAL + "/api/v1/login";
String signup_endpoint = BASE_URL_LOCAL + "/api/v1/register";

// User profile endpoint
String profile_endpoint = BASE_URL_LOCAL + "/api/v1/me";

// Wallet endpoints
String wallet_balance_endpoint = BASE_URL_LOCAL + "/api/v1/wallet";

// Transaction endpoints
String transactions_endpoint = BASE_URL_LOCAL + "/api/v1/transactions";
String transaction_detail_endpoint = BASE_URL_LOCAL + "/api/v1/transactions";
String check_risk_endpoint = BASE_URL_LOCAL + "/api/v1/wallet/check-risk";
String preview_send_endpoint = BASE_URL_LOCAL + "/api/v1/wallet/preview-send";
String confirm_send_endpoint = BASE_URL_LOCAL + "/api/v1/wallet/confirm-send";
String send_money_endpoint = BASE_URL_LOCAL + "/api/v1/wallet/send";

// Face endpoints
String enroll_face_endpoint = BASE_URL_LOCAL + "/api/v1/face/enroll";
String verify_face_endpoint = BASE_URL_LOCAL + "/api/v1/face/verify";

// Chat endpoints
String chat_endpoint = BASE_URL_LOCAL + "/api/v1/chat";
String chat_health_endpoint = BASE_URL_LOCAL + "/api/v1/health";
String chat_session_endpoint = BASE_URL_LOCAL + "/api/v1/session";

String? authToken;
Map<String, String> authHeaders() => {
  'Accept': 'application/json',
  if (authToken != null) 'Authorization': 'Bearer $authToken',
};
