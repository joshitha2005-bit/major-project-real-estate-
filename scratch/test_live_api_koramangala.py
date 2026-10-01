import requests

r = requests.get('http://127.0.0.1:8000/api/v1/properties/?query=Koramangala&limit=10')
if r.status_code == 200:
    data = r.json()
    print('Total results:', data['total'])
    for item in data['items'][:10]:
        t = item.get('display_title')
        b = item.get('building_name')
        l = item.get('locality')
        s = item.get('sub_locality')
        conf = item.get('identity_confidence')
        coord = item.get('coordinate_confidence')
        stat = item.get('listing_status')
        addr = item.get('formatted_address')
        print(f"ID {item['id']}: '{t}' | bldg='{b}' | loc='{l}' | sub='{s}' | id_conf={conf} | coord_conf={coord} | stat={stat}")
        print(f"   Addr: {addr}")
else:
    print('Error:', r.status_code, r.text)
