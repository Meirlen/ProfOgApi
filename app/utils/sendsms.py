import requests


def send_sms(code,phone):
    print(code,phone)
    app_hash = "UgngZHxDDxj" # prod
    mobizone_token = "kza1fe1aef2adaf485a3cfdf69c89f6ba61cfe23ca2fb47c7601efdc8d34760fc30e21"
    # app_hash = "jg9AkTD8yOw" # debug

    message  = 'Sapar KZ код: '+str(code)+' '+app_hash

    response = requests.get(
            url='https://api.mobizon.kz/service/message/sendsmsmessage?apiKey='+mobizone_token+'&recipient='+phone+'&text='+message,
        )

    print(response)