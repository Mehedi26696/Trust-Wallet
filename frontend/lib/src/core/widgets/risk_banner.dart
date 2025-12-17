import 'package:flutter/material.dart';

class RiskBanner extends StatelessWidget {
  final String level, text; final int score;
  const RiskBanner({super.key, required this.level, required this.text, required this.score});

  @override
  Widget build(BuildContext context) {
    final color = level=='high' ? Colors.red :
                  level=='medium' ? Colors.orange : Colors.green;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: color.withOpacity(.12), borderRadius: BorderRadius.circular(12)),
      child: Row(children: [
        Icon(Icons.shield, color: color),
        const SizedBox(width: 8),
        Expanded(child: Text('$text — ($score)', style: TextStyle(color: color, fontWeight: FontWeight.w600))),
      ]),
    );
  }
}
