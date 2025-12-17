import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class SplashScreen extends StatefulWidget { const SplashScreen({super.key}); 
  @override State<SplashScreen> createState() => _SplashScreenState(); }

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 900))
    ..forward();
  @override void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 1400), () => context.go('/onboarding'));
  }
  @override void dispose(){ _c.dispose(); super.dispose(); }

  @override Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(fit: StackFit.expand, children: [
        // soft background (optional)
        Image.asset('assets/images/splash_screen.png', fit: BoxFit.cover),
        Center(
          child: ScaleTransition(
            scale: CurvedAnimation(parent: _c, curve: Curves.easeOutBack),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Image.asset('assets/images/logo.png', height: 280),
              const SizedBox(height: 12),
            ]),
          ),
        ),
      ]),
    );
  }
}
