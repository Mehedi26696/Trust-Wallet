import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

class ReceiptScreen extends StatelessWidget {
  const ReceiptScreen({super.key});

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

    final txnId = (data['txnId'] ?? 'TW-000000') as String;
    final phone = (data['phone'] ?? '') as String;

    // numeric values
    final amount = num.tryParse((data['amount'] ?? '0').toString()) ?? 0;
    final total = (data['final'] ?? amount) as num;

    final fees = (data['fees'] as Map?) ?? {};
    final vat = (fees['vat'] ?? 0) as num;
    final fee = (fees['fee'] ?? 0) as num;

    final risk = (data['risk'] as Map?) ?? const {};
    final level = (risk['level'] ?? 'low') as String;
    final score = (risk['score'] ?? 0).toString();
    final reason = (risk['reason'] ?? 'Normal') as String;

    // time
    final timestamp =
        DateTime.tryParse(
          (data['timestamp'] ?? DateTime.now().toIso8601String()) as String,
        ) ??
        DateTime.now();
    final timeStr = DateFormat('hh:mm a').format(timestamp);
    final dateStr = DateFormat('dd MMM yyyy').format(timestamp);

    final bdt = NumberFormat.currency(
      locale: 'en_US',
      symbol: '৳',
      decimalDigits: 0,
    );

    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
          colors: [Color.fromARGB(255, 151, 212, 255), Colors.white],
        ),
      ),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: const Color.fromARGB(255, 2, 101, 250),
          elevation: 0,
          leading: IconButton(
            icon: const Icon(
              Icons.close,
              color: Color.fromARGB(255, 245, 245, 245),
            ),
            onPressed: () => context.go('/home'),
          ),
          title: const Text(
            'Payment Receipt',
            style: TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: Color.fromARGB(255, 245, 245, 245),
            ),
          ),
          actions: [
            IconButton(
              tooltip: 'Copy Txn ID',
              icon: const Icon(
                Icons.copy,
                color: Color.fromARGB(255, 245, 245, 245),
              ),
              onPressed: () async {
                await Clipboard.setData(ClipboardData(text: txnId));
                // ignore: use_build_context_synchronously
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Transaction ID copied')),
                );
              },
            ),
          ],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Success header
              Container(
                padding: const EdgeInsets.symmetric(
                  vertical: 18,
                  horizontal: 16,
                ),
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
                  children: const [
                    _SuccessIcon(),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Transaction Successful',
                        style: TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF1E1E1E),
                        ),
                      ),
                    ),
                    Icon(Icons.check_circle, color: Color(0xFF4CAF50)),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Amount card
              _Card(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const Text(
                      'Final Paid',
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 12,
                        color: Color(0xFF626C7A),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      bdt.format(total),
                      style: const TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 36,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF2196F3),
                        letterSpacing: -1,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _Pill(text: 'Txn: $txnId'),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Recipient & meta
              _Card(
                child: Column(
                  children: [
                    _Row(label: 'Recipient', value: phone, boldValue: true),
                    const Divider(height: 24),
                    _Row(label: 'Date', value: dateStr),
                    const SizedBox(height: 6),
                    _Row(label: 'Time', value: timeStr),
                    const SizedBox(height: 6),
                    const _Row(
                      label: 'Payment Type',
                      value: 'Instant Transfer',
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Fees & breakdown
              _Card(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _Row(
                      label: 'Amount',
                      value: bdt.format(amount),
                      boldValue: true,
                    ),
                    const Divider(),
                    _Row(label: 'Transaction Fee', value: bdt.format(fee)),
                    _Row(label: 'Service Fee (VAT)', value: bdt.format(vat)),
                    const SizedBox(height: 6),
                    const Divider(),
                    _Row(
                      label: 'Total Paid',
                      value: bdt.format(total),
                      boldValue: true,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Risk summary
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _riskBg(level),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _riskColor(level)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(.03),
                      blurRadius: 8,
                      offset: const Offset(0, 3),
                    ),
                  ],
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
                    _Badge(
                      label: level.toUpperCase(),
                      color: _riskColor(level),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Actions
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFF2196F3)),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      icon: const Icon(
                        Icons.ios_share,
                        color: Color(0xFF2196F3),
                      ),
                      label: const Text(
                        'Share Receipt',
                        style: TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF2196F3),
                        ),
                      ),
                      onPressed: () {
                        // Mock share; no extra deps
                        showModalBottomSheet(
                          context: context,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                          builder: (_) => _ShareSheet(
                            txnId: txnId,
                            amount: bdt.format(total),
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFFEF5350)),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      icon: const Icon(
                        Icons.report_gmailerrorred,
                        color: Color(0xFFEF5350),
                      ),
                      label: const Text(
                        'Report/Block',
                        style: TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontWeight: FontWeight.w600,
                          color: Color(0xFFEF5350),
                        ),
                      ),
                      onPressed: () {
                        // If you have a report screen, navigate there; else show toast
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Report flow (demo)')),
                        );
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2196F3),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  icon: const Icon(Icons.home, color: Colors.white),
                  label: const Text(
                    'Back to Home',
                    style: TextStyle(
                      fontFamily: 'InstrumentSans',
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                      letterSpacing: -0.5,
                    ),
                  ),
                  onPressed: () => context.go('/home'),
                ),
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}

class _Card extends StatelessWidget {
  final Widget child;
  const _Card({required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
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
      child: child,
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

class _Badge extends StatelessWidget {
  final String label;
  final Color color;
  const _Badge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: color),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontFamily: 'InstrumentSans',
          fontWeight: FontWeight.w700,
          color: color,
        ),
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  final String text;
  const _Pill({required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFFE3F2FD),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        text,
        style: const TextStyle(
          fontFamily: 'InstrumentSans',
          fontWeight: FontWeight.w700,
          color: Color(0xFF2196F3),
          fontSize: 12,
        ),
      ),
    );
  }
}

class _SuccessIcon extends StatelessWidget {
  const _SuccessIcon({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 46,
      height: 46,
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5E9),
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Icon(Icons.check, color: Color(0xFF4CAF50)),
    );
  }
}

class _ShareSheet extends StatelessWidget {
  final String txnId;
  final String amount;
  const _ShareSheet({super.key, required this.txnId, required this.amount});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 18, 16, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              height: 4,
              width: 44,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(999),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Share Receipt (Demo)',
              style: TextStyle(
                fontFamily: 'InstrumentSans',
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Amount: $amount\nTxn ID: $txnId',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Saved to gallery (mock)'),
                        ),
                      );
                    },
                    icon: const Icon(Icons.download),
                    label: const Text('Save'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2196F3),
                    ),
                    onPressed: () {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Shared (mock)')),
                      );
                    },
                    icon: const Icon(Icons.ios_share, color: Colors.white),
                    label: const Text(
                      'Share',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
