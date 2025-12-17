import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import '../../api.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool isLoading = true;
  String? errorMessage;
  Map<String, dynamic>? userData;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    try {
      final response = await http.get(
        Uri.parse(profile_endpoint),
        headers: authHeaders(),
      );

      if (response.statusCode == 200) {
        setState(() {
          userData = jsonDecode(response.body);
          isLoading = false;
        });
      } else {
        setState(() {
          errorMessage = 'Failed to load profile';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Network error';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      appBar: AppBar(
        backgroundColor: const Color.fromARGB(255, 2, 101, 250),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => context.go('/home'),
        ),
        title: const Text(
          'Profile',
          style: TextStyle(
            fontFamily: 'InstrumentSans',
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.white,
            letterSpacing: -0.1,
          ),
        ),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(errorMessage!),
                      ElevatedButton(
                        onPressed: _fetchProfile,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  child: Column(
                    children: [
                      _ProfileHeader(userData: userData!),
                      const SizedBox(height: 20),
                      _ProfileDetails(userData: userData!),
                    ],
                  ),
                ),
    );
  }
}

class _ProfileHeader extends StatelessWidget {
  final Map<String, dynamic> userData;

  const _ProfileHeader({required this.userData});

  @override
  Widget build(BuildContext context) {
    final name = userData['full_name'] ?? 'User';
    final email = userData['email'] ?? '';
    final facePath = userData['face_image_path'] as String?;

    ImageProvider? backgroundImage;
    if (facePath != null && facePath.isNotEmpty) {
      // Normalize path for URL (replace backslashes with forward slashes)
      final normalizedPath = facePath.replaceAll(r'\', '/');
      final url = '$BASE_URL_LOCAL/$normalizedPath';
      backgroundImage = NetworkImage(url);
    }

    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        color: Color.fromARGB(255, 2, 101, 250),
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(30),
          bottomRight: Radius.circular(30),
        ),
      ),
      padding: const EdgeInsets.only(bottom: 40),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 2),
            ),
            child: CircleAvatar(
              radius: 50,
              backgroundColor: Colors.white,
              backgroundImage: backgroundImage,
              child: backgroundImage == null
                  ? const Icon(Icons.person, size: 60, color: Color(0xFF2196F3))
                  : null,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            name,
            style: const TextStyle(
              fontFamily: 'InstrumentSans',
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          if (email.isNotEmpty)
            Text(
              email,
              style: const TextStyle(
                fontFamily: 'InstrumentSans',
                fontSize: 16,
                color: Colors.white70,
              ),
            ),
        ],
      ),
    );
  }
}

class _ProfileDetails extends StatelessWidget {
  final Map<String, dynamic> userData;

  const _ProfileDetails({required this.userData});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        children: [
          _buildInfoTile(
            icon: Icons.phone_rounded,
            title: 'Phone Number',
            value: userData['phone_number'] ?? 'N/A',
          ),
          const SizedBox(height: 16),
          _buildInfoTile(
            icon: Icons.credit_card_rounded,
            title: 'NID Number',
            value: userData['nid'] ?? 'N/A',
          ),
          const SizedBox(height: 16),
          _buildInfoTile(
            icon: Icons.account_balance_wallet_rounded,
            title: 'Wallet Balance',
            value: '৳${(userData['balance'] ?? 0.0).toString()}',
          ),
        ],
      ),
    );
  }

  Widget _buildInfoTile({
    required IconData icon,
    required String title,
    required String value,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
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
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFFE3F2FD),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: const Color(0xFF2196F3)),
          ),
          const SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 14,
                  color: Color(0xFF626C7A),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontFamily: 'InstrumentSans',
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF1E1E1E),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
