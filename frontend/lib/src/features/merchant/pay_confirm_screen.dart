import 'dart:math';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../mock/mock_services.dart'; // Merchant model

class PayConfirmScreen extends StatefulWidget {
  const PayConfirmScreen({super.key});

  @override
  State<PayConfirmScreen> createState() => _PayConfirmScreenState();
}

class _PayConfirmScreenState extends State<PayConfirmScreen> {
  final _bdt = NumberFormat.currency(
    locale: 'en_US',
    symbol: '৳',
    decimalDigits: 0,
  );

  bool _verifying = false;
  bool _otpPassed = false;

  bool _needsStepUp(String level, num amount) {
    final h = DateTime.now().hour;
    final lateNight = h <= 6 || h >= 23;
    return level == 'high' || amount > 10000 || lateNight;
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

  Future<void> _startStepUp(BuildContext context) async {
    final controller = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text(
          'Additional Verification',
          style: TextStyle(
            fontFamily: 'InstrumentSans',
            fontWeight: FontWeight.bold,
          ),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Enter the 6-digit code (demo: 123456).',
              style: TextStyle(fontFamily: 'InstrumentSans'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              keyboardType: TextInputType.number,
              maxLength: 6,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontFamily: 'InstrumentSans',
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 8,
              ),
              decoration: InputDecoration(
                counterText: '',
                hintText: '••••••',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (controller.text == '123456') Navigator.pop(context, true);
            },
            child: const Text('Verify'),
          ),
        ],
      ),
    );
    if (ok == true) {
      setState(() => _otpPassed = true);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Verification successful')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = GoRouterState.of(context);
    final data = (state.extra as Map?) ?? {};
    final Merchant m =
        (data['merchant'] as Merchant?) ?? MerchantService().byId('M001');
    final amount = num.tryParse((data['amount'] ?? '0').toString()) ?? 0;

    final fees = (data['fees'] as Map?) ?? {};
    final vat = (fees['vat'] ?? 0) as num;
    final fee = (fees['fee'] ?? 0) as num;
    final total = (fees['total'] ?? amount) as num;

    final risk = (data['risk'] as Map?) ?? const {};
    final level = (risk['level'] ?? 'low') as String;
    final score = (risk['score'] ?? 0).toString();
    final reason = (risk['reason'] ?? 'Normal') as String;

    final needsStepUp = _needsStepUp(level, amount);
    final now = DateTime.now();

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color.fromARGB(255, 151, 212, 255), // Sky blue at bottom
              Colors.white, // White at top
            ],
            begin: Alignment.bottomCenter,
            end: Alignment.topCenter,
          ),
        ),
        child: Scaffold(
          backgroundColor: Colors.transparent,
          appBar: AppBar(
            backgroundColor: Color.fromARGB(255, 2, 101, 250),
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => context.go('/merchant'),
            ),
            title: const Text(
              'Pay Merchant',
              style: TextStyle(
                fontFamily: 'InstrumentSans',
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Color.fromARGB(255, 245, 245, 245),
                letterSpacing: -0.1,
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => context.pop(),
                child: const Text(
                  'Edit',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Merchant header
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(.05),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 50,
                        height: 50,
                        decoration: BoxDecoration(
                          color: const Color(0xFFE3F2FD),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(
                          Icons.store,
                          color: Color(0xFF2196F3),
                          size: 26,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              m.name,
                              style: const TextStyle(
                                fontFamily: 'InstrumentSans',
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              m.address,
                              style: const TextStyle(
                                fontFamily: 'InstrumentSans',
                                fontSize: 12,
                                color: Color(0xFF626C7A),
                              ),
                            ),
                          ],
                        ),
                      ),
                      Row(
                        children: [
                          Icon(
                            m.verified
                                ? Icons.verified
                                : Icons.verified_outlined,
                            color: m.verified
                                ? const Color(0xFF4CAF50)
                                : const Color(0xFF9E9E9E),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            m.verified ? 'Verified' : 'Unverified',
                            style: TextStyle(
                              fontFamily: 'InstrumentSans',
                              fontWeight: FontWeight.w700,
                              color: m.verified
                                  ? const Color(0xFF4CAF50)
                                  : const Color(0xFF9E9E9E),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Amount & breakdown
                const Text(
                  'Transaction Details',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E1E1E),
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(.05),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Center(
                        child: Column(
                          children: [
                            const Text(
                              'Amount to Pay',
                              style: TextStyle(
                                fontFamily: 'InstrumentSans',
                                fontSize: 12,
                                color: Color(0xFF626C7A),
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _bdt.format(amount),
                              style: const TextStyle(
                                fontFamily: 'InstrumentSans',
                                fontSize: 36,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF2196F3),
                                letterSpacing: -1,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 20),
                      const Divider(),
                      const SizedBox(height: 12),
                      _Row(label: 'Transaction Fee', value: _bdt.format(fee)),
                      const SizedBox(height: 8),
                      _Row(label: 'Service Fee (VAT)', value: _bdt.format(vat)),
                      const SizedBox(height: 12),
                      const Divider(),
                      const SizedBox(height: 12),
                      _Row(
                        label: 'Final Payable',
                        value: _bdt.format(total),
                        boldValue: true,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Risk banner
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _riskBg(level),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _riskColor(level)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.shield, color: _riskColor(level)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '$reason — ($score)',
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontWeight: FontWeight.w700,
                            color: _riskColor(level),
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(999),
                          border: Border.all(color: _riskColor(level)),
                        ),
                        child: Text(level.toUpperCase()),
                      ),
                    ],
                  ),
                ),
                if (_needsStepUp(level, amount)) ...[
                  const SizedBox(height: 8),
                  const Text(
                    'Unusual activity detected. Additional verification required.',
                    style: TextStyle(color: Color(0xFFE65100)),
                  ),
                ],

                const SizedBox(height: 28),

                // Confirm CTA
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2196F3),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    onPressed: _verifying
                        ? null
                        : () async {
                            final needs = _needsStepUp(level, amount);
                            if (needs && !_otpPassed) {
                              await _startStepUp(context);
                              if (!_otpPassed) return;
                            }
                            setState(() => _verifying = true);
                            await Future.delayed(
                              const Duration(milliseconds: 1200),
                            );

                            final txnId =
                                'TW-${Random().nextInt(999999).toString().padLeft(6, '0')}';

                            if (context.mounted) {
                              context.go(
                                '/receipt',
                                extra: {
                                  'txnId': txnId,
                                  'phone': m.phone, // merchant receive number
                                  'amount': amount.toStringAsFixed(0),
                                  'fees': fees,
                                  'risk': risk,
                                  'final': total,
                                  'timestamp': DateTime.now().toIso8601String(),
                                },
                              );
                            }
                          },
                    child: _verifying
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text(
                            'Confirm Payment',
                            style: TextStyle(
                              fontFamily: 'InstrumentSans',
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                              letterSpacing: -0.5,
                            ),
                          ),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'No real money moves in this demo.',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 12,
                    color: Color(0xFF9E9E9E),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  final String label;
  final String value;
  final bool boldValue;
  const _Row({
    required this.label,
    required this.value,
    this.boldValue = false,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 14,
              color: Color(0xFF626C7A),
              fontWeight: FontWeight.w500,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: boldValue ? 18 : 16,
              fontWeight: boldValue ? FontWeight.w800 : FontWeight.w700,
              color: const Color(0xFF1E1E1E),
            ),
          ),
        ],
      ),
    );
  }
}
