import json
import requests

headers = {
    'Accpet':'application/json',
    'Authorization':'frbSEAcXD+a6UEOUq1lkWcWmFoDku20SZvLeO++pP9e5yQo5GIqTkbVbctqafewScJuzLLcTW/l4d/Lw/wjOig==',
    'Content-Type': 'application/json',
}

params = (
    ('serviceKey', 'frbSEAcXD+a6UEOUq1lkWcWmFoDku20SZvLeO++pP9e5yQo5GIqTkbVbctqafewScJuzLLcTW/l4d/Lw/wjOig=='),
)
a = input()
a_data = {"b_no":["{0}".format(a)]}
a_data = json.dumps(a_data)

data = '{"b_no":["0000000000"]}'

response = requests.post('http://api.odcloud.kr/api/nts-businessman/v1/status', headers=headers, params=params, data=a_data)

if response.json()['data'][0]['tax_type'] == '국세청에 등록되지 않은 사업자등록번호입니다.':
    print('등록 불가')

