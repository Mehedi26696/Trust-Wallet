import 'dart:math';

class RiskService {
  // fake score: risky if number ends with 999 or amount > 10k
  Map<String, dynamic> score(String phone, num amount) {
    final risky = phone.endsWith('999') || amount > 10000;
    final score = risky ? 86 : (20 + Random().nextInt(20));
    final reason = risky ? 'Reported last week' : 'Normal';
    return {'score': score, 'reason': reason, 'level': risky ? 'high' : 'low'};
  }
}

class FeeService {
  Map<String, num> quote(num amount) {
    // Rates: ৳10 per ৳1000 for transaction fee (1%) and ৳5 per ৳1000 for VAT (0.5%)
    const feeRate = 10 / 1000;
    const vatRate = 5 / 1000;

    final fee = (amount * feeRate).roundToDouble();
    final vat = (amount * vatRate).roundToDouble();
    return {'vat': vat, 'fee': fee, 'total': amount + vat + fee};
  }
}

class Offer {
  final String title; // e.g., "৳20 off — ৳500+"
  final String tag; // e.g., "Today only"
  const Offer(this.title, this.tag);
}

class Merchant {
  final String id; // e.g., "M001"
  final String name; // "Campus Cafe"
  final bool verified; // true/false
  final String phone; // merchant receive phone (mock)
  final String address; // display only
  final List<Offer> offers;

  const Merchant({
    required this.id,
    required this.name,
    required this.verified,
    required this.phone,
    required this.address,
    required this.offers,
  });
}

const _merchants = <Merchant>[
  Merchant(
    id: 'M001',
    name: 'Campus Cafe',
    verified: true,
    phone: '+8801700001001',
    address: 'Gate 2, University Road',
    offers: [
      Offer('৳20 off — ৳500+', 'Today only'),
      Offer('Free drink — ৳1000+', 'Weekend'),
    ],
  ),
  Merchant(
    id: 'M002',
    name: 'Book Hub',
    verified: false,
    phone: '+8801700001002',
    address: 'Library Market, 2nd Floor',
    offers: [Offer('10% discount', 'Student ID')],
  ),
  Merchant(
    id: 'M003',
    name: 'Tech Corner',
    verified: true,
    phone: '+8801700001003',
    address: 'IT Building, Level 1',
    offers: [Offer('৳50 off — ৳1000+', 'Today only')],
  ),
];

class MerchantService {
  List<Merchant> list() => _merchants;

  Merchant byId(String id) =>
      _merchants.firstWhere((m) => m.id == id, orElse: () => _merchants.first);

  // mock “QR code” -> merchant mapping (accepts ID like M001 or name)
  Merchant fromScanCode(String code) {
    final id = code.trim().toUpperCase();
    final byId = _merchants.where((m) => m.id == id);
    if (byId.isNotEmpty) return byId.first;

    final byName = _merchants.where(
      (m) => m.name.toLowerCase() == code.toLowerCase(),
    );
    if (byName.isNotEmpty) return byName.first;

    // fallback random
    return _merchants[Random().nextInt(_merchants.length)];
  }
}
