import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import 'package:trustwallet_frontend/src/api.dart';

class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key});

  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  final _formKey = GlobalKey<FormState>();
  final phoneController = TextEditingController();
  final passwordController = TextEditingController();
  bool _obscureText = true;
  bool rememberMe = false;

  String? _accessToken;

  @override
  void dispose() {
    phoneController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color.fromARGB(255, 245, 249, 255),
              Color.fromARGB(255, 151, 212, 255),
            ],
            begin: Alignment.center,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Image.asset(
                      'assets/images/logo.png',
                      height: 150,
                      width: 370,
                    ),
                    const SizedBox(height: 40),
                    const Text(
                      "Welcome!",
                      style: TextStyle(
                        color: Color.fromARGB(246, 6, 122, 238),
                        fontFamily: 'InstrumentSans',
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        letterSpacing: -1,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      "Login with your data that you entered\n during your registration",
                      textAlign: TextAlign.center,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontFamily: 'InstrumentSans',
                        fontWeight: FontWeight.w300,
                        color: const Color(0xFF6E6E86),
                        fontSize: 14,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: 36),
                    TextFormField(
                      controller: phoneController,
                      keyboardType: TextInputType.phone,
                      decoration: InputDecoration(
                        labelText: "Phone",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 20,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF626C7A),
                          letterSpacing: -0.5,
                        ),
                        prefixIcon: const Icon(Icons.phone_rounded),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(
                            color: Color(0xFF626C7A),
                            width: 1,
                          ),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(
                            color: Color.fromARGB(255, 45, 121, 172),
                            width: 1,
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(
                            color: Color(0xFF2196F3),
                            width: 2,
                          ),
                        ),
                      ),
                      validator: (value) => value == null || value.isEmpty
                          ? 'Please enter your phone number'
                          : null,
                    ),
                    const SizedBox(height: 20),
                    TextFormField(
                      controller: passwordController,
                      obscureText: _obscureText,
                      decoration: InputDecoration(
                        labelText: "Password",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 20,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF626C7A),
                          letterSpacing: -0.5,
                        ),
                        prefixIcon: const Icon(Icons.lock_rounded),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscureText
                                ? Icons.visibility_off
                                : Icons.visibility,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscureText = !_obscureText;
                            });
                          },
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(
                            color: Color.fromARGB(255, 45, 121, 172),
                            width: 1,
                          ),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(
                            color: Color(0xFFBDBDBD),
                            width: 1,
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(20),
                          borderSide: const BorderSide(
                            color: Color(0xFF2196F3),
                            width: 2,
                          ),
                        ),
                      ),
                      validator: (value) => value == null || value.isEmpty
                          ? 'Please enter your password'
                          : null,
                    ),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        const Spacer(),
                        TextButton(
                          onPressed: () {
                            context.push('/forgot-password');
                          },
                          child: const Text(
                            'Forgot Password?',
                            style: TextStyle(
                              color: Color(0xFF2196F3),
                              fontFamily: 'InstrumentSans',
                              fontSize: 16,
                              fontWeight: FontWeight.w400,
                              letterSpacing: -0.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color.fromARGB(
                            255,
                            41,
                            43,
                            44,
                          ),
                          elevation: 0,
                          padding: const EdgeInsets.symmetric(
                            vertical: 14,
                            horizontal: 24,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(18),
                          ),
                        ),
                        onPressed: () async {
                          if (_formKey.currentState!.validate()) {
                            final messenger = ScaffoldMessenger.of(context);
                            try {
                              final uri = Uri.parse(login_endpoint);
                              final res = await http.post(
                                uri,
                                headers: {'Content-Type': 'application/json'},
                                body: jsonEncode({
                                  'phone_number': phoneController.text.trim(),
                                  'password': passwordController.text,
                                }),
                              );

                              if (res.statusCode == 200) {
                                final data =
                                    jsonDecode(res.body)
                                        as Map<String, dynamic>;
                                _accessToken = data['access_token'] as String?;
                                // Optional: you can also read data['expires_in'] if needed.

                                if (_accessToken == null) {
                                  if (!mounted) return;
                                  messenger.showSnackBar(
                                    const SnackBar(
                                      content: Text('Invalid server response.'),
                                    ),
                                  );
                                  return;
                                }
                                authToken = _accessToken;
                                if (!mounted) return;
                                context.go('/home');
                              } else {
                                if (!mounted) return;
                                messenger.showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      'Login failed (${res.statusCode}). Check your credentials.',
                                    ),
                                  ),
                                );
                              }
                            } catch (e) {
                              if (!mounted) return;
                              messenger.showSnackBar(
                                const SnackBar(
                                  content: Text(
                                    'Network error. Please try again.',
                                  ),
                                ),
                              );
                            }
                          }
                        },
                        child: const Text(
                          "Sign in",
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 20,
                            fontWeight: FontWeight.w500,
                            color: Colors.white,
                            letterSpacing: -0.5,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    const SizedBox(height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Don't have an account? ",
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 16,
                            color: Color(0xFF626C7A),
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            context.push('/signup');
                          },
                          child: const Text(
                            "Sign Up",
                            style: TextStyle(
                              color: Color(0xFF2196F3),
                              fontFamily: 'InstrumentSans',
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              letterSpacing: -0.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
