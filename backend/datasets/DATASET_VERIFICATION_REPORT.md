# BENGALURU REAL PROPERTY DATASET VERIFICATION REPORT
Generated: 2026-09-29 22:12:16 IST

## 1. Executive Summary
- **Total Records Collected**: 1986
- **Records Verified (PASS)**: 1984
- **Records Flagged (WARNING)**: 0
- **Records Rejected/Quarantined (QUARANTINED)**: 2
- **Records With Property-Specific Images**: 1986
- **Records Without Images**: 0
- **Records With Real Building/Project Identity**: 1404
- **Records Without Building Identity (Null/Building Unavailable)**: 582
- **Records With Exact GPS Coordinates**: 1986
- **Records With Approximate Coordinates**: 0

## 2. Records by Source & Access Boundary
| Source Website | Status | Records Collected | Limitations / Boundary Observed |
| :--- | :--- | :--- | :--- |
| **NoBroker.in** | Accessible (HTTP 200) | 1986 | Permitted public server-rendered listing pages across 23 Bengaluru localities. |
| **Housing.com** | Restricted | 0 | Automated access blocked with Cloudflare HTTP 406 (Not Acceptable). Complied with Section 18.2 anti-bot rule. |
| **MagicBricks.com** | Restricted | 0 | Automated access returns 4.1KB interstitial verification challenge. Complied with Section 18.2 anti-bot rule. |
| **99acres.com** | Accessible (Rate Trends) | 50 trend tuples | Permitted public market intelligence trends page. |

## 3. Records by Bengaluru Locality
| Locality | Total Records Collected | Exact GPS Coordinates | Building Identity Identified |
| :--- | :--- | :--- | :--- |
| **Koramangala** | 125 | 125 | 74 |
| **HSR Layout** | 125 | 125 | 97 |
| **Whitefield** | 125 | 125 | 112 |
| **Indiranagar** | 55 | 55 | 35 |
| **Electronic City** | 125 | 125 | 112 |
| **Bellandur** | 124 | 124 | 110 |
| **JP Nagar** | 0 | 0 | 0 |
| **Jayanagar** | 100 | 100 | 53 |
| **Marathahalli** | 100 | 100 | 69 |
| **Hebbal** | 100 | 100 | 49 |
| **Yelahanka** | 100 | 100 | 68 |
| **Malleshwaram** | 98 | 98 | 66 |
| **Rajajinagar** | 100 | 100 | 48 |
| **Banashankari** | 100 | 100 | 58 |
| **Sarjapur Road** | 0 | 0 | 0 |
| **Devanahalli** | 75 | 75 | 64 |
| **BTM Layout** | 100 | 100 | 51 |
| **Thanisandra** | 75 | 75 | 67 |
| **Mahadevapura** | 75 | 75 | 54 |
| **KR Puram** | 75 | 75 | 67 |
| **Ejipura** | 59 | 59 | 24 |
| **Varthur** | 75 | 75 | 66 |
| **Kadugodi** | 75 | 75 | 60 |

## 4. Records by Property Type
- **Apartment**: 1593
- **Independent House**: 344
- **Villa**: 49

