import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import 'package:trustwallet_frontend/src/api.dart';
import 'package:image_picker/image_picker.dart';

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final _formKey = GlobalKey<FormState>();
  final nameController = TextEditingController();
  final nidController = TextEditingController();
  final phoneController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool agreeToTerms = false;
  XFile? _faceImage;

  @override
  void dispose() {
    nameController.dispose();
    nidController.dispose();
    phoneController.dispose();
    emailController.dispose();
    passwordController.dispose();
    confirmPasswordController.dispose();
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
              Color.fromARGB(255, 245, 249, 255), // Light blue
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
                      height: 120,
                      width: 400,
                    ),
                    const SizedBox(height: 26),
                    const Text(
                      "Create Account",
                      style: TextStyle(
                        color: Color.fromARGB(255, 2, 128, 253),
                        fontFamily: 'InstrumentSans',
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        letterSpacing: -1,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      "Sign up to get started with your account",
                      textAlign: TextAlign.center,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontFamily: 'InstrumentSans',
                        fontWeight: FontWeight.w300,
                        color: const Color(0xFF6E6E86),
                        fontSize: 14,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: 28),
                    // Face Capture
                    Row(
                      children: [
                        CircleAvatar(
                          radius: 28,
                          backgroundImage: _faceImage != null
                              ? FileImage(File(_faceImage!.path))
                              : null,
                          child: _faceImage == null
                              ? const Icon(
                                  Icons.person_outline,
                                  size: 28,
                                  color: Color(0xFF2196F3),
                                )
                              : null,
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          icon: const Icon(Icons.camera_alt_rounded),
                          label: const Text('Capture Face'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2196F3),
                          ),
                          onPressed: () async {
                            final picker = ImagePicker();
                            final img = await picker.pickImage(
                              source: ImageSource.camera,
                              preferredCameraDevice: CameraDevice.front,
                              imageQuality: 85,
                            );
                            if (img != null) {
                              setState(() => _faceImage = img);
                            }
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    // Name Field
                    TextFormField(
                      controller: nameController,
                      keyboardType: TextInputType.name,
                      decoration: InputDecoration(
                        labelText: "Full Name",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 18,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF626C7A),
                          letterSpacing: -0.5,
                        ),
                        prefixIcon: const Icon(Icons.person_rounded),
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
                          ? 'Please enter your full name'
                          : null,
                    ),
                    const SizedBox(height: 18),
                    // NID Field
                    TextFormField(
                      controller: nidController,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: "NID No",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 18,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF626C7A),
                          letterSpacing: -0.5,
                        ),
                        prefixIcon: const Icon(Icons.credit_card_rounded),
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
                          ? 'Please enter your NID number'
                          : null,
                    ),
                    const SizedBox(height: 18),
                    // Phone Field
                    TextFormField(
                      controller: phoneController,
                      keyboardType: TextInputType.phone,
                      decoration: InputDecoration(
                        labelText: "Phone",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 18,
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
                          ? 'Please enter your phone number'
                          : null,
                    ),
                    const SizedBox(height: 18),
                    // Email Field
                    TextFormField(
                      controller: emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: InputDecoration(
                        labelText: "Email",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 18,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF626C7A),
                          letterSpacing: -0.5,
                        ),
                        prefixIcon: const Icon(Icons.email_rounded),
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
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your email';
                        }
                        final emailRegex = RegExp(r'^[\w\.-]+@[\w\.-]+\.\w+$');
                        if (!emailRegex.hasMatch(value.trim())) {
                          return 'Enter a valid email';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 18),
                    // Password Field
                    TextFormField(
                      controller: passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: "Password",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 18,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF626C7A),
                          letterSpacing: -0.5,
                        ),
                        prefixIcon: const Icon(Icons.lock_rounded),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword
                                ? Icons.visibility_off
                                : Icons.visibility,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
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
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        if (value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 18),
                    // Confirm Password Field
                    TextFormField(
                      controller: confirmPasswordController,
                      obscureText: _obscureConfirmPassword,
                      decoration: InputDecoration(
                        labelText: "Confirm Password",
                        labelStyle: const TextStyle(
                          fontFamily: 'InstrumentSans',
                          fontSize: 18,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF626C7A),
                          letterSpacing: -0.5,
                        ),
                        prefixIcon: const Icon(Icons.lock_outline_rounded),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscureConfirmPassword
                                ? Icons.visibility_off
                                : Icons.visibility,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscureConfirmPassword =
                                  !_obscureConfirmPassword;
                            });
                          },
                        ),
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
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please confirm your password';
                        }
                        if (value != passwordController.text) {
                          return 'Passwords do not match';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    // Terms and Conditions
                    Row(
                      children: [
                        Checkbox(
                          value: agreeToTerms,
                          onChanged: (newValue) {
                            setState(() {
                              agreeToTerms = newValue ?? false;
                            });
                          },
                          activeColor: const Color(0xFF2196F3),
                          tristate: false,
                          fillColor: MaterialStateProperty.resolveWith((
                            states,
                          ) {
                            if (states.contains(MaterialState.selected)) {
                              return const Color(0xFF2196F3);
                            }
                            return Colors.white;
                          }),
                          checkColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        Expanded(
                          child: RichText(
                            text: const TextSpan(
                              text: "I agree to the ",
                              style: TextStyle(
                                fontFamily: 'InstrumentSans',
                                fontSize: 13,
                                color: Color(0xFF626C7A),
                              ),
                              children: [
                                TextSpan(
                                  text: "Terms & Conditions",
                                  style: TextStyle(
                                    color: Color(0xFF2196F3),
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    // Sign Up Button
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
                            if (!agreeToTerms) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text(
                                    'Please agree to Terms & Conditions',
                                  ),
                                  backgroundColor: Colors.red,
                                ),
                              );
                              return;
                            }

                            try {
                              final uri = Uri.parse(signup_endpoint);
                              final res = await http.post(
                                uri,
                                headers: {'Content-Type': 'application/json'},
                                body: jsonEncode({
                                  'full_name': nameController.text.trim(),
                                  'nid': nidController.text.trim(),
                                  'phone_number': phoneController.text.trim(),
                                  'email': emailController.text.trim(),
                                  'password': passwordController.text,
                                }),
                              );

                              if (res.statusCode == 200 ||
                                  res.statusCode == 201) {
                                final loginRes = await http.post(
                                  Uri.parse(login_endpoint),
                                  headers: {'Content-Type': 'application/json'},
                                  body: jsonEncode({
                                    'phone_number': phoneController.text.trim(),
                                    'password': passwordController.text,
                                  }),
                                );
                                if (loginRes.statusCode == 200) {
                                  final data =
                                      jsonDecode(loginRes.body)
                                          as Map<String, dynamic>;
                                  final token = data['access_token'] as String?;
                                  if (token != null) {
                                    authToken = token; // include Authorization
                                    // Enroll face if captured
                                    if (_faceImage != null) {
                                      try {
                                        final file = File(_faceImage!.path);
                                        final fileExists = await file.exists();
                                        print(
                                          'Face enrollment: File exists=$fileExists, path=${_faceImage!.path}',
                                        );

                                        if (!fileExists) {
                                          print(
                                            'Face enrollment: File does not exist!',
                                          );
                                        } else {
                                          final fileSize = await file.length();
                                          print(
                                            'Face enrollment: File size=$fileSize bytes',
                                          );

                                          final req = http.MultipartRequest(
                                            'POST',
                                            Uri.parse(enroll_face_endpoint),
                                          );
                                          req.headers['Authorization'] =
                                              'Bearer $authToken';
                                          req.files.add(
                                            await http.MultipartFile.fromPath(
                                              'file',
                                              file.path,
                                              filename: 'face.jpg',
                                            ),
                                          );
                                          print(
                                            'Face enrollment: Sending to $enroll_face_endpoint',
                                          );
                                          final streamed = await req.send();
                                          print(
                                            'Face enrollment: Response status=${streamed.statusCode}',
                                          );
                                          if (streamed.statusCode != 200) {
                                            final response = await http
                                                .Response.fromStream(streamed);
                                            print(
                                              'Face enrollment: Error response=${response.body}',
                                            );
                                          } else {
                                            print('Face enrollment: Success!');
                                          }
                                        }
                                      } catch (e) {
                                        print('Face enrollment error: $e');
                                      }
                                    }
                                    if (!mounted) return;
                                    context.go('/home');
                                    return;
                                  }
                                }
                                if (!mounted) return;
                                context.go('/signin'); // fallback
                              } else {
                                // Show backend validation error to help diagnose 422s
                                String msg = 'Sign up failed';
                                try {
                                  final err = jsonDecode(res.body);
                                  if (err is Map && err['detail'] != null) {
                                    msg = err['detail'].toString();
                                  } else if (err is Map &&
                                      err['error'] != null) {
                                    msg = err['error'].toString();
                                  } else {
                                    msg = res.body;
                                  }
                                } catch (_) {
                                  msg = res.body.isNotEmpty ? res.body : msg;
                                }
                                if (!mounted) return;
                                ScaffoldMessenger.of(
                                  context,
                                ).showSnackBar(SnackBar(content: Text(msg)));
                              }
                            } catch (e) {
                              if (!mounted) return;
                              ScaffoldMessenger.of(context).showSnackBar(
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
                          "Sign Up",
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
                    // Already have account
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Already have an account? ",
                          style: TextStyle(
                            fontFamily: 'InstrumentSans',
                            fontSize: 16,
                            color: Color(0xFF626C7A),
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            context.push('/signin');
                          },
                          child: const Text(
                            "Sign In",
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
