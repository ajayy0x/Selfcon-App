"""Seed data: 12 Lagos listings. Imported by app.py."""
IMGS = ["1560448204-e02f11c3d0e2", "1522708323590-d24dbb6b0267", "1502672260266-1c1ef2d93688",
        "1493809842364-78817add7ffb", "1545324418-cc1a3fa10c00", "1512917774080-9991f1c4c750",
        "1564013799919-ab600027ffc6", "1580587771525-78b9dba3b914", "1600596542815-ffad4c1539a9",
        "1600607687939-ce8a6c25118c", "1600585154340-be6161a56a0c", "1613490493576-7fde63acd811"]
A = ["wifi", "generator", "gym", "parking", "security", "water", "ac"]

def img(i, w=1000):
    return f"https://images.unsplash.com/photo-{IMGS[i % 12]}?auto=format&fit=crop&w={w}&q=70"

# title, location, type, beds, baths, area(sqm), nightly, rent/yr, sale, badges, amenities, vs-average %, ROI %, rating
RAW = [
 ("Quiet 2-Bed with Gym, Lekki Phase 1", "Lekki", "Flat", 2, 2, 110, 85000, 1900000, 145000000, ["Verified", "New"], A, -10, 9.2, 4.9),
 ("Smart Self-Contain near Yaba Tech", "Yaba", "Self-Contain", 1, 1, 32, 28000, 650000, 38000000, ["Verified"], ["wifi", "generator", "water", "security"], -6, 8.1, 4.6),
 ("Skyline 3-Bed Penthouse, Victoria Island", "Victoria Island", "Flat", 3, 4, 240, 220000, 12500000, 480000000, ["Verified", "High ROI"], A, 4, 11.4, 4.9),
 ("Family Duplex with Garden, Ajah", "Ajah", "Duplex", 4, 5, 320, 150000, 6500000, 210000000, ["New"], A[:2] + A[3:], -8, 10.2, 4.7),
 ("Cosy 1-Bed in Ikeja GRA", "Ikeja", "Flat", 1, 1, 60, 45000, 1800000, 62000000, ["Verified"], ["wifi", "generator", "parking", "security", "water", "ac"], -3, 7.8, 4.5),
 ("Fixer-upper Bungalow, Surulere", "Surulere", "Bungalow", 3, 2, 180, None, 2200000, 58000000, ["Fixer-upper", "High ROI"], ["parking", "security", "water"], -22, 14.5, 4.2),
 ("Waterfront 4-Bed Terrace, Ikoyi", "Ikoyi", "Duplex", 4, 5, 380, 350000, 18000000, 750000000, ["Verified", "High ROI"], A, 6, 9.9, 5.0),
 ("Modern 2-Bed with Pool, Lekki Phase 2", "Lekki", "Flat", 2, 2, 120, 95000, 2600000, 165000000, ["New", "Verified"], A, 1, 8.8, 4.8),
 ("Studio Self-Contain, Ikeja", "Ikeja", "Self-Contain", 1, 1, 28, 25000, 550000, 32000000, ["New"], ["wifi", "generator", "water"], -9, 8.6, 4.4),
 ("Bright 3-Bed Flat, Yaba", "Yaba", "Flat", 3, 3, 150, 90000, 3200000, 98000000, ["Verified"], ["wifi", "generator", "parking", "security", "water"], -5, 9.0, 4.6),
 ("Beachside Studio, Ajah", "Ajah", "Self-Contain", 1, 1, 40, 40000, 900000, 45000000, ["High ROI"], ["wifi", "generator", "security", "ac", "water"], -12, 12.1, 4.5),
 ("Fixer-upper Duplex, Surulere", "Surulere", "Duplex", 4, 3, 260, None, 3500000, 72000000, ["Fixer-upper", "High ROI"], ["parking", "security"], -25, 15.8, 4.1),
]

def build():
    out = []
    for i, r in enumerate(RAW):
        t, loc, typ, bd, ba, area, n, rent, sale, badges, am, diff, roi, rating = r
        out.append(dict(id=i + 1, title=t, location=loc, type=typ, beds=bd, baths=ba, area=area,
                        nightly=n, rent=rent, service=round(rent * 0.1, -3), sale=sale, badges=badges,
                        amenities=am, vs_avg=diff, roi=roi, rating=rating,
                        images=[img(i), img(i + 4), img(i + 7), img(i + 10)],
                        desc=f"A {bd}-bedroom {typ.lower()} in {loc}, Lagos with {area} sqm of living space. "
                             f"Verified by the SelfCon team, with clear pricing and a tour you can book in minutes."))
    return out

LISTINGS = build()
