import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:trustwallet_frontend/src/features/auth/onboarding_screen.dart';
import 'package:trustwallet_frontend/src/features/auth/signin_screen.dart';
import 'package:trustwallet_frontend/src/features/auth/signup_screen.dart';
import 'package:trustwallet_frontend/src/features/auth/splash_screen.dart';
import 'package:trustwallet_frontend/src/features/merchant/pay_confirm_screen.dart';
import '../features/dashboard/home_screen.dart';
import '../features/send/send_entry_screen.dart';
import '../features/send/send_confirm_screen.dart';
import '../features/receipt/receipt_screen.dart';
import '../features/cashin/cash_in_screen.dart';
import '../features/cashout/cash_out_screen.dart';
import '../features/merchant/scan_screen.dart';
import '../features/merchant/merchant_profile_screen.dart';
import '../features/offers/top_shops_screen.dart';
import '../features/history/history_screen.dart';
import '../features/settings/settings_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (_, __) => const SplashScreen()),
      GoRoute(
        path: '/onboarding',
        builder: (_, __) => const OnboardingScreen(),
      ),
      GoRoute(path: '/signin', builder: (_, __) => const SignInScreen()),
      GoRoute(path: '/signup', builder: (_, __) => const SignUpScreen()),

      GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
      GoRoute(path: '/send', builder: (_, __) => const SendEntryScreen()),
      GoRoute(
        path: '/send/confirm',
        builder: (_, __) => const SendConfirmScreen(),
      ),
      GoRoute(
        path: '/receipt',
        builder: (context, state) => const ReceiptScreen(),
      ),
      /*GoRoute(path: '/cashin', builder: (_, __) => const CashInScreen()),
      GoRoute(path: '/cashout', builder: (_, __) => const CashOutScreen()),*/
      GoRoute(path: '/scan', builder: (_, __) => const ScanScreen()),
      GoRoute(
        path: '/pay/confirm',
        builder: (context, state) => const PayConfirmScreen(),
      ),
      GoRoute(
        path: '/merchant',
        builder: (_, __) => const MerchantProfileScreen(),
      ),
      /*GoRoute(path: '/offers', builder: (_, __) => const TopShopsScreen()),
      GoRoute(path: '/history', builder: (_, __) => const HistoryScreen()),
      GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),*/
    ],
  );
});
