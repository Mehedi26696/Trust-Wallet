// lib/src/features/dashboard/home_screen.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import '../../core/widgets/rounded_navbar.dart';
import '../../api.dart';

const kPrimary = Color(0xFF2196F3);
const kPrimaryDark = Color(0xFF1976D2);
const kSurface = Color(0xFFF8F9FA);
const kText = Color(0xFF1E1E1E);
const kSubtle = Color(0xFF626C7A);

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tab = 0;

  // Data from API
  String userName = 'Loading...';
  String userId = ''; // Store current user ID
  double balance = 0.0;
  List<dynamic> transactions = [];
  bool isLoading = true;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (authToken == null) {
      setState(() {
        errorMessage = 'Not logged in';
        isLoading = false;
      });
      // Redirect to login
      WidgetsBinding.instance.addPostFrameCallback((_) {
        context.go('/signin');
      });
      return;
    }

    try {
      // Fetch user profile
      final profileResponse = await http.get(
        Uri.parse(profile_endpoint),
        headers: authHeaders(),
      );

      if (profileResponse.statusCode == 200) {
        final profileData = jsonDecode(profileResponse.body);
        setState(() {
          userName = profileData['full_name'] ?? 'User';
          userId = profileData['id'] ?? ''; // Store user ID
        });
      }

      // Fetch wallet balance
      final balanceResponse = await http.get(
        Uri.parse(wallet_balance_endpoint),
        headers: authHeaders(),
      );

      if (balanceResponse.statusCode == 200) {
        final balanceData = jsonDecode(balanceResponse.body);
        setState(() {
          balance = (balanceData['balance'] ?? 0.0).toDouble();
        });
      }

      // Fetch recent transactions
      final txResponse = await http.get(
        Uri.parse('$transactions_endpoint?page=1&page_size=4'),
        headers: authHeaders(),
      );

      if (txResponse.statusCode == 200) {
        final txData = jsonDecode(txResponse.body);
        print('Parsed Data: $txData');
        print('Items: ${txData['items']}');

        setState(() {
          transactions = txData['items'] ?? [];
          isLoading = false;
        });
      } else {
        setState(() {
          isLoading = false;
          errorMessage = 'Failed to load transactions';
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = 'Network error: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (errorMessage != null) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(errorMessage!),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadData,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

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
        body: SafeArea(
          child: RefreshIndicator(
            onRefresh: _loadData,
            child: CustomScrollView(
              slivers: [
                SliverToBoxAdapter(child: _Header()),
                const SliverToBoxAdapter(child: SizedBox(height: 16)),
                SliverToBoxAdapter(child: _Greeting(userName: userName)),
                const SliverToBoxAdapter(child: SizedBox(height: 16)),
                SliverToBoxAdapter(child: _BalanceCard(balance: balance)),
                const SliverToBoxAdapter(child: SizedBox(height: 16)),
                SliverToBoxAdapter(child: _QuickButtons()),
                const SliverToBoxAdapter(child: SizedBox(height: 12)),
                SliverToBoxAdapter(child: _AlertStrip()),
                const SliverToBoxAdapter(child: SizedBox(height: 24)),
                SliverToBoxAdapter(
                  child: _TransactionHistory(
                    transactions: transactions,
                    currentUserId: userId,
                  ),
                ),
                const SliverToBoxAdapter(child: SizedBox(height: 24)),
              ],
            ),
          ),
        ),
        bottomNavigationBar: RoundedNavBar(
          currentIndex: _tab,
          onTap: (i) {
            setState(() => _tab = i);
            if (i == 0) return;
            if (i == 1) context.go('/history');
            if (i == 2) context.go('/scan');
            if (i == 3) context.go('/settings');
          },
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Image.asset(
            'assets/images/logo1.png',
            height: 32,
            errorBuilder: (_, __, ___) => Container(
              height: 32,
              width: 32,
              decoration: const BoxDecoration(
                color: kPrimary,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.account_balance_wallet,
                color: Colors.white,
                size: 18,
              ),
            ),
          ),
          Row(
            children: [
              IconButton(
                onPressed: () => context.go('/chat'),
                icon: const Icon(
                  Icons.chat_bubble_outline_rounded,
                  color: kText,
                ),
              ),
              const SizedBox(width: 8),
              InkWell(
                onTap: () => context.go('/profile'),
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      colors: [kPrimary, kPrimaryDark],
                    ),
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                  child: const Icon(Icons.person, color: Colors.white, size: 20),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Greeting extends StatelessWidget {
  final String userName;

  const _Greeting({required this.userName});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Hi, $userName',
            style: const TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: kText,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
        ],
      ),
    );
  }
}

class _BalanceCard extends StatelessWidget {
  final double balance;

  const _BalanceCard({required this.balance});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Container(
        height: 120,
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [
              Color.fromARGB(255, 49, 85, 248),
              Color.fromARGB(255, 77, 160, 243),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(.08),
              blurRadius: 16,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Total Balance',
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        color: Colors.white70,
                        letterSpacing: -1,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '৳${balance.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontFamily: 'InstrumentSans',
                        color: Colors.white,
                        fontSize: 26,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.5,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: IconButton(
                  onPressed: () => context.go('/cashin'),
                  icon: const Icon(Icons.add, color: kPrimary, size: 24),
                  padding: EdgeInsets.zero,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _AlertStrip extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFFE8F5E9),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF2E7D32)),
        ),
        child: Row(
          children: const [
            Icon(Icons.verified_user, color: Color(0xFF2E7D32), size: 18),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'No risky activity detected today.',
                style: TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 14,
                  color: Color(0xFF2E7D32),
                  fontWeight: FontWeight.w100,
                  letterSpacing: -0.7,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _QuickButtons extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        children: [
          _QuickButton(
            icon: Icons.add_circle_outline,
            label: 'Add Money',
            onTap: () => context.go('/cashin'),
          ),
          _QuickButton(
            icon: Icons.north_east,
            label: 'Send Money',
            onTap: () => context.go('/send'),
          ),
          _QuickButton(
            icon: Icons.south_west,
            label: 'Deposit Funds',
            onTap: () => context.go('/deposit'),
          ),
          _QuickButton(
            icon: Icons.account_balance_wallet_outlined,
            label: 'Cashout',
            onTap: () => context.go('/withdraw'),
          ),
          _QuickButton(
            icon: Icons.savings_outlined,
            label: 'Micro Finance',
            onTap: () => context.go('/microfinance'),
          ),
          _QuickButton(
            icon: Icons.payment,
            label: 'Payment',
            onTap: () => context.go('/scan'),
          ),
        ],
      ),
    );
  }
}

class _QuickButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final w = (MediaQuery.of(context).size.width - 20 * 2 - 12) / 2;
    return SizedBox(
      width: w,
      child: InkWell(
        borderRadius: BorderRadius.circular(22),
        onTap: onTap,
        child: Ink(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 12,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 5),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: const BoxDecoration(
                  color: Color.fromARGB(255, 22, 73, 243),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, size: 26, color: Colors.white),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  label,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF1E1E1E),
                    letterSpacing: -0.6,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TransactionHistory extends StatelessWidget {
  final List<dynamic> transactions;
  final String currentUserId;

  const _TransactionHistory({
    required this.transactions,
    required this.currentUserId,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Recent Transactions',
                style: TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 20,
                  fontWeight: FontWeight.w400,
                  color: kText,
                  letterSpacing: -0.5,
                ),
              ),
              TextButton(
                onPressed: () => context.go('/history'),
                child: const Text(
                  'See All',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Color.fromARGB(255, 49, 51, 53),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (transactions.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32.0),
                child: Text(
                  'No transactions yet',
                  style: TextStyle(
                    fontFamily: 'InstrumentSans',
                    color: kSubtle,
                    fontSize: 16,
                  ),
                ),
              ),
            )
          else
            ...transactions.map((tx) => Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: _TransactionItem(
                transaction: tx,
                currentUserId: currentUserId,
              ),
            )).toList(),
        ],
      ),
    );
  }
}

