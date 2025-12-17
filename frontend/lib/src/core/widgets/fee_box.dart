import 'package:flutter/material.dart';

class FeeBox extends StatelessWidget {
  final num vat, fee, total;
  const FeeBox({super.key, required this.vat, required this.fee, required this.total});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(top: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          _row('VAT', vat),
          _row('Service fee', fee),
          const Divider(),
          _row('মোট পরিশোধ', total, isBold: true),
        ]),
      ),
    );
  }

  Widget _row(String label, num value, {bool isBold=false}) => Row(
    mainAxisAlignment: MainAxisAlignment.spaceBetween,
    children: [
      Text(label, style: TextStyle(fontWeight: isBold? FontWeight.w700: FontWeight.w500)),
      Text('৳${value.toStringAsFixed(0)}', style: TextStyle(fontWeight: isBold? FontWeight.w700: FontWeight.w600)),
    ],
  );
}
