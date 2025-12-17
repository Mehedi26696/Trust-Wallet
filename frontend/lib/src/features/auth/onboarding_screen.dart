import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF2196F3), // Blue
              Color(0xFFE3F2FD), // Light Blue
              Color(0xFFFFFFFF), // White
            ],
            stops: [0.0, 0.4, 0.8],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 160),
                // Logo
                Align(
                  alignment: Alignment.centerLeft,
                  child: Image.asset(
                    'assets/images/logo.png',
                    height: 140,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        height: 50,
                        width: 200,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Center(
                          child: Text(
                            'TrustWallet',
                            style: TextStyle(
                              fontFamily: 'InstrumentSans',
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF2196F3),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const Spacer(flex: 2),
                // Tagline - Three Lines
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Secure,',
                      textAlign: TextAlign.left,
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 50,
                        fontWeight: FontWeight.w100,
                        color: Color(0xFF1E1E1E),
                        letterSpacing: -1,
                        height: 1.2,
                      ),
                    ),
                    Text(
                      'Transparent,',
                      textAlign: TextAlign.left,
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 50,
                        fontWeight: FontWeight.w100,
                        color: Color(0xFF1E1E1E),
                        letterSpacing: -1,
                        height: 1.2,
                      ),
                    ),
                    Text(
                      '& Intelligent',
                      textAlign: TextAlign.left,
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 50,
                        fontWeight: FontWeight.w100,
                        color: Color(0xFF1E1E1E),
                        letterSpacing: -1,
                        height: 1.2,
                      ),
                    ),
                    Text(
                      'payments',
                      textAlign: TextAlign.left,
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 50,
                        fontWeight: FontWeight.w100,
                        color: Color.fromARGB(255, 0, 59, 252),
                        letterSpacing: -1,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
                const Spacer(flex: 2),
                // Buttons
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color.fromARGB(255, 41, 43, 44),
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(
                        vertical: 14,
                        horizontal: 24,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(18),
                      ),
                    ),
                    onPressed: () => context.go('/signup'),
                    child: const Text(
                      'Get Started',
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 18,
                        fontWeight: FontWeight.w500,
                        color: Colors.white,
                        letterSpacing: -0.5,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Center(
                  child: TextButton(
                    onPressed: () => context.go('/signin'),
                    child: const Text(
                      'I already have an account',
                      style: TextStyle(
                        fontFamily: 'InstrumentSans',
                        fontSize: 16,
                        fontWeight: FontWeight.w400,
                        color: Color.fromARGB(255, 59, 62, 66),
                        letterSpacing: -0.5,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
