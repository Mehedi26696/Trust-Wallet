// lib/src/core/widgets/rounded_navbar.dart
import 'package:flutter/material.dart';

class RoundedNavBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;

  const RoundedNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      top: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(0, 0, 0, 0),
        child: Container(
          decoration: BoxDecoration(
           
            boxShadow: [
              BoxShadow(
                color: const Color.fromARGB(255, 29, 115, 243).withOpacity(0.1),
                blurRadius: 10,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: BottomNavigationBar(
              currentIndex: currentIndex,
              onTap: onTap,
              backgroundColor: const Color.fromARGB(255, 245, 245, 245),
              type: BottomNavigationBarType.fixed,
              selectedItemColor: const Color.fromARGB(255, 255, 255, 255),
              unselectedItemColor: const Color.fromARGB(255, 141, 141, 141),
              showSelectedLabels: false,
              showUnselectedLabels: false,
              items: [
                _buildNavItem(Icons.home_rounded, 'Home', 0),
                _buildNavItem(Icons.history, 'History', 1),
                _buildNavItem(Icons.qr_code_scanner, 'Scan', 2),
                _buildNavItem(Icons.settings_rounded, 'Settings', 3),
              ],
            ),
          ),
        ),
      ),
    );
  }

  BottomNavigationBarItem _buildNavItem(
    IconData icon,
    String label,
    int index,
  ) {
    final isSelected = currentIndex == index;
    return BottomNavigationBarItem(
      icon: Container(
        padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 9),
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFF2196F3)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(28),
        ),
        child: Icon(icon),
      ),
      label: label,
    );
  }
}
