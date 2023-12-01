import json
import os
from typing import Dict, Union

from app.core.schema import ErrorDetail
from fastapi.responses import JSONResponse



def load_errors_from_file():
    with open('app/core/error_code.json', 'r') as file:
        print("Loading errors.")
        error = json.load(file)
    return error

global_list_of_errors_dict: Dict = load_errors_from_file()



def error_detail(error_code):
    
    error_english:str=global_list_of_errors_dict.get(error_code,"")
    if error_english=="": raise Exception("No such error code: "+error_code)
    
    # return json.dumps(ErrorDetail(error_code=error_code, error_english=global_list_of_errors_dict[error_code]).json())
    return ErrorDetail(error_code=error_code, error_english=global_list_of_errors_dict[error_code]).dict()

def err(status_code,detail_code):
    return JSONResponse(status_code=status_code,content=error_detail(detail_code))