// lib/src/features/send/send_entry_screen.dart
import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:http/http.dart' as http;
import 'package:trustwallet_frontend/src/api.dart';
import '../../mock/mock_services.dart';

class SendEntryScreen extends StatefulWidget {
  const SendEntryScreen({super.key});
  @override
  State<SendEntryScreen> createState() => _SendEntryScreenState();
}

class _SendEntryScreenState extends State<SendEntryScreen> {
  // --- Controllers & services ---
  final _phoneController = TextEditingController();
  final _amountController = TextEditingController(text: '500');

  final risk = RiskService();
  final fees = FeeService();

  // --- Debounce timer for smooth UX ---
  Timer? _debounce;

  final _bdt = NumberFormat.currency(
    locale: 'en_US',
    symbol: '৳',
    decimalDigits: 0,
  );

  // --- State ---
  bool _isLoading = false;
  Map<String, dynamic> riskData = const {
    'level': 'low',
    'score': 12,
    'reason': 'Normal transaction',
  };
  bool _riskVisible = false;

  Map<String, num> feeData = const {'vat': 0, 'fee': 0, 'total': 0};

  // Backend preview data
  Map<String, dynamic>? _previewData;

  // Limits to keep demo safe
  static const num _minAmount = 1;
  static const num _maxAmount = 500000;

