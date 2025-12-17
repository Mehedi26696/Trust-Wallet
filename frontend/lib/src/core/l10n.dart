import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final localeProvider = StateProvider<Locale?>((_) => const Locale('bn'));

String t(BuildContext ctx, String key, {Locale? locale}) {
  final map = (locale ?? Localizations.localeOf(ctx)).languageCode == 'bn'
      ? _bn : _en;
  return map[key] ?? key;
}

const _bn = {
  'app_title':'TrustWallet',
  'login':'লগইন করুন',
  'create_account':'নতুন অ্যাকাউন্ট',
  'send_money':'টাকা পাঠান',
  'cash_in':'ক্যাশ ইন',
  'cash_out':'ক্যাশ আউট',
  'offers':'টপ শপস & অফারস',
  'history':'লেনদেন',
  'settings':'সেটিংস',
  'final_payable':'মোট পরিশোধ'
};

const _en = {
  'app_title':'TrustWallet',
  'login':'Login',
  'create_account':'Create Account',
  'send_money':'Send Money',
  'cash_in':'Cash In',
  'cash_out':'Cash Out',
  'offers':'Top Shops & Offers',
  'history':'History',
  'settings':'Settings',
  'final_payable':'Final payable'
};
