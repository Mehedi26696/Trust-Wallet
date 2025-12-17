import 'package:flutter/material.dart';

class VerifiedBadge extends StatelessWidget {
  final bool verified;
  const VerifiedBadge({super.key, required this.verified});

  @override
  Widget build(BuildContext context) {
    final color = verified ? Colors.green : Colors.grey;
    final text  = verified ? 'Verified' : 'Unverified';
    return Row(children: [
      Icon(verified ? Icons.verified : Icons.verified_outlined, color: color, size: 18),
      const SizedBox(width: 6),
      Text(text, style: TextStyle(color: color, fontWeight: FontWeight.w600)),
    ]);
  }
}