class _TransactionItem extends StatelessWidget {
  final Map<String, dynamic> transaction;
  final String currentUserId;

  const _TransactionItem({
    required this.transaction,
    required this.currentUserId,
  });

  @override
  Widget build(BuildContext context) {
    final amount = (transaction['amount'] ?? 0.0).toDouble();
    final senderId = transaction['sender_id']?.toString() ?? '';
    final receiverId = transaction['receiver_id']?.toString() ?? '';
    final timestamp = transaction['timestamp'] ?? '';

    // Determine if this is sent or received
    final isReceived = receiverId == currentUserId;
    final isPositive = isReceived;

    // Parse timestamp
    String formattedDate = 'Unknown date';
    try {
      final dt = DateTime.parse(timestamp);
      final now = DateTime.now();
      final diff = now.difference(dt);

      if (diff.inDays == 0) {
        final hour = dt.hour > 12 ? dt.hour - 12 : dt.hour;
        final period = dt.hour >= 12 ? 'PM' : 'AM';
        formattedDate = 'Today, $hour:${dt.minute.toString().padLeft(2, '0')} $period';
      } else if (diff.inDays == 1) {
        final hour = dt.hour > 12 ? dt.hour - 12 : dt.hour;
        final period = dt.hour >= 12 ? 'PM' : 'AM';
        formattedDate = 'Yesterday, $hour:${dt.minute.toString().padLeft(2, '0')} $period';
      } else {
        final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        final hour = dt.hour > 12 ? dt.hour - 12 : dt.hour;
        final period = dt.hour >= 12 ? 'PM' : 'AM';
        formattedDate = '${months[dt.month - 1]} ${dt.day}, $hour:${dt.minute.toString().padLeft(2, '0')} $period';
      }
    } catch (e) {
      // Keep default
    }

    final icon = isPositive ? Icons.arrow_downward : Icons.arrow_upward;
    final title = transaction['description'] ?? (isPositive ? 'Received' : 'Sent');
    final amountStr = '${isPositive ? '+' : '-'}৳${amount.toStringAsFixed(2)}';

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: isPositive
                  ? const Color(0xFFE8F5E9).withOpacity(0.5)
                  : const Color(0xFFFFEBEE).withOpacity(0.5),
              shape: BoxShape.circle,
            ),
            child: Icon(
              icon,
              color: isPositive
                  ? const Color(0xFF2E7D32)
                  : const Color(0xFFD32F2F),
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    letterSpacing: -0.5,
                    color: kText,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  formattedDate,
                  style: const TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 12,
                    fontWeight: FontWeight.w400,
                    letterSpacing: -0.5,
                    color: kSubtle,
                  ),
                ),
              ],
            ),
          ),
          Text(
            amountStr,
            style: TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: isPositive
                  ? const Color(0xFF2E7D32)
                  : const Color(0xFFD32F2F),
            ),
          ),
        ],
      ),
    );
  }
}