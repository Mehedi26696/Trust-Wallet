class Merchant {
  final String name; final bool verified; final String offer;
  const Merchant(this.name, this.verified, this.offer);
}

const merchants = <Merchant>[
  Merchant('Campus Cafe', true, '৳20 ছাড় — ৳500+ এ'),
  Merchant('Book Hub', false, '১০% ডিসকাউন্ট'),
];
