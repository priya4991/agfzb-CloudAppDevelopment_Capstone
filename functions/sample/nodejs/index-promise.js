/**
  *
  * main() will be run when you invoke this action
  *
  * @param Cloud Functions actions accept a single parameter, which must be a JSON object.
  *
  * @return The output of this action, which must be a JSON object.
  *
  */

const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');
function main(params) {
    const IAM_API_KEY = '';
    const COUCH_URL = '';
    const authenticator = new IamAuthenticator({ apikey: IAM_API_KEY })
    const cloudant = CloudantV1.newInstance({
        authenticator: authenticator
    });
    cloudant.setServiceUrl(COUCH_URL);
    if (Object.keys(params).length > 0 && params.state) {
        const sel = {
            st: params.state
        };
        return new Promise((resolve, reject) => {
            cloudant.postFind({ db: 'dealerships', selector: sel })
                .then((result) => {
                    if (result.result.docs.length > 0) {
                        const mapping = result.result.docs.map(r => {
                            //eliminating _id and _rev from the response
                            const { _id, _rev, ...y } = r;
                            return y;
                        });
                        resolve({ result: mapping });

                    }
                    else {
                        reject({
                            err: {
                                "statusCode": 404,
                                "message": "The state does not exist"
                            }
                        });
                    }
                })
                .catch(err => {
                    console.log(err);
                    reject({
                        err: {
                            "statusCode": 500,
                            "message": "Something went wrong on the server"
                        }
                    });
                });
        });


    } else {
        return new Promise((resolve, reject) => {
            cloudant.postAllDocs({ db: 'dealerships', includeDocs: true, limit: 10 })
                .then((result) => {
                    console.log(result)
                    if (result.result.rows.length > 0) {
                        const mapping = result.result.rows.map(r => {
                            //eliminating _id and _rev from the response
                            const { _id, _rev, ...y } = r.doc;
                            return y;
                        });
                        resolve({ result: mapping });
                    }
                    else {
                        reject({
                            err: {
                                "statusCode": 404,
                                "message": "The database is empty"
                            }
                        });
                    }
                })
                .catch(err => {
                    console.log(err);
                    reject({
                        err: {
                            "statusCode": 500,
                            "message": "Something went wrong on the server"
                        }
                    });
                });
        });

    }
}
