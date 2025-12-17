import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../api.dart';
import '../../core/widgets/rounded_navbar.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final int _tab = 3; // Settings tab index

  void _handleLogout() {
    // Clear token
    authToken = null;
    // Navigate to Sign In
    context.go('/signin');
  }

  @override
  Widget build(BuildContext context) {
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
          centerTitle: true,
          title: const Text(
            'Settings',
            style: TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 22,
              fontWeight: FontWeight.w500,
              color: Colors.white,
              letterSpacing: -1,
            ),
          ),
          automaticallyImplyLeading: false,
        ),
        body: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Account',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF626C7A),
                    letterSpacing: -1,
                  ),
                ),
                const SizedBox(height: 12),
                _SettingsTile(
                  icon: Icons.person_outline_rounded,
                  title: 'Profile Info',
                  onTap: () => context.go('/profile'),
                ),
                const SizedBox(height: 12),
                _SettingsTile(
                  icon: Icons.lock_outline_rounded,
                  title: 'Change Password',
                  onTap: () {
                    // TODO: Implement Change Password
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Change Password coming soon')),
                    );
                  },
                ),
                const SizedBox(height: 24),
                const Text(
                  'General',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF626C7A),
                    letterSpacing: -1,
                  ),
                ),
                const SizedBox(height: 12),
                _SettingsTile(
                  icon: Icons.notifications_none_rounded,
                  title: 'Notifications',
                  onTap: () {},
                ),
                 const SizedBox(height: 12),
                _SettingsTile(
                  icon: Icons.language,
                  title: 'Language',
                  onTap: () {},
                ),
                const SizedBox(height: 12),
                _SettingsTile(
                  icon: Icons.description_outlined,
                  title: 'Terms & Conditions',
                  onTap: () {},
                ),
                const SizedBox(height: 12),
                _SettingsTile(
                  icon: Icons.privacy_tip_outlined,
                  title: 'Privacy Policy',
                  onTap: () {},
                ),
                const SizedBox(height: 32),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _handleLogout,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFFFEBEE),
                      foregroundColor: const Color(0xFFD32F2F),
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    icon: const Icon(Icons.logout_rounded),
                    label: const Text(
                      'Log Out',
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        letterSpacing: -1,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        bottomNavigationBar: RoundedNavBar(
          currentIndex: _tab,
          onTap: (i) {
            if (i == _tab) return;
            if (i == 0) context.go('/home');
            if (i == 1) context.go('/history');
            if (i == 2) context.go('/scan');
          },
        ),
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _SettingsTile({
    required this.icon,
    required this.title,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(icon, color: const Color(0xFF2196F3), size: 24),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: Color(0xFF1E1E1E),
                  letterSpacing: -1,
                ),
              ),
            ),
            const Icon(
              Icons.chevron_right_rounded,
              color: Color(0xFF626C7A),
            ),
          ],
        ),
      ),
    );
  }
}
