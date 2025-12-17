// lib/src/core/theme.dart
import 'package:flutter/material.dart';

const kPrimary = Color(0xFF2196F3);
const kPrimaryDark = Color(0xFF1976D2);
const kSurface = Color(0xFFF8F9FA);
const kText = Color(0xFF1E1E1E);
const kSubtle = Color(0xFF626C7A);

ThemeData buildTheme() {
  final colorScheme = ColorScheme.fromSeed(
    seedColor: kPrimary,
    brightness: Brightness.light,
  );
  return ThemeData(
    colorScheme: colorScheme,
    useMaterial3: true,
    fontFamily: 'InstrumentSans',
    scaffoldBackgroundColor: kSurface,
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.white,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontFamily: 'InstrumentSans',
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: kText,
      ),
    ),
  );
}
