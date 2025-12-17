// lib/src/features/send/send_confirm_screen.dart
import 'dart:math';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:http/http.dart' as http;
import '../../api.dart';
import 'package:image_picker/image_picker.dart';

class SendConfirmScreen extends StatefulWidget {
  const SendConfirmScreen({super.key});

  @override
  State<SendConfirmScreen> createState() => _SendConfirmScreenState();
}

class _SendConfirmScreenState extends State<SendConfirmScreen> {
  final _bdt = NumberFormat.currency(
    locale: 'en_US',
    symbol: '৳',
    decimalDigits: 0,
  );

  bool _verifying = false;
  bool _faceVerified = false;

  Future<void> _verifyFaceNow() async {
    final picker = ImagePicker();
    final img = await picker.pickImage(
      source: ImageSource.camera,
      preferredCameraDevice: CameraDevice.front,
      imageQuality: 85,
    );
    if (img == null) return;

    try {
      final req = http.MultipartRequest(
        'POST',
        Uri.parse(verify_face_endpoint),
      );
      req.headers['Authorization'] = 'Bearer $authToken';
      req.files.add(
        await http.MultipartFile.fromPath(
          'file',
          img.path,
          filename: 'verify.jpg',
        ),
      );
      final resp = await req.send();
      if (resp.statusCode == 200) {
        final body = await resp.stream.bytesToString();
        final json = jsonDecode(body) as Map<String, dynamic>;
        final ok = json['verified'] == true;
        setState(() => _faceVerified = ok);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(ok ? 'Face verified' : 'Face verification failed'),
            backgroundColor: ok ? const Color(0xFF4CAF50) : Colors.red,
          ),
        );
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Face verification failed'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Error during face verification'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  // Simple anomaly rule for demo
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

  // Removed OTP step-up flow; face verification is the only step-up.

  @override
  Widget build(BuildContext context) {
    // Access extras sent from SendEntryScreen
    final state = GoRouterState.of(context);
    final data = (state.extra as Map?) ?? {};
    final phone = (data['phone'] ?? '') as String;
    final amountStr = (data['amount'] ?? '0') as String;
    final amount = num.tryParse(amountStr) ?? 0;
    final receiverName = (data['receiverName'] ?? 'Unknown') as String;

    final fees = (data['fees'] as Map?) ?? {};
    final vat = (fees['vat'] ?? 0) as num;
    final fee = (fees['fee'] ?? 0) as num;
    final total = (fees['total'] ?? amount) as num;

    final risk = (data['risk'] as Map?) ?? const {};
    final level = (risk['level'] ?? 'low') as String;
    final score = (risk['score'] ?? 0).toString();
    final reason = (risk['reason'] ?? 'Normal') as String;

    final previewData = data['previewData'] as Map<String, dynamic>?;

    final needsStepUp = _needsStepUp(level, amount);
    final now = DateTime.now();
    final timeFormat = DateFormat('hh:mm a');

    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FA),
      appBar: AppBar(
        backgroundColor: const Color.fromARGB(255, 22, 80, 240),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF1E1E1E)),
          onPressed: () => context.go('/send'),
        ),
        title: const Text(
          'Review & Confirm',
          style: TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Color.fromARGB(255, 255, 255, 255),
          ),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Recipient Card
            Container(
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
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF2196F3), Color(0xFF1976D2)],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.person,
                      color: Colors.white,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          receiverName,
                          style: const TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1E1E1E),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          phone,
                          style: const TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 12,
                            color: Color(0xFF626C7A),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Transaction Details
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
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Amount Display - Large
                  Center(
                    child: Column(
                      children: [
                        const Text(
                          'Transaction Amount',
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
                  _DetailRow(label: 'Transaction Fee', value: _bdt.format(fee)),
                  const SizedBox(height: 8),
                  _DetailRow(
                    label: 'Service Fee (VAT)',
                    value: _bdt.format(vat),
                  ),
                  const SizedBox(height: 12),
                  const Divider(),
                  const SizedBox(height: 12),
                  _DetailRow(
                    label: 'Total Payable',
                    value: _bdt.format(total),
                    isBold: true,
                    valueColor: const Color(0xFF1E1E1E),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Additional Info
            const Text(
              'Additional Info',
              style: TextStyle(
                fontFamily: 'InstrumentSans',
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1E1E1E),
              ),
            ),
            const SizedBox(height: 12),
            Container(
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
              child: Column(
                children: [
                  _InfoRow(
                    icon: Icons.access_time,
                    label: 'Time',
                    value: DateFormat('hh:mm a').format(now),
                  ),
                  const Divider(height: 24),
                  _InfoRow(
                    icon: Icons.calendar_today,
                    label: 'Date',
                    value: DateFormat('dd MMM yyyy').format(now),
                  ),
                  const Divider(height: 24),
                  const _InfoRow(
                    icon: Icons.payment,
                    label: 'Payment Type',
                    value: 'Instant Transfer',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Risk
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
                        color: _riskColor(level),
                        fontWeight: FontWeight.w700,
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
            if (needsStepUp) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF3E0),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE65100)),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.warning_amber_rounded,
                      color: Color(0xFFE65100),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Unusual activity detected. Please verify your face to continue.',
                        style: const TextStyle(color: Color(0xFFE65100)),
                      ),
                    ),
                    if (!_faceVerified)
                      TextButton(
                        onPressed: _verifyFaceNow,
                        style: TextButton.styleFrom(
                          foregroundColor: Colors.white,
                          backgroundColor: const Color(0xFF1976D2),
                        ),
                        child: const Text('Verify Face'),
                      )
                    else
                      const Icon(Icons.verified, color: Color(0xFF4CAF50)),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 28),

            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Color(0xFF2196F3)),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    onPressed: _verifying ? null : () => context.pop(),
                    child: const Text(
                      'Go Back',
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF2196F3),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
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
                            // High-risk face verification (required)
                            if (needsStepUp && !_faceVerified) {
                              final picker = ImagePicker();
                              final img = await picker.pickImage(
                                source: ImageSource.camera,
                                preferredCameraDevice: CameraDevice.front,
                                imageQuality: 85,
                              );
                              if (img == null) {
                                if (mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text(
                                        'Face verification required',
                                      ),
                                      backgroundColor: Colors.red,
                                    ),
                                  );
                                }
                                return;
                              }
                              try {
                                final req = http.MultipartRequest(
                                  'POST',
                                  Uri.parse(verify_face_endpoint),
                                );
                                req.headers['Authorization'] =
                                    'Bearer $authToken';
                                req.files.add(
                                  await http.MultipartFile.fromPath(
                                    'file',
                                    img.path,
                                    filename: 'verify.jpg',
                                  ),
                                );
                                final resp = await req.send();
                                if (resp.statusCode == 200) {
                                  final body = await resp.stream
                                      .bytesToString();
                                  final json =
                                      jsonDecode(body) as Map<String, dynamic>;
                                  setState(
                                    () => _faceVerified =
                                        json['verified'] == true,
                                  );
                                  if (!_faceVerified) {
                                    if (mounted) {
                                      ScaffoldMessenger.of(
                                        context,
                                      ).showSnackBar(
                                        const SnackBar(
                                          content: Text(
                                            'Face verification failed',
                                          ),
                                          backgroundColor: Colors.red,
                                        ),
                                      );
                                    }
                                    return;
                                  }
                                } else {
                                  if (mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text(
                                          'Face verification failed',
                                        ),
                                        backgroundColor: Colors.red,
                                      ),
                                    );
                                  }
                                  return;
                                }
                              } catch (_) {
                                if (mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text(
                                        'Error during face verification',
                                      ),
                                      backgroundColor: Colors.red,
                                    ),
                                  );
                                }
                                return;
                              }
                            }

                            setState(() => _verifying = true);

                            try {
                              // Call backend confirm-send API
                              final response = await http.post(
                                Uri.parse(confirm_send_endpoint),
                                headers: {
                                  'Content-Type': 'application/json',
                                  'Authorization': 'Bearer $authToken',
                                },
                                body: jsonEncode({
                                  'receiver_phone': phone,
                                  'amount': double.parse(amountStr),
                                }),
                              );

                              if (!mounted) return;

                              if (response.statusCode == 201) {
                                final result = jsonDecode(response.body);
                                final transaction = result['transaction'];
                                final txnId = transaction['id'];

                                // Show success and navigate to home
                                await showDialog(
                                  context: context,
                                  barrierDismissible: false,
                                  builder: (_) => AlertDialog(
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(16),
                                    ),
                                    content: Column(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Container(
                                          width: 60,
                                          height: 60,
                                          decoration: BoxDecoration(
                                            color: const Color(0xFF4CAF50),
                                            borderRadius: BorderRadius.circular(
                                              30,
                                            ),
                                          ),
                                          child: const Icon(
                                            Icons.check,
                                            color: Colors.white,
                                            size: 40,
                                          ),
                                        ),
                                        const SizedBox(height: 16),
                                        const Text(
                                          'Transaction Successful!',
                                          style: TextStyle(
                                            fontFamily: 'InstrumentSans',
                                            fontSize: 18,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          '৳${amountStr} sent to $receiverName',
                                          style: const TextStyle(
                                            fontFamily: 'InstrumentSans',
                                            color: Color(0xFF626C7A),
                                          ),
                                          textAlign: TextAlign.center,
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          'Transaction ID: ${txnId.toString().substring(0, 8)}...',
                                          style: const TextStyle(
                                            fontFamily: 'InstrumentSans',
                                            fontSize: 12,
                                            color: Color(0xFF9E9E9E),
                                          ),
                                        ),
                                        if (result['warning'] != null) ...[
                                          const SizedBox(height: 12),
                                          Container(
                                            padding: const EdgeInsets.all(8),
                                            decoration: BoxDecoration(
                                              color: const Color(0xFFFFF3E0),
                                              borderRadius:
                                                  BorderRadius.circular(8),
                                            ),
                                            child: Row(
                                              children: [
                                                const Icon(
                                                  Icons.warning_amber,
                                                  color: Color(0xFFE65100),
                                                  size: 16,
                                                ),
                                                const SizedBox(width: 8),
                                                Expanded(
                                                  child: Text(
                                                    result['warning']['reason'],
                                                    style: const TextStyle(
                                                      fontFamily:
                                                          'InstrumentSans',
                                                      fontSize: 11,
                                                      color: Color(0xFFE65100),
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                                    actions: [
                                      ElevatedButton(
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: const Color(
                                            0xFF2196F3,
                                          ),
                                          shape: RoundedRectangleBorder(
                                            borderRadius: BorderRadius.circular(
                                              8,
                                            ),
                                          ),
                                        ),
                                        onPressed: () {
                                          Navigator.pop(context);
                                          context.go('/home');
                                        },
                                        child: const Text(
                                          'Done',
                                          style: TextStyle(
                                            fontFamily: 'InstrumentSans',
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                );
                              } else if (response.statusCode == 409) {
                                // Transaction blocked by ML
                                final error = jsonDecode(response.body);
                                final warning = error['detail']['warning'];
                                if (mounted) {
                                  showDialog(
                                    context: context,
                                    builder: (_) => AlertDialog(
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(16),
                                      ),
                                      title: const Text(
                                        'Transaction Blocked',
                                        style: TextStyle(
                                          fontFamily: 'InstrumentSans',
                                          fontWeight: FontWeight.bold,
                                          color: Color(0xFFD32F2F),
                                        ),
                                      ),
                                      content: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          const Icon(
                                            Icons.block,
                                            color: Color(0xFFD32F2F),
                                            size: 48,
                                          ),
                                          const SizedBox(height: 16),
                                          Text(
                                            warning['reason'],
                                            style: const TextStyle(
                                              fontFamily: 'InstrumentSans',
                                            ),
                                            textAlign: TextAlign.center,
                                          ),
                                        ],
                                      ),
                                      actions: [
                                        ElevatedButton(
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: const Color(
                                              0xFF2196F3,
                                            ),
                                          ),
                                          onPressed: () {
                                            Navigator.pop(context);
                                            context.go('/home');
                                          },
                                          child: const Text(
                                            'OK',
                                            style: TextStyle(
                                              fontFamily: 'InstrumentSans',
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                }
                              } else {
                                final error = jsonDecode(response.body);
                                if (mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        error['detail'] ?? 'Transaction failed',
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
                                setState(() => _verifying = false);
                              }
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
                            'Confirm & Send',
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
              ],
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}

// Detail Row Widget
class _DetailRow extends StatelessWidget {
  final String label;
  final String value;
  final bool isBold;
  final Color? valueColor;

  const _DetailRow({
    required this.label,
    required this.value,
    this.isBold = false,
    this.valueColor,
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
            fontWeight: isBold ? FontWeight.bold : FontWeight.w400,
            color: const Color(0xFF626C7A),
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: isBold ? 18 : 16,
            fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
            color: valueColor ?? const Color(0xFF1E1E1E),
          ),
        ),
      ],
    );
  }
}

// Info Row Widget
class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFFE3F2FD),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: const Color(0xFF2196F3), size: 18),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: const TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 14,
              color: Color(0xFF626C7A),
            ),
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: Color(0xFF1E1E1E),
          ),
        ),
      ],
    );
  }
}
