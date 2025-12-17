import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/theme.dart';
import 'router.dart';
import '../core/l10n.dart';

class TrustWalletApp extends ConsumerWidget {
  const TrustWalletApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final locale = ref.watch(localeProvider);
    return MaterialApp.router(
      title: 'TrustWallet',
      theme: buildTheme(),
      routerConfig: router,
      locale: locale,
      debugShowCheckedModeBanner: false,
    );
  }
}