## 5. Audit Sample Verification (100+ Records Cross-Check)
| # | Property ID | Building / Project Name | Locality | BHK | Area (sqft) | Price (₹) | Source ₹/sqft | Calc ₹/sqft | Lat, Lon | Image Ref | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | NB-8aa9a8849f32 | Monarch Aqua | KR Puram | 3 | 1606.0 | ₹19,500,000 | ₹12,142 | ₹12,141 | 13.014963, 77.701713 | Yes (Source) | PASS |
| 2 | NB-8aa9b2f59f61 | *Unavailable* | Jayanagar | 3 | 1207.0 | ₹10,000,000 | ₹8,285 | ₹8,285 | 12.935619, 77.576525 | Yes (Source) | PASS |
| 3 | NB-8aa9bb389c94 | Ansal Forte | BTM Layout | 2 | 1100.0 | ₹9,000,000 | ₹8,182 | ₹8,181 | 12.914816, 77.622512 | Yes (Source) | PASS |
| 4 | NB-8aa991169f45 | Phoenix Kessaku | Rajajinagar | 3 | 3497.0 | ₹143,500,000 | ₹41,035 | ₹41,035 | 12.998173, 77.553045 | Yes (Source) | PASS |
| 5 | NB-8aa9a6709f4f | White Lotus Tamara | Indiranagar | 4 | 3553.0 | ₹121,200,000 | ₹34,112 | ₹34,112 | 12.976336, 77.641475 | Yes (Source) | PASS |
| 6 | NB-8a9f8683925d | *Unavailable* | Marathahalli | 4 | 7300.0 | ₹50,000,000 | ₹6,849 | ₹6,849 | 12.948531, 77.702428 | Yes (Source) | PASS |
| 7 | NB-8aa9daa49ddd | L&t Elara Celestia | Hebbal | 4 | 4931.0 | ₹126,190,477 | ₹25,591 | ₹25,591 | 13.035356, 77.598787 | Yes (Source) | PASS |
| 8 | NB-ff8081816a35 | Kendriya Vihar | Yelahanka | 3 | 1250.0 | ₹6,000,000 | ₹4,800 | ₹4,800 | 13.107216, 77.600028 | Yes (Source) | PASS |
| 9 | NB-8aa9a6cea0e8 | *Unavailable* | Mahadevapura | 4 | 3500.0 | ₹27,000,000 | ₹7,714 | ₹7,714 | 12.992552, 77.672847 | Yes (Source) | PASS |
| 10 | NB-8aa9a1c69f34 | Provident Botanico | Whitefield | 3 | 1335.0 | ₹16,000,000 | ₹11,985 | ₹11,985 | 12.96982, 77.749972 | Yes (Source) | PASS |
| 11 | NB-8a9fdc8283ac | Vandana Jasmine Apartments | Koramangala | 2 | 1183.0 | ₹8,000,000 | ₹6,762 | ₹6,762 | 12.919756, 77.633748 | Yes (Source) | PASS |
| 12 | NB-8aa99582a0e0 | *Unavailable* | Jayanagar | 1 | 300.0 | ₹4,499,999 | ₹15,000 | ₹15,000 | 12.924706, 77.600093 | Yes (Source) | PASS |
| 13 | NB-8a9faf849a30 | *Unavailable* | Koramangala | 4 | 2200.0 | ₹25,600,000 | ₹11,636 | ₹11,636 | 12.931908, 77.626299 | Yes (Source) | PASS |
| 14 | NB-8a9ffb8287fe | Mbr Suave Apartments | Kadugodi | 3 | 1145.0 | ₹11,000,000 | ₹9,607 | ₹9,606 | 13.005667, 77.758958 | Yes (Source) | PASS |
| 15 | NB-8aa9b61b9ca2 | *Unavailable* | BTM Layout | 2 | 1100.0 | ₹10,000,000 | ₹9,091 | ₹9,090 | 12.922509, 77.614582 | Yes (Source) | PASS |
| 16 | NB-8aa9bb579add | R K Palace Apartment | Jayanagar | 2 | 500.0 | ₹3,000,000 | ₹6,000 | ₹6,000 | 12.94375, 77.592278 | Yes (Source) | PASS |
| 17 | NB-8aa9b19d9f12 | *Unavailable* | Ejipura | 1 | 300.0 | ₹4,000,000 | ₹13,333 | ₹13,333 | 12.945701, 77.628959 | Yes (Source) | PASS |
| 18 | NB-8aa9b4729f16 | Srinivasa Classic | Bellandur | 3 | 1549.0 | ₹25,000,000 | ₹16,139 | ₹16,139 | 12.916396, 77.674144 | Yes (Source) | PASS |
| 19 | NB-ff80818156d5 | Ahad Silver Shelter | HSR Layout | 2 | 975.0 | ₹8,500,000 | ₹8,718 | ₹8,717 | 12.894221, 77.655138 | Yes (Source) | PASS |
| 20 | NB-8aa994569cb2 | Sri Balaji Nest, | Kadugodi | 3 | 1208.0 | ₹10,500,000 | ₹8,692 | ₹8,692 | 12.984862, 77.758269 | Yes (Source) | PASS |
| 21 | NB-8a9fac839a14 | *Unavailable* | Marathahalli | 2 | 1100.0 | ₹9,000,000 | ₹8,182 | ₹8,181 | 12.961495, 77.700481 | Yes (Source) | PASS |
| 22 | NB-8a9f8b8697e3 | Brigade Orchards | Devanahalli | 3 | 1290.0 | ₹12,500,000 | ₹9,690 | ₹9,689 | 13.237063, 77.72428 | Yes (Source) | PASS |
| 23 | NB-8aa9bab29f4f | Kinglife Telosa | Koramangala | 4 | 4415.0 | ₹65,600,000 | ₹14,858 | ₹14,858 | 12.928103, 77.638929 | Yes (Source) | PASS |
| 24 | NB-8a9f8e039357 | Mv Periwinkle Apartments | Thanisandra | 3 | 1860.0 | ₹20,000,000 | ₹10,753 | ₹10,752 | 13.064353, 77.61936 | Yes (Source) | PASS |
| 25 | NB-8a9f8e038fe8 | Candeur Rise | Varthur | 2 | 1180.0 | ₹12,000,000 | ₹10,169 | ₹10,169 | 12.935148, 77.744512 | Yes (Source) | PASS |
| 26 | NB-8aa9be819f04 | Prestige Lavender Fields | Varthur | 1 | 669.0 | ₹10,300,000 | ₹15,396 | ₹15,396 | 12.934257, 77.739616 | Yes (Source) | PASS |
| 27 | NB-8aa99b02a0db | *Unavailable* | Jayanagar | 2 | 550.0 | ₹22,500,000 | ₹40,909 | ₹40,909 | 12.94294, 77.592812 | Yes (Source) | PASS |
| 28 | NB-8aa995b0a0ae | Adhiwara Svm Living | Electronic City | 2 | 1031.0 | ₹5,900,000 | ₹5,723 | ₹5,722 | 12.841146, 77.646931 | Yes (Source) | PASS |
| 29 | NB-8aa9ba91a03d | Sowparnika Skanda | KR Puram | 3 | 1730.0 | ₹9,000,000 | ₹5,202 | ₹5,202 | 12.996383, 77.722763 | Yes (Source) | PASS |
| 30 | NB-ff8081815230 | Mvs Pride Annex | Electronic City | 3 | 1450.0 | ₹9,000,000 | ₹6,207 | ₹6,206 | 12.834638, 77.687391 | Yes (Source) | PASS |
| 31 | NB-8aa9c8a69dd3 | Casagrand | Yelahanka | 2 | 1070.0 | ₹13,500,000 | ₹12,617 | ₹12,616 | 13.115, 77.607 | Yes (Source) | PASS |
| 32 | NB-8aa9b33f9f4f | White Lotus Tamara | Indiranagar | 3 | 2692.0 | ₹91,800,000 | ₹34,101 | ₹34,101 | 12.976336, 77.641475 | Yes (Source) | PASS |
| 33 | NB-8a9f8c838e0d | Kendriya Vihar | Yelahanka | 3 | 1200.0 | ₹10,000,000 | ₹8,333 | ₹8,333 | 13.10689, 77.60013 | Yes (Source) | PASS |
| 34 | NB-8a9faa838b75 | Happy Minds | Yelahanka | 2 | 989.0 | ₹8,500,000 | ₹8,595 | ₹8,594 | 13.121954, 77.608124 | Yes (Source) | PASS |
| 35 | NB-8aa99f3fa004 | Sobha City Aristos 1 | Thanisandra | 4 | 3736.0 | ₹85,000,000 | ₹22,752 | ₹22,751 | 13.055919, 77.632451 | Yes (Source) | PASS |
| 36 | NB-8aa9b4c59ada | Capsicon Enclave, Dasarahalli | Thanisandra | 2 | 1031.0 | ₹6,000,000 | ₹5,820 | ₹5,819 | 13.054009, 77.613453 | Yes (Source) | PASS |
| 37 | NB-8a9fb08499e7 | *Unavailable* | Hebbal | 4 | 2900.0 | ₹12,500,000 | ₹4,310 | ₹4,310 | 13.034299, 77.59818 | Yes (Source) | PASS |
| 38 | NB-8aa9ad709f9e | Awho Sandeep Vihar | KR Puram | 3 | 1721.0 | ₹26,000,000 | ₹15,107 | ₹15,107 | 13.020916, 77.761792 | Yes (Source) | PASS |
| 39 | NB-8aa98e789f30 | Birla Tisya | Rajajinagar | 3 | 1800.0 | ₹45,500,000 | ₹25,278 | ₹25,277 | 12.980229, 77.538274 | Yes (Source) | PASS |
| 40 | NB-8a9f8a839a39 | Mantri Centrium | Malleshwaram | 4 | 4375.0 | ₹52,500,000 | ₹12,000 | ₹12,000 | 12.990155, 77.570547 | Yes (Source) | PASS |
| 41 | NB-8aa9aa6a9c6f | Orchid Lakeview | Bellandur | 3 | 1832.0 | ₹27,000,000 | ₹14,738 | ₹14,737 | 12.931587, 77.679062 | Yes (Source) | PASS |
| 42 | NB-8aa9a3b19c9c | Birla Trimaya, | Devanahalli | 1 | 703.0 | ₹8,200,000 | ₹11,664 | ₹11,664 | 13.24, 77.72 | Yes (Source) | PASS |
| 43 | NB-8a9faf8494cd | Radiance Platinum | Koramangala | 4 | 3056.0 | ₹49,300,000 | ₹16,132 | ₹16,132 | 12.928882, 77.64013 | Yes (Source) | PASS |
| 44 | NB-8a9f8bc3938b | Sahith Delight | Bellandur | 3 | 1750.0 | ₹13,500,000 | ₹7,714 | ₹7,714 | 12.927259, 77.670084 | Yes (Source) | PASS |
| 45 | NB-8a9f86ca7006 | Asset Enclave | Whitefield | 4 | 2815.0 | ₹42,500,000 | ₹15,098 | ₹15,097 | 12.96148, 77.743198 | Yes (Source) | PASS |
| 46 | NB-8aa99c72a0c6 | Birla Tisya | Rajajinagar | 3 | 1660.0 | ₹34,000,000 | ₹20,482 | ₹20,481 | 12.980229, 77.538274 | Yes (Source) | PASS |
| 47 | NB-8aa99cf99fc5 | *Unavailable* | BTM Layout | 3 | 4000.0 | ₹140,000,000 | ₹35,000 | ₹35,000 | 12.917002, 77.620267 | Yes (Source) | PASS |
| 48 | NB-8aa9a407a0b4 | *Unavailable* | Bellandur | 4 | 4680.0 | ₹51,500,000 | ₹11,004 | ₹11,004 | 12.916045, 77.67519 | Yes (Source) | PASS |
| 49 | NB-8a9f898395c0 | Sobha Magnolia | BTM Layout | 3 | 1900.0 | ₹30,000,000 | ₹15,789 | ₹15,789 | 12.923446, 77.601063 | Yes (Source) | PASS |
| 50 | NB-8a9fba849692 | Candeur Carlisle | Mahadevapura | 3 | 1460.0 | ₹27,000,000 | ₹18,493 | ₹18,493 | 12.997352, 77.690186 | Yes (Source) | PASS |
| 51 | NB-8a9faa8495c6 | *Unavailable* | Rajajinagar | 4 | 1025.0 | ₹28,700,000 | ₹28,000 | ₹28,000 | 12.985607, 77.556465 | Yes (Source) | PASS |
| 52 | NB-8aa9cade9ddc | Malleswaram Mansion | Malleshwaram | 1 | 470.0 | ₹5,500,000 | ₹11,702 | ₹11,702 | 12.994604, 77.571053 | Yes (Source) | PASS |
| 53 | NB-8aa9b7b39e63 | Sizzle Serenity Woods | KR Puram | 4 | 2700.0 | ₹19,900,000 | ₹7,370 | ₹7,370 | 13.001596, 77.73116 | Yes (Source) | PASS |
| 54 | NB-8aa9ba4a9b45 | Sattva Park Cubix | Devanahalli | 3 | 1498.0 | ₹12,500,000 | ₹8,344 | ₹8,344 | 13.241982, 77.720184 | Yes (Source) | PASS |
| 55 | NB-8a9f82827a52 | *Unavailable* | Hebbal | 3 | 1400.0 | ₹9,600,000 | ₹6,857 | ₹6,857 | 13.03185, 77.60813 | Yes (Source) | PASS |
| 56 | NB-8a9f8b8391f4 | Sai Divya Recidency | Marathahalli | 2 | 1045.0 | ₹7,500,001 | ₹7,177 | ₹7,177 | 12.960653, 77.702753 | Yes (Source) | PASS |
| 57 | NB-8a9f8c718e56 | Shilpitha Splendour Annex | Mahadevapura | 3 | 1500.0 | ₹18,000,000 | ₹12,000 | ₹12,000 | 12.984587, 77.688979 | Yes (Source) | PASS |
| 58 | NB-8aa9b3159ba5 | Elv Signature | Whitefield | 2 | 1140.0 | ₹8,500,000 | ₹7,456 | ₹7,456 | 12.975001, 77.759657 | Yes (Source) | PASS |
| 59 | NB-8aa9abed9fbc | *Unavailable* | Banashankari | 2 | 1050.0 | ₹7,000,000 | ₹6,667 | ₹6,666 | 12.912958, 77.5659 | Yes (Source) | PASS |
| 60 | NB-8aa9aa6ea086 | Sobha Hibiscus | Bellandur | 3 | 1770.0 | ₹30,000,000 | ₹16,949 | ₹16,949 | 12.923099, 77.669443 | Yes (Source) | PASS |
| 61 | NB-8aa9b13c9f2b | *Unavailable* | Yelahanka | 2 | 560.0 | ₹3,900,000 | ₹6,964 | ₹6,964 | 13.088214, 77.588306 | Yes (Source) | PASS |
| 62 | NB-8aa9a05b9f12 | Sv Sheshagiri Nilaya | KR Puram | 2 | 1125.0 | ₹9,800,000 | ₹8,711 | ₹8,711 | 13.005157, 77.716542 | Yes (Source) | PASS |
| 63 | NB-8a9fa08393e2 | Nikoo Homes 2 | Thanisandra | 1 | 693.0 | ₹9,000,000 | ₹12,987 | ₹12,987 | 13.06, 77.62 | Yes (Source) | PASS |
| 64 | NB-8aa9b4959f50 | *Unavailable* | Hebbal | 3 | 2450.0 | ₹43,000,001 | ₹17,551 | ₹17,551 | 13.035356, 77.598787 | Yes (Source) | PASS |
| 65 | NB-8a9fd582850f | Abhigruha Aparment | Marathahalli | 2 | 800.0 | ₹6,500,000 | ₹8,125 | ₹8,125 | 12.967768, 77.705278 | Yes (Source) | PASS |
| 66 | NB-8a9f11858865 | Parijatha Apartments | Bellandur | 3 | 1650.0 | ₹16,000,000 | ₹9,697 | ₹9,696 | 12.926625, 77.672428 | Yes (Source) | PASS |
| 67 | NB-8aa9b4ca9c9d | *Unavailable* | Hebbal | 2 | 1200.0 | ₹20,000,000 | ₹16,667 | ₹16,666 | 13.02904, 77.60722 | Yes (Source) | PASS |
| 68 | NB-8a9fd682861b | Ozone Belvedere | Devanahalli | 3 | 1865.0 | ₹14,500,000 | ₹7,775 | ₹7,774 | 13.24372, 77.717241 | Yes (Source) | PASS |
| 69 | NB-8a9faf839625 | Purva Whitehall | Bellandur | 3 | 1984.0 | ₹36,000,000 | ₹18,145 | ₹18,145 | 12.93, 77.68 | Yes (Source) | PASS |
| 70 | NB-8a9f8d8696f5 | Mithuna White Water Apartments, Jakkuru | Hebbal | 3 | 1782.0 | ₹22,500,000 | ₹12,626 | ₹12,626 | 13.032532, 77.598844 | Yes (Source) | PASS |
| 71 | NB-8a9f8ac38e5a | Marvel Residency | Koramangala | 3 | 1846.0 | ₹32,500,000 | ₹17,606 | ₹17,605 | 12.925422, 77.631909 | Yes (Source) | PASS |
| 72 | NB-8aa9bb84a00d | Adarsh Palm Retreat Lake Front | Bellandur | 2 | 1341.0 | ₹27,500,000 | ₹20,507 | ₹20,507 | 12.923495, 77.685107 | Yes (Source) | PASS |
| 73 | NB-8aa997079dec | Prestige Lavender Fields | Varthur | 1 | 669.0 | ₹11,000,000 | ₹16,442 | ₹16,442 | 12.934257, 77.739616 | Yes (Source) | PASS |
| 74 | NB-8aa993f99fc7 | Challamma Residency | Jayanagar | 3 | 1663.0 | ₹32,500,000 | ₹19,543 | ₹19,542 | 12.919491, 77.586437 | Yes (Source) | PASS |
| 75 | NB-8a9f82829cd8 | Tvs Emerald Isle Of Trees | Thanisandra | 4 | 2378.0 | ₹35,000,000 | ₹14,718 | ₹14,718 | 13.061386, 77.62139 | Yes (Source) | PASS |
| 76 | NB-8a9f824390da | *Unavailable* | BTM Layout | 4 | 3000.0 | ₹40,000,000 | ₹13,333 | ₹13,333 | 12.922163, 77.606178 | Yes (Source) | PASS |
| 77 | NB-8aa997f79ab0 | Essem Poetree | Marathahalli | 3 | 1477.0 | ₹24,000,000 | ₹16,249 | ₹16,249 | 12.947636, 77.703747 | Yes (Source) | PASS |
| 78 | NB-8aa9971b9fb1 | Birla Tisya | Rajajinagar | 3 | 1800.0 | ₹36,500,000 | ₹20,278 | ₹20,277 | 12.980229, 77.538274 | Yes (Source) | PASS |
| 79 | NB-8aa9bb529f7e | Prestige Lavender Fields | Varthur | 3 | 1431.0 | ₹21,000,000 | ₹14,675 | ₹14,675 | 12.934257, 77.739616 | Yes (Source) | PASS |
| 80 | NB-8aa9b3f69d04 | Ozone Evergreens | HSR Layout | 2 | 953.0 | ₹14,500,000 | ₹15,215 | ₹15,215 | 12.908471, 77.663383 | Yes (Source) | PASS |
| 81 | NB-8aa9a7929cfb | Birla Tisya | Rajajinagar | 3 | 1800.0 | ₹33,000,000 | ₹18,333 | ₹18,333 | 12.980229, 77.538274 | Yes (Source) | PASS |
| 82 | NB-8aa9c8a69dd3 | *Unavailable* | HSR Layout | 4 | 1500.0 | ₹24,000,000 | ₹16,000 | ₹16,000 | 12.908194, 77.643418 | Yes (Source) | PASS |
| 83 | NB-8a9fa18a9724 | *Unavailable* | Mahadevapura | 1 | 2400.0 | ₹28,000,000 | ₹11,667 | ₹11,666 | 12.995425, 77.672489 | Yes (Source) | PASS |
| 84 | NB-8a9fc082817f | Sri Tirumala Splendour | BTM Layout | 3 | 1449.0 | ₹14,500,000 | ₹10,007 | ₹10,006 | 12.915307, 77.622765 | Yes (Source) | PASS |
| 85 | NB-8aa9ac9f9bfd | *Unavailable* | Kadugodi | 2 | 1246.0 | ₹7,500,000 | ₹6,019 | ₹6,019 | 13.00705, 77.759368 | Yes (Source) | PASS |
| 86 | NB-8a9faa868bef | *Unavailable* | Bellandur | 2 | 1248.0 | ₹10,500,000 | ₹8,413 | ₹8,413 | 12.929865, 77.67353 | Yes (Source) | PASS |
| 87 | NB-ff8081816470 | *Unavailable* | Hebbal | 2 | 825.0 | ₹6,300,000 | ₹7,636 | ₹7,636 | 13.027921, 77.601456 | Yes (Source) | PASS |
| 88 | NB-8a9f9e8399ea | *Unavailable* | Banashankari | 4 | 1344.0 | ₹5,000,000 | ₹3,720 | ₹3,720 | 12.917651, 77.563649 | Yes (Source) | PASS |
| 89 | NB-8aa9b2ce9f6a | Sap Kyros Iris | Whitefield | 2 | 756.0 | ₹9,000,000 | ₹11,905 | ₹11,904 | 12.976858, 77.751846 | Yes (Source) | PASS |
| 90 | NB-8aa9b684a04c | Shigra Palms | Whitefield | 3 | 2096.0 | ₹14,000,000 | ₹6,679 | ₹6,679 | 12.960845, 77.752827 | Yes (Source) | PASS |
| 91 | NB-8aa9b2849fc0 | Bhartiya Nikoo Homes 6 | Yelahanka | 2 | 1325.0 | ₹20,000,000 | ₹15,094 | ₹15,094 | 13.104792, 77.609084 | Yes (Source) | PASS |
| 92 | NB-8a9fe6828873 | Countryside Raindance | Electronic City | 3 | 1580.0 | ₹19,500,000 | ₹12,342 | ₹12,341 | 12.832699, 77.658532 | Yes (Source) | PASS |
| 93 | NB-8aa99c869cbd | Malibu Rivona | Bellandur | 2 | 1130.0 | ₹9,000,000 | ₹7,965 | ₹7,964 | 12.926991, 77.672268 | Yes (Source) | PASS |
| 94 | NB-8aa9b3339f40 | *Unavailable* | Banashankari | 4 | 12000.0 | ₹135,000,000 | ₹11,250 | ₹11,250 | 12.930516, 77.547165 | Yes (Source) | PASS |
| 95 | NB-8aa98a8d9f88 | Blueberry | Indiranagar | 3 | 2200.0 | ₹22,000,000 | ₹10,000 | ₹10,000 | 12.966745, 77.638575 | Yes (Source) | PASS |
| 96 | NB-8a9fbc828176 | *Unavailable* | Hebbal | 4 | 2500.0 | ₹9,500,000 | ₹3,800 | ₹3,800 | 13.02915, 77.601522 | Yes (Source) | PASS |
| 97 | NB-ff8081816970 | Ozone Evergreens | HSR Layout | 2 | 970.0 | ₹18,000,000 | ₹18,557 | ₹18,556 | 12.908965, 77.662871 | Yes (Source) | PASS |
| 98 | NB-8aa9a3c0a061 | Sahith Delight | Bellandur | 2 | 1100.0 | ₹12,500,000 | ₹11,364 | ₹11,363 | 12.927278, 77.669926 | Yes (Source) | PASS |
| 99 | NB-8a9f858395f4 | Gcn Green Springs | Whitefield | 2 | 1180.0 | ₹9,000,000 | ₹7,627 | ₹7,627 | 12.974616, 77.758599 | Yes (Source) | PASS |
| 100 | NB-8aa9bdb89e7c | *Unavailable* | Jayanagar | 2 | 540.0 | ₹4,500,000 | ₹8,333 | ₹8,333 | 12.934047, 77.58754 | Yes (Source) | PASS |
| 101 | NB-8aa99d5a9c4a | Aakruti Amity | Electronic City | 2 | 1700.0 | ₹10,000,000 | ₹5,882 | ₹5,882 | 12.834238, 77.694634 | Yes (Source) | PASS |
| 102 | NB-8aa9b2559f31 | I1 Ashritha Apartment | Koramangala | 2 | 1207.0 | ₹8,500,000 | ₹7,042 | ₹7,042 | 12.918659, 77.63381 | Yes (Source) | PASS |
| 103 | NB-8a9f84c38db0 | Genurise North Park | Yelahanka | 2 | 1059.0 | ₹10,000,000 | ₹9,443 | ₹9,442 | 13.145979, 77.675986 | Yes (Source) | PASS |
| 104 | NB-8a9fa78794cb | Sb | Rajajinagar | 3 | 1350.0 | ₹14,450,000 | ₹10,704 | ₹10,703 | 12.984335, 77.557063 | Yes (Source) | PASS |
| 105 | NB-8aa9972ba0ae | Passcode City | Devanahalli | 2 | 1319.0 | ₹17,100,000 | ₹12,964 | ₹12,964 | 13.24372, 77.717241 | Yes (Source) | PASS |
