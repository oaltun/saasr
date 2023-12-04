import os
import requests
import time
import json
from datetime import datetime
from app.core.error import error_detail


from fastapi import status, HTTPException

from app.config import settings
headers = {
    "accept":"application/json",
    "api-key": settings.SENDINBLUE_API_KEY,
    "content-type": "application/json"
}
url = "https://api.sendinblue.com/v3/smtp/email"

# Send mail to a single person. 
# Based on https://developers.sendinblue.com/docs/batch-send-transactional-emails
def send_mail_or_424(subject, html_content,sender_email,sender_name, to_email,to_name=None):

    if os.environ.get('IS_TESTING')== "true":
        print("Since testing, mail is not sent")
        return
    
    to_dict = dict(email=to_email)
    if to_name:
        to_dict["name"]=to_name

    data = {
            "sender":{
                "email":sender_email,
                "name" :sender_name
            },
            "subject":subject,
            "htmlContent":html_content,
            "messageVersions":[
                {
                    "to":[to_dict],
                },
            ]
    }

    json_str = json.dumps(data)
    print("Start sending mail at time:", datetime.now())
    r = requests.post(url,data=json_str,headers=headers)
    print("r.status_code: ",r.status_code)
    print("r.json: ", r.json())
    print("r.headers: ",r.headers)
    print("End sending mail")
    
    if r.status_code >= 400:
        print("7b298403")
        raise HTTPException(
            status_code=r.status_code,
            detail=error_detail("USERNAME_OR_PASSWORD_INCORRECT")
        )
 
