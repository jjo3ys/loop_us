from django.conf.global_settings import DATE_INPUT_FORMATS
import requests
import json

key = 'frbSEAcXD%2Ba6UEOUq1lkWcWmFoDku20SZvLeO%2B%2BpP9e5yQo5GIqTkbVbctqafewScJuzLLcTW%2Fl4d%2FLw%2FwjOig%3D%3D'
data = {   
    "b_no":[
        "2208162517"
    ]
}
params = {}
# data = json.dumps(data)
res = requests.post('http://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey=frbSEAcXD%2Ba6UEOUq1lkWcWmFoDku20SZvLeO%2B%2BpP9e5yQo5GIqTkbVbctqafewScJuzLLcTW%2Fl4d%2FLw%2FwjOig%3D%3D', data=data)
print(res.json())
