// lib/src/features/merchant/scan_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../mock/mock_services.dart';
import '../../core/widgets/rounded_navbar.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final ms = MerchantService();
  final int _tab = 2; // Scan tab index

  @override
  Widget build(BuildContext context) {
    final merchants = ms.list();

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
            centerTitle: true,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => context.go('/home'),
            ),
            title: const Text(
              'Pay Merchant',
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
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Info Banner
                Container(
                  padding: const EdgeInsets.all(16),

                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Select a merchant to pay',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 22,
                            fontWeight: FontWeight.w100,
                            letterSpacing: -1,
                            color: Color(0xFF1E1E1E),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                const Text(
                  'Available Merchants',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 18,
                    fontWeight: FontWeight.w200,
                    letterSpacing: -1,
                    color: Color(0xFF1E1E1E),
                  ),
                ),
                const SizedBox(height: 12),

                ...merchants.map(
                  (m) => _MerchantTile(
                    merchant: m,
                    onTap: () {
                      context.go('/merchant', extra: {'merchant': m});
                    },
                  ),
                ),
              ],
            ),
          ),
          bottomNavigationBar: RoundedNavBar(
            currentIndex: _tab,
            onTap: (i) {
              if (i == _tab) return;
              if (i == 0) context.go('/home');
              if (i == 1) context.go('/history');
              if (i == 3) context.go('/settings');
            },
          ),
        ),
      ),
    );
  }
}

class _MerchantTile extends StatelessWidget {
  final Merchant merchant;
  final VoidCallback onTap;
  const _MerchantTile({required this.merchant, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Color(0xFF2196F3).withOpacity(0.3), width: 1.5),
      ),
      child: ListTile(
        onTap: onTap,
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: const Color.fromARGB(255, 255, 255, 255),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Icon(Icons.store, color: Color(0xFF2196F3)),
        ),
        title: Text(
          merchant.name,
          style: const TextStyle(
            fontFamily: 'InstrumentSans',
            fontWeight: FontWeight.w700,
          ),
        ),
        subtitle: Text(
          merchant.address,
          style: const TextStyle(
            fontFamily: 'InstrumentSans',
            color: Color(0xFF626C7A),
          ),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              merchant.verified ? Icons.verified : Icons.verified_outlined,
              color: merchant.verified
                  ? const Color(0xFF4CAF50)
                  : const Color(0xFF9E9E9E),
            ),
            const Icon(Icons.chevron_right),
          ],
        ),
      ),
    );
  }
}
