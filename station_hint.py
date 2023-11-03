import requests
import json
import re

def GetHints(station_short_str: str):
    url = "https://idos.idnes.cz/vlakyautobusymhdvse/Ajax/SearchTimetableObjects"
    url = "https://idos.idnes.cz/ostrava/Ajax/SearchTimetableObjects"

    querystring = {"callback":"jQuery","count":"3","prefixText":station_short_str,"searchByPosition":"false","onlyStation":"false","format":"json"}

    payload = ""
    headers = {
        "cookie": "Idos4=DId=WoEEDlGBVeGFMevBT9Ryt7Z+Quha2YZXKUjo7EMcNsnzlt5QwiYQgQ==&LS=ZIQdlw6zEyldp5HNOVvWlyOzt2oW97mnHN/nMWnLmfprxYUKlsKllfKSi8wkExpXEd55KhWsLKOLxCBCrPb3Eg==; personalizace=setver=full&sp=2442490069104306; _webid=2.f7f7ae9e2e.1664319406.1664319406; _ga=GA1.2.1515798913.1664312208; _ga=GA1.3.1515798913.1664312208; euctmp=CPajhsAPajhsAAHABBENCTCgAP_AAH_AAATIHfoBpDxkBSFCAGJoYtkwAAAGxxAAICACABAAoAAAABoAIAQAAAAQAAAgBAAAABIAIAIAAABAGEAAAAAAQAAAAQAAAEAAAAAAIQIAAAAAAiBAAAAAAAAAAAAAAABAQAAAgAAAAAIAQAAAAAEAgAAAAAAAAAAABAAAAQganAoAAWABUAC4AHAAQAAyABoADmAIgAigBMACeAFUALgAYgAzAB-AEJAIgAiQBHAClAFiAMsAZsA7gDvAH6AQgAiwBaQC6gGBANYAdQA-QCQQE2gLUAXmAyQBpQDUwBA0AGAAII0CIAMAAQRoFQAYAAgjQMgAwABBGgAA.f_gAD_gAAAAA; AMCVS_2C2555935C79EB590A495E90^%^40AdobeOrg=1; cpex2ibb=seg^%^3D3014904; aam_uuid=90287049809936262293977602180212916953; __gfp_64b=EGjGg2eSOmLduyePpCezTehqmU.Y6Njm7OenfNP1U.H.d7^|1664312220; lastAdSyncDate=1664917511242; __gads=ID=a28332d88b39ef3f-228c2a9a3bce005f:T=1664917518:RT=1664917518:S=ALNI_MZ9OBpkbBMwC9nJSYPVsIrS5tKJhg; AMCV_2C2555935C79EB590A495E90^%^40AdobeOrg=-1124106680^%^7CMCIDTS^%^7C19270^%^7CMCMID^%^7C90124907121509349433994098921332168499^%^7CMCAAMLH-1665522330^%^7C6^%^7CMCAAMB-1665522330^%^7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y^%^7CMCOPTOUT-1664924730s^%^7Cpartner^%^2Cpartner^%^7CvVersion^%^7C5.2.0^%^7CMCCIDH^%^7C-869045355; __gsync_gdpr=1:YTU6bjpuOjE2NjQ5MTc1NDk3NjM6bjpu; cto_bundle=zyubhF8lMkJsbENFWVQyQ2c1Ym4lMkJkb0l0VFQzWWt1OTd6aXdaT3VjVGlPSyUyQmVCeG1ZR2NrTERxYWhWRW9IR1lLJTJGQXdoZmJJaUolMkZ1V05zcTlIdlhMZWlaTWwxdzFkMnBPJTJCOUFqVk9UYkdtZVoxV2tHdmZQUmZzZTRUZkpBZzJGOFRXQlc0eVNybDZmMEVNNlB1aCUyQjh6cVY4SHVxdyUzRCUzRA; webidsync=1665700766905; _gid=GA1.2.1100156879.1665700767; _gid=GA1.3.1100156879.1665700767; euconsent-v2=CPgejgAPgejgAAHABBENCjCgAAAAADwAAATIDTQBgAFgAWADKAT0AtIBpgFpgBAALALSAIGgAwABBIIRABgACCQQqADAAEEghkAGAAIJBAAA.YAAAB4AAAAAA; myId5=ID5*FdS-E2wNOvthb39rAVaoyuEm9wR4HDmc4nv5VuEhdVYluPpP8RQLc6svDSpth3iuJbooKJLh2CDJVa5UWQhvQSW9QNpBIAe9wmmEIb7mYnMlvsEsWFQTzsCCp_wYgGalJcNeB3F5wmOuT84JPdZq7CXIsaLZNaKzui5LShdSs_MlymEx7txqmgtG-IZv5dtUJdP3Bt1rAZiV9iOLcnNDxiXVBldkxokZ7Il0E2bRFYQl1vChhlgrA0nvCmsMt9ej; dCMP=mafra=0000,cpex=0,google=0,gemius=0,adobe=0,id5=0,next=0000,onlajny=0000,jenzeny=0000,databazeknih=0000,autojournal=0000,skodahome=0000,skodaklasik=0000,groupm=0,",
        "authority": "idos.idnes.cz",
        "accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
        "accept-language": "en,cs-CZ;q=0.9,cs;q=0.8",
        "referer": "https://idos.idnes.cz/vlakyautobusymhdvse/spojeni/vysledky/?date=15.10.2022&time=02:01&f=Horn^%^C3^%^AD^%^20Polanka&fc=303003&t=V^%^C5^%^A0B-TUO&tc=303003",
        "sec-ch-ua": "^\^Google"
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    r = re.match(r"^jQuery\((.*)\);", response.text)

    hints = json.loads(r[1])
    # print(r[1])
    # print("")

    names = list()
    for hint in hints:
        # print(hint["text"])
        # print(hint["lines"])
        names.append(hint["text"])

    return names