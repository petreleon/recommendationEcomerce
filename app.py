import sys

from flask import Flask
from flask import request
from flask_cors import CORS
from bson.json_util import dumps
import json

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
from nDimensionalKNN_copy import *
@app.route('/recommendations', methods=['GET'])
def home(): 
    print(request.args)
    try:
        command = request.args["command"]
        if command == "getRecommendationRelatedToSpecifiedProduct":
            try:
                product = request.args.get("product")
                try:
                    return {
                        "response": tuple(recommendationOfProductsByProduct(product))
                    }
                except Exception:
                    return {"EXCEPT":str(sys.exc_info())}
            except:
                return {
                    "error":"No product specified"
                }
        
        if command == "getRecommendationRelatedToSpecifiedUser":
            try:
                user = request.args.get("user")
            except:
                return {
                    "error":"No user specified"
                }
            try:
                return {
                    "response": tuple(recommendationOfProductsByUser(user))
                }
            except Exception:
                return {"EXCEPT":str(sys.exc_info())}
            
            
    except:
        return {
            "error":"No command specified"
        }

@app.route('/rating', methods=['GET'])
def getRatingRoute():
    data = request.args
    # user and product
    if set({'user', 'product'}).issubset(data):
        user = data['user']
        product = data['product']
        responseDB = getRatingDB(user, product)
        return dumps(responseDB)
    if 'user' in data:
        user = data['user']
        responseDB = getRatingsByUser(user)
        return dumps(responseDB)

    if 'product' in data:
        product = data['product']
        responseDB = getRatingsByProduct(product)
        return dumps(responseDB)
    
    return {
            "error":"No user and/or product specified"
        }
    

@app.route('/rating', methods=['DELETE'])
def deleteRatingRoute():
    data = request.args
    # user and product
    if set({'user', 'product'}).issubset(data):
        user = data['user']
        product = data['product']
        responseDB = deleteRatingDB(user, product)
        return dumps(responseDB.raw_result)
    if 'user' in data:
        user = data['user']
        responseDB = deleteRatingByUser(user)
        return dumps(responseDB.raw_result)
    if 'product' in data:
        product = data['product']
        responseDB = deleteRatingByProduct(product)
        return dumps(responseDB.raw_result)
    
    return {
            "error":"No user and/or product specified"
        }

@app.route('/rating', methods=['POST', 'PUT'])
def addRatingRoute():
    data = json.loads(request.data.decode('UTF-8'))
    try:
        user = data['user']
    except:
        return {
            "error":"No user specified"
        }
    try:
        product = data['product']
    except:
        return {
            "error":"No product specified"
        }
    try:
        rating = data['rating']
    except:
        return {
            "error":"No rating specified"
        }
    try:
        dataToReturn = addRatingDB(user, product, rating)
    except:
        return {
            "error":"adding not allowed"
        }
    return dumps(dataToReturn.raw_result)

    
if __name__ == '__main__':
    app.run()