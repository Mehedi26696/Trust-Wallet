// lib/src/features/merchant/merchant_profile_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../mock/mock_services.dart'; // MerchantService, FeeService, RiskService

class MerchantProfileScreen extends StatefulWidget {
  const MerchantProfileScreen({super.key});

  @override
  State<MerchantProfileScreen> createState() => _MerchantProfileScreenState();
}

class _MerchantProfileScreenState extends State<MerchantProfileScreen> {
  final _amount = TextEditingController(text: '500');
  final fs = FeeService();
  final rs = RiskService();
  final bdt = NumberFormat.currency(
    locale: 'en_US',
    symbol: '৳',
    decimalDigits: 0,
  );

  Map<String, num> fee = const {'vat': 0, 'fee': 0, 'total': 0};
  Map<String, dynamic> risk = const {
    'level': 'low',
    'score': 12,
    'reason': 'Normal',
  };

  @override
  void initState() {
    super.initState();
    _recalc();
    _amount.addListener(_recalc);
  }

  @override
  void dispose() {
    _amount.dispose();
    super.dispose();
  }

  void _recalc() {
    final a = num.tryParse(_amount.text.replaceAll(RegExp(r'[^0-9]'), '')) ?? 0;
    setState(() {
      fee = fs.quote(a);
      risk = rs.score(
        'merchant',
        a,
      ); // using amount only; merchant number reputation is mocked
    });
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
  Widget build(BuildContext context) {
    final state = GoRouterState.of(context);
    final data = (state.extra as Map?) ?? {};
    // If only id was passed, you could fetch with MerchantService().byId(id)
    final Merchant m =
        (data['merchant'] as Merchant?) ?? MerchantService().byId('M001');

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color.fromARGB(255, 177, 220, 252), // Sky blue at bottom
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
            centerTitle: true,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => context.go('/scan'),
            ),
            title: const Text(
              'Merchant',
              style: TextStyle(
                fontFamily: 'InstrumentSans',
                fontSize: 22,
                fontWeight: FontWeight.w500,
                color: Colors.white,
                letterSpacing: -1,
              ),
            ),
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header card
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

                // Offers
                if (m.offers.isNotEmpty) ...[
                  const Text(
                    'Offers',
                    style: TextStyle(
                      fontFamily: 'InstrumentSans',
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: m.offers
                        .map(
                          (o) => Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: const Color(0xFFE3F2FD),
                              borderRadius: BorderRadius.circular(999),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.local_offer,
                                  size: 16,
                                  color: Color.fromARGB(255, 36, 39, 41),
                                ),
                                const SizedBox(width: 6),
                                Text(
                                  '${o.title}  •  ${o.tag}',
                                  style: const TextStyle(
                                    fontFamily: 'InstrumentSans',
                                    fontWeight: FontWeight.w700,
                                    color: Color.fromARGB(255, 41, 43, 44),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        )
                        .toList(),
                  ),
                  const SizedBox(height: 16),
                ],

                // Amount entry
                const Text(
                  'Enter amount',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
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
                      const SizedBox(width: 12),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE3F2FD),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          '৳',
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF2196F3),
                          ),
                        ),
                      ),
                      Expanded(
                        child: TextField(
                          controller: _amount,
                          keyboardType: TextInputType.number,
                          decoration: InputDecoration(
                            hintText: '0',
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
                          style: const TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1E1E1E),
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(
                          Icons.refresh,
                          color: Color(0xFF626C7A),
                        ),
                        onPressed: () => _amount.text = '',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),

                // Risk banner
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _riskBg(risk['level'] as String),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: _riskColor(risk['level'] as String),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.security,
                        color: _riskColor(risk['level'] as String),
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '${risk['reason']} — (${risk['score']})',
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 12,
                            color: _riskColor(risk['level'] as String),
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),

                // Fee box
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF5F5F5),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      _feeRow('Transaction Fee', bdt.format(fee['fee'] ?? 0)),
                      const SizedBox(height: 8),
                      _feeRow('Service Fee (VAT)', bdt.format(fee['vat'] ?? 0)),
                      const Divider(height: 24),
                      _feeRow(
                        'Total Amount',
                        bdt.format(fee['total'] ?? 0),
                        bold: true,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Pay CTA
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color.fromARGB(255, 0, 99, 247),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                    ),
                    onPressed: () {
                      final amount =
                          num.tryParse(
                            _amount.text.replaceAll(RegExp(r'[^0-9]'), ''),
                          ) ??
                          0;
                      if (amount <= 0) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Enter a valid amount')),
                        );
                        return;
                      }

                      // Reuse your existing SendConfirmScreen to keep consistent UX
                      context.go(
                        '/pay/confirm',
                        extra: {
                          'phone': m.phone, // pay to merchant phone
                          'amount': amount.toStringAsFixed(0),
                          'fees': fee,
                          'risk': risk,
                        },
                      );
                    },
                    child: const Text(
                      'Pay Now',
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

                
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _feeRow(String label, String value, {bool bold = false}) => Row(
    mainAxisAlignment: MainAxisAlignment.spaceBetween,
    children: [
      Text(
        label,
        style: TextStyle(
          fontFamily: 'InstrumentSans',
          fontSize: bold ? 16 : 14,
          fontWeight: bold ? FontWeight.bold : FontWeight.w500,
          color: const Color(0xFF626C7A),
        ),
      ),
      Text(
        value,
        style: TextStyle(
          fontFamily: 'InstrumentSans',
          fontSize: bold ? 18 : 16,
          fontWeight: bold ? FontWeight.bold : FontWeight.w700,
          color: const Color(0xFF1E1E1E),
        ),
      ),
    ],
  );
}
