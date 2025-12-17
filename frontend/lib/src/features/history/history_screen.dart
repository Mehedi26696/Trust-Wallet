import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import '../../api.dart';
import '../../core/widgets/rounded_navbar.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final int _tab = 1; // History tab index
  List<dynamic> transactions = [];
  bool isLoading = true;
  String? errorMessage;
  String currentUserId = '';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (authToken == null) {
      context.go('/signin');
      return;
    }

    try {
      // 1. Get current user ID to determine Send/Receive
      final profileResponse = await http.get(
        Uri.parse(profile_endpoint),
        headers: authHeaders(),
      );
      if (profileResponse.statusCode == 200) {
        final profileData = jsonDecode(profileResponse.body);
        currentUserId = profileData['id'] ?? '';
      }

      // 2. Fetch Transactions
      // Using a larger page size for history
      final txResponse = await http.get(
        Uri.parse('$transactions_endpoint?page=1&page_size=50'), 
        headers: authHeaders(),
      );

      if (txResponse.statusCode == 200) {
        final txData = jsonDecode(txResponse.body);
        setState(() {
          transactions = txData['items'] ?? [];
          isLoading = false;
        });
      } else {
        setState(() {
          errorMessage = 'Failed to load transactions';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Network error: $e';
        isLoading = false;
      });
    }
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
            'Transaction History',
            style: TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 22,
              fontWeight: FontWeight.w500,
              color: Colors.white,
              letterSpacing: -1,
            ),
          ),
          leading: null, // No back button on main tab pages usually, but if navigated from "See All", it might need one.
          // If this is a main tab, we use BottomNavBar.
          // For consistent navigation, let's assume it's part of the navbar system.
          automaticallyImplyLeading: false, 
        ),
        body: isLoading
            ? const Center(child: CircularProgressIndicator())
            : errorMessage != null
                ? Center(
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
                  )
                : transactions.isEmpty
                    ? const Center(
                        child: Text(
                          'No transactions found',
                          style: TextStyle(
                            color: Color(0xFF626C7A),
                            fontSize: 16,
                            fontFamily: 'InstrumentSans',
                            letterSpacing: -0.5,
                          ),
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: _loadData,
                        child: ListView.builder(
                          itemCount: transactions.length,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          itemBuilder: (context, index) {
                            return _HistoryItem(
                              transaction: transactions[index],
                              currentUserId: currentUserId,
                            );
                          },
                        ),
                      ),
        bottomNavigationBar: RoundedNavBar(
          currentIndex: _tab,
          onTap: (i) {
            if (i == _tab) return;
            if (i == 0) context.go('/home');
            if (i == 2) context.go('/scan');
            if (i == 3) context.go('/settings');
          },
        ),
      ),
    );
  }
}

class _HistoryItem extends StatelessWidget {
  final Map<String, dynamic> transaction;
  final String currentUserId;

  const _HistoryItem({
    required this.transaction,
    required this.currentUserId,
  });

  @override
  Widget build(BuildContext context) {
    final amount = (transaction['amount'] ?? 0.0).toDouble();
    final senderId = transaction['sender_id']?.toString() ?? '';
    final receiverId = transaction['receiver_id']?.toString() ?? '';
    final timestamp = transaction['timestamp'] ?? '';

    final isReceived = receiverId == currentUserId;
    final isPositive = isReceived;

    String formattedDate = 'Unknown date';
    try {
      final dt = DateTime.parse(timestamp);
      final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      final hour = dt.hour > 12 ? dt.hour - 12 : dt.hour;
      final period = dt.hour >= 12 ? 'PM' : 'AM';
      formattedDate = '${months[dt.month - 1]} ${dt.day}, $hour:${dt.minute.toString().padLeft(2, '0')} $period';
    } catch (_) {}

    final icon = isPositive ? Icons.arrow_downward : Icons.arrow_upward;
    final title = transaction['description'] ?? (isPositive ? 'Received' : 'Sent');
    final amountStr = '${isPositive ? '+' : '-'}৳${amount.toStringAsFixed(2)}';

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
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
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1E1E1E),
                    letterSpacing: -1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  formattedDate,
                  style: const TextStyle(
                    fontFamily: 'InstrumentSans',
                    fontSize: 13,
                    color: Color(0xFF626C7A),
                    letterSpacing: -0.5,
                  ),
                ),
              ],
            ),
          ),
          Text(
            amountStr,
            style: TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: isPositive
                  ? const Color(0xFF2E7D32)
                  : const Color(0xFFD32F2F),
              letterSpacing: -1,
            ),
          ),
        ],
      ),
    );
  }
}
