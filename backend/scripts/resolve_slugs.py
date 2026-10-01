import urllib.request
import ssl
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

candidates = {
    'MG Road': ['mg-road', 'mahatma-gandhi-road'],
    'Brigade Road': ['brigade-road'],
    'Commercial Street': ['commercial-street', 'tasker-town', 'shivajinagar'],
    'Shivajinagar': ['shivajinagar', 'shivaji-nagar'],
    'Gandhinagar': ['gandhi-nagar', 'gandhinagar'],
    'Shanthi Nagar': ['shanthi-nagar', 'shanthinagar'],
    'Chamarajpet': ['chamarajpet', 'chamarajapete'],
    'Chickpet': ['chickpet', 'chikpet'],
    'Majestic': ['majestic', 'gandhi-nagar'],
    'Vasanth Nagar': ['vasanth-nagar', 'vasanthanagar'],
    'Lavelle Road': ['lavelle-road', 'shanthi-nagar'],
    'Richmond Town': ['richmond-town'],
    'Frazer Town': ['frazer-town', 'pulikeshi-nagar'],
    'RR Nagar': ['rr-nagar', 'rajarajeshwari-nagar'],
    'Peenya': ['peenya', 'peenya-industrial-area'],
    'Dasarahalli': ['dasarahalli', 't-dasarahalli'],
    'Govindrajnagar': ['govindraj-nagar', 'govindaraja-nagar'],
    'Mahalakshmi Layout': ['mahalakshmi-layout'],
    'Nagarbhavi': ['nagarbhavi'],
    'Basaveshwara Nagar': ['basaveshwar-nagar', 'basaveshwaranagar'],
    'Yeshwanthpur': ['yeshwanthpur', 'yeshwantpur'],
    'Yelahanka New Town': ['yelahanka-new-town'],
    'Yelahanka Old Town': ['yelahanka-old-town', 'yelahanka'],
    'Byatarayanapura': ['byatarayanapura'],
    'RT Nagar': ['rt-nagar', 'r-t-nagar'],
    'Jakkur': ['jakkur'],
    'Sahakara Nagar': ['sahakara-nagar', 'sahakaranagar'],
    'Vidyaranyapura': ['vidyaranyapura'],
    'Mathikere': ['mathikere', 'mattikere'],
    'Sanjaynagar': ['sanjay-nagar', 'sanjaynagar'],
    'Bommanahalli': ['bommanahalli'],
    'Uttarahalli': ['uttarahalli'],
    'Kumaraswamy Layout': ['kumaraswamy-layout'],
    'Padmanabhanagar': ['padmanabha-nagar', 'padmanabhanagar'],
    'CV Raman Nagar': ['cv-raman-nagar', 'c-v-raman-nagar'],
    'Brookefield': ['brookefield', 'brookfield'],
}

resolved = {}
for loc, slugs in candidates.items():
    found = False
    for s in slugs:
        u = f"https://www.nobroker.in/properties-for-sale-in-{s}-bangalore"
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=4) as r:
                if r.getcode() == 200:
                    resolved[loc] = s
                    found = True
                    break
        except Exception:
            pass
    if not found:
        for s in slugs:
            u = f"https://www.nobroker.in/properties-for-rent-in-{s}-bangalore"
            try:
                req = urllib.request.Request(u, headers=headers)
                with urllib.request.urlopen(req, context=ctx, timeout=4) as r:
                    if r.getcode() == 200:
                        resolved[loc] = s
                        found = True
                        break
            except Exception:
                pass
    if found:
        print(f"[RESOLVED] {loc} -> {resolved[loc]}", flush=True)
    else:
        print(f"[UNRESOLVED] {loc}", flush=True)

import json
with open('backend/scripts/resolved_slugs.json', 'w') as f:
    json.dump(resolved, f, indent=2)
print("Finished slug resolution.", flush=True)
