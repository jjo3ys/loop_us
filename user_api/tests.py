import requests



data = '{"b_no":["0000000000"]}'

response = requests.post('http://api.odcloud.kr/api/nts-businessman/v1/status', headers=headers, params=params, data=data)

if response.json()['data'][0]['tax_type'] == '국세청에 등록되지 않은 사업자등록번호입니다.':
    print('등록 불가')