  // --- Helpers ---
  void _triggerRecalc() {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 600), _recalculate);
  }

  void _recalculate() {
    final amount = _parseAmount(_amountController.text);
    final clamped = amount.clamp(_minAmount, _maxAmount);

    // keep field value in sync if user typed crazy-big negative etc.
    if (clamped != amount) {
      _amountController.text = clamped.toStringAsFixed(0);
      _amountController.selection = TextSelection.fromPosition(
        TextPosition(offset: _amountController.text.length),
      );
    }

    // Always update fees locally
    setState(() {
      feeData = fees.quote(clamped);
    });

    // Only hit backend when inputs are valid and user paused typing
    if (!_isPhoneValid || !_isAmountValid) {
      setState(() {
        riskData = {
          'level': 'low',
          'score': 0,
          'reason': 'Enter receiver and amount',
        };
        _riskVisible = false;
      });
      return;
    }

    // Fetch risk from backend; fallback to mock on error
    _fetchRiskFromBackend(_sanitizePhone(_phoneController.text), clamped);
  }

  Future<void> _fetchRiskFromBackend(String phone, num amount) async {
    try {
      final resp = await http.post(
        Uri.parse(check_risk_endpoint),
        headers: {
          'Content-Type': 'application/json',
          if (authToken != null) 'Authorization': 'Bearer $authToken',
        },
        body: jsonEncode({'receiver_phone': phone, 'amount': amount}),
      );

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        final level = (data['risk_level'] ?? 'low') as String;
        final score01 = (data['risk_score'] ?? 0.0) as num; // 0..1
        final warnings =
            (data['warnings'] as List?)?.cast<dynamic>() ?? const [];
        final reason = warnings.isNotEmpty
            ? warnings.first.toString()
            : (level == 'high' ? 'High fraud risk detected' : 'Normal');

        setState(() {
          riskData = {
            'level': level,
            'score': (score01 * 100).toStringAsFixed(1), // Show one decimal
            'reason': reason,
          };
        });
        return;
      }
    } catch (_) {
      // ignore, will fallback
    }

    // Fallback to local mock if backend unavailable
    setState(() {
      riskData = risk.score(phone, amount);
      _riskVisible = false;
    });
  }

  num _parseAmount(String raw) {
    // Remove non-digits
    final clean = raw.replaceAll(RegExp(r'[^0-9]'), '');
    if (clean.isEmpty) return 0;
    return num.tryParse(clean) ?? 0;
  }

  String _sanitizePhone(String raw) {
    // Keep digits and plus; trims spaces
    return raw.replaceAll(RegExp(r'[^\d\+]'), '').trim();
  }

  bool get _isPhoneValid {
    final p = _sanitizePhone(_phoneController.text);
    // Accept: +8801XXXXXXXXX (11 digits) or 01XXXXXXXXX (11 digits)
    if (p.isEmpty) return false;
    // Remove +880 or 0 prefix and check if we have 10 digits
    final cleaned = p
        .replaceAll(RegExp(r'^\+?880'), '')
        .replaceAll(RegExp(r'^0'), '');
    return cleaned.length == 10 && cleaned.startsWith('1');
  }

  bool get _isAmountValid {
    final a = _parseAmount(_amountController.text);
    return a >= _minAmount && a <= _maxAmount;
  }

  Color _riskColor(String level) {
    switch (level) {
      case 'high':
        return const Color(0xFFD32F2F);
      case 'medium':
        return const Color(0xFFE65100);
      default:
        return const Color(0xFF2E7D32);
    }
  }

  Color _riskBg(String level) {
    switch (level) {
      case 'high':
        return const Color(0xFFFFEBEE);
      case 'medium':
        return const Color(0xFFFFF3E0);
      default:
        return const Color(0xFFE8F5E9);
    }
  }

  @override
  void initState() {
    super.initState();
    _recalculate();
    _amountController.addListener(_triggerRecalc);
    _phoneController.addListener(_triggerRecalc);
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _phoneController.dispose();
    _amountController.dispose();
    super.dispose();
  }

  // ---------------- UI ----------------
  @override
  Widget build(BuildContext context) {
    // Everything below matches your current frontend layout/styles.
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        backgroundColor: Color.fromARGB(255, 2, 101, 250),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => context.go('/home'),
        ),
        title: const Text(
          'Send Money',
          style: TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Color.fromARGB(255, 245, 245, 245),
            letterSpacing: -0.1,
          ),
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Recipient Phone Number
              const Text(
                'Recipient Number',
                style: TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  letterSpacing: -0.1,
                  color: Color(0xFF1E1E1E),
                ),
              ),
              const SizedBox(height: 8),
              Container(
                decoration: BoxDecoration(
                  color: const Color.fromARGB(255, 75, 133, 167),
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: TextField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  style: const TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF1E1E1E),
                  ),
                  decoration: InputDecoration(
                    hintText: '+8801XXXXXXXX',
                    hintStyle: const TextStyle(
                      fontFamily: 'InstrumentSans',
                      color: Color.fromARGB(255, 194, 212, 245),
                    ),
                    prefixIcon: const Icon(
                      Icons.phone_rounded,
                      color: Color(0xFF2196F3),
                    ),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _isPhoneValid ? Icons.check_circle : Icons.contacts,
                        color: _isPhoneValid
                            ? const Color(0xFF2E7D32)
                            : const Color(0xFF626C7A),
                      ),
                      onPressed: () {
                        // Open contacts (stub)
                      },
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: Colors.white,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 16,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Amount
              const Text(
                'Amount',
                style: TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF1E1E1E),
                ),
              ),
              const SizedBox(height: 8),
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(left: 16),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: const Color.fromARGB(255, 255, 255, 255),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'Tk',
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2196F3),
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: TextField(
                        controller: _amountController,
                        keyboardType: TextInputType.number,
                        style: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E1E1E),
                        ),
                        decoration: InputDecoration(
                          hintText: '0',
                          hintStyle: const TextStyle(
                            fontFamily: 'InstrumentSans',
                            color: Color(0xFF9E9E9E),
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide.none,
                          ),
                          filled: true,
                          fillColor: Colors.white,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 16,
                          ),
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.refresh, color: Color(0xFF626C7A)),
                      onPressed: () {
                        _amountController.text = '';
                        _triggerRecalc();
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),

              // Quick Amount Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _QuickAmountButton(
                    amount: '৳100',
                    onTap: () => _amountController.text = '100',
                  ),
                  _QuickAmountButton(
                    amount: '৳500',
                    onTap: () => _amountController.text = '500',
                  ),
                  _QuickAmountButton(
                    amount: '৳1000',
                    onTap: () => _amountController.text = '1000',
                  ),
                  _QuickAmountButton(
                    amount: '৳2000',
                    onTap: () => _amountController.text = '2000',
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Payment Method (static stub)
              const Text(
                'Payment Method',
                style: TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF1E1E1E),
                ),
              ),
              const SizedBox(height: 8),
              GestureDetector(
                onTap: () {
                  // Show payment method selector
                  showModalBottomSheet(
                    context: context,
                    shape: const RoundedRectangleBorder(
                      borderRadius: BorderRadius.vertical(
                        top: Radius.circular(20),
                      ),
                    ),
                    builder: (context) => Container(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            'Select Payment Method',
                            style: TextStyle(
                              fontFamily: 'InstrumentSans',
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 20),
                          ListTile(
                            leading: Container(
                              width: 40,
                              height: 40,
                              decoration: BoxDecoration(
                                color: const Color(0xFFE3F2FD),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Icon(
                                Icons.account_balance_wallet,
                                color: Color(0xFF2196F3),
                                size: 20,
                              ),
                            ),
                            title: const Text('My Wallet'),
                            trailing: const Icon(
                              Icons.check_circle,
                              color: Color(0xFF2196F3),
                            ),
                            onTap: () => Navigator.pop(context),
                          ),
                        ],
                      ),
                    ),
                  );
                },
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.05),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: const Color(0xFFE3F2FD),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(
                          Icons.account_balance_wallet,
                          color: Color(0xFF2196F3),
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Text(
                          'My Wallet',
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF1E1E1E),
                          ),
                        ),
                      ),
                      const Icon(
                        Icons.keyboard_arrow_down,
                        color: Color(0xFF626C7A),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // --- Risk Banner (only after user presses Continue) ---
              if (_riskVisible) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _riskBg(riskData['level'] as String),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: _riskColor(riskData['level'] as String),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.security,
                        color: _riskColor(riskData['level'] as String),
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '${riskData['reason']} — (${riskData['score']})',
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 12,
                            color: _riskColor(riskData['level'] as String),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // --- Fee Summary ---
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFF5F5F5),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    _FeeRow(
                      label: 'Transaction Fee',
                      amount: _bdt.format(feeData['fee'] ?? 0),
                    ),
                    const SizedBox(height: 8),
                    _FeeRow(
                      label: 'Service Fee (VAT)',
                      amount: _bdt.format(feeData['vat'] ?? 0),
                    ),
                    const Divider(height: 24),
                    _FeeRow(
                      label: 'Total Amount',
                      amount: _bdt.format(feeData['total'] ?? 0),
                      isBold: true,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // Continue Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor:
                        (_isPhoneValid && _isAmountValid && !_isLoading)
                        ? const Color(0xFF2196F3)
                        : Colors.grey,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: (_isPhoneValid && _isAmountValid && !_isLoading)
                      ? () async {
                          // Call backend preview API
                          setState(() => _isLoading = true);

                          try {
                            final amountValue = _parseAmount(
                              _amountController.text,
                            ).toDouble();

                            final response = await http.post(
                              Uri.parse(preview_send_endpoint),
                              headers: {
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer $authToken',
                              },
                              body: jsonEncode({
                                'receiver_phone': _sanitizePhone(
                                  _phoneController.text,
                                ),
                                'amount': amountValue,
                              }),
                            );

                            if (!mounted) return;

                            if (response.statusCode == 200) {
                              final data = jsonDecode(response.body);
                              _previewData = data;

                              // Update risk data from backend
                              final riskCheck = data['risk_check'];
                              final riskScore =
                                  (riskCheck['risk_score'] ?? 0.0) as num;
                              final riskDetails = riskCheck['details'] ?? {};
                              final biometricsRequired = riskDetails['biometrics_required'] == true;
                              final faceEnrolled = riskDetails['face_enrolled'] == true;

                              final backendFee = (data['fee'] as num?) ?? 0;
                              final backendVat = (data['vat'] as num?) ?? 0;
                              final backendTotal =
                                  (data['total_deducted'] as num?) ??
                                  (amountValue + backendFee + backendVat);
                              setState(() {
                                riskData = {
                                  'level': riskCheck['risk_level'],
                                  'score': (riskScore * 100).toStringAsFixed(1),
                                  'reason': riskCheck['warnings'].isEmpty
                                      ? 'Normal transaction'
                                      : riskCheck['warnings'][0],
                                  'biometrics_required': biometricsRequired,
                                  'face_enrolled': faceEnrolled,
                                };
                                feeData = {
                                  'vat': backendVat,
                                  'fee': backendFee,
                                  'total': backendTotal,
                                };
                                _riskVisible =
                                    true; // show banner only after continue
                              });

                              // If backend says cannot proceed, warn but still allow moving to confirm (server will enforce on final send)
                              if (!riskCheck['can_proceed']) {
                                if (mounted) {
                                  await showDialog<void>(
                                    context: context,
                                    builder: (_) => AlertDialog(
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(16),
                                      ),
                                      title: const Text(
                                        'Transaction Flagged',
                                        style: TextStyle(
                                          fontFamily: 'InstrumentSans',
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      content: Text(
                                        riskCheck['warnings'].join('\n'),
                                        style: const TextStyle(
                                          fontFamily: 'InstrumentSans',
                                        ),
                                      ),
                                      actions: [
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(
                                              0xFF2196F3,
                                            ),
                                          ),
                                          onPressed: () =>
                                              Navigator.pop(context),
                                          child: const Text(
                                            'Review & Continue',
                                            style: TextStyle(
                                              fontFamily: 'InstrumentSans',
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                }
                                // Continue to confirm screen; final send will be blocked if server enforces
                              }

                              // If high risk or biometrics required, show warning

                              if (riskCheck['risk_level'] == 'high' || biometricsRequired) {
                                if (mounted) {
                                  await showDialog<void>(
                                    context: context,
                                    builder: (_) => AlertDialog(
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(16),
                                      ),
                                      title: Text(
                                        biometricsRequired
                                            ? (faceEnrolled ? 'Face Verification Required' : 'Setup Face ID Required')
                                            : 'High Risk Detected',
                                        style: const TextStyle(
                                          fontFamily: 'InstrumentSans',
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      content: Text(
                                        biometricsRequired
                                            ? (faceEnrolled 
                                                ? '${riskCheck['warnings'].join('\n')}\n\nYou will need to verify your face on the next screen to complete this transaction.'
                                                : '${riskCheck['warnings'].join('\n')}\n\nYou haven\'t set up Face ID yet. You will need to enroll your face on the next screen to proceed with this high-value transfer.')
                                            : riskCheck['warnings'].join('\n'),
                                        style: const TextStyle(
                                          fontFamily: 'InstrumentSans',
                                        ),
                                      ),
                                      actions: [
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(
                                              0xFF2196F3,
                                            ),
                                          ),
                                          onPressed: () => Navigator.pop(context),
                                          child: const Text(
                                            'Continue',
                                            style: TextStyle(
                                              fontFamily: 'InstrumentSans',
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                }
                                // Do not block; continue to confirm where face verification/enrollment is enforced
                              }

                              // Navigate to confirmation screen with preview data
                              if (mounted) {
                                context.push(
                                  '/send/confirm',
                                  extra: {
                                    'phone': _sanitizePhone(
                                      _phoneController.text,
                                    ),
                                    'amount': _parseAmount(
                                      _amountController.text,
                                    ).toStringAsFixed(0),
                                    'receiverName': data['receiver_name'],
                                    'fees': feeData,
                                    'risk': riskData,
                                    'previewData': _previewData,
                                  },
                                );
                              }
                            } else if (response.statusCode == 404) {
                              if (mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Receiver not found'),
                                    backgroundColor: Colors.red,
                                  ),
                                );
                              }
                            } else if (response.statusCode == 400) {
                              final error = jsonDecode(response.body);
                              if (mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      error['detail'] ?? 'Invalid request',
                                    ),
                                    backgroundColor: Colors.red,
                                  ),
                                );
                              }
                            } else {
                              if (mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text(
                                      'Failed to preview transaction',
                                    ),
                                    backgroundColor: Colors.red,
                                  ),
                                );
                              }
                            }
                          } catch (e) {
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Error: ${e.toString()}'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          } finally {
                            if (mounted) {
                              setState(() => _isLoading = false);
                            }
                          }
                        }
                      : null,
                  child: _isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Text(
                          'Continue',
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                            letterSpacing: -0.5,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}

// Quick Amount Button Widget
class _QuickAmountButton extends StatelessWidget {
  final String amount;
  final VoidCallback onTap;
  const _QuickAmountButton({required this.amount, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFE0E0E0)),
        ),
        child: Text(
          amount,
          style: const TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: Color(0xFF2196F3),
          ),
        ),
      ),
    );
  }
}

// Fee Row Widget
class _FeeRow extends StatelessWidget {
  final String label;
  final String amount;
  final bool isBold;
  const _FeeRow({
    required this.label,
    required this.amount,
    this.isBold = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: isBold ? 16 : 14,
            fontWeight: isBold ? FontWeight.bold : FontWeight.w500,
            color: const Color(0xFF626C7A),
          ),
        ),
        Text(
          amount,
          style: TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: isBold ? 18 : 16,
            fontWeight: isBold ? FontWeight.bold : FontWeight.w700,
            color: const Color(0xFF1E1E1E),
          ),
        ),
      ],
    );
  }
}
