#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys
from ibmcloudant.cloudant_v1 import Document, CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException
import requests


def main(dict):
    databaseName = "reviews"
    CLOUDANT_APIKEY = ''
    CLOUDANT_URL = ''
    
    try:
        authenticator = IAMAuthenticator(CLOUDANT_APIKEY)

        client = CloudantV1(authenticator=authenticator)

        client.set_service_url(CLOUDANT_URL)
        
        if 'dealerId' in dict.keys():
            sel = {
                "dealership": int(dict['dealerId'])
            }
    
            result = client.post_find(db=databaseName,selector=sel).get_result()['docs']
            if len(result) > 0:
                refined_result = list(map(refine, result))
    
    
                return {"reviews": refined_result}
            
            else:
                return {"error": {
                    "statusCode": 404,
                    "message": "dealerId does not exist"
                }}
    
        elif 'id' in dict.keys():
            reviews_doc = Document(
            ID=dict['id'],
            name=dict['name'],
            dealership=dict['dealership'],
            review=dict['review'],
            purchase=True if dict['purchase'] == "true" else False,
            another=dict['another'],
            purchase_date=dict['purchase_date'],
            car_make=dict['car_make'],
            car_model=dict['car_model'],
            car_year=dict['car_year']
            )

            response = client.post_document(db=databaseName, document=reviews_doc).get_result()
            return {"response": response}
        
        else: 
            return {"error": {
            "statusCode": 500,
            "message": "Something went wrong on the server"
        }}


        
    except ApiException as ce:
        return {"error": {
            "statusCode": 500,
            "message": "Something went wrong on the server"
        }}
    
    except (requests.exceptions.RequestException, ConnectionResetError) as err:
        print("connection error")
        return {"error": err}

    
    
def refine(res): 
    res.pop('_id')
    res.pop('_rev')
    return res


