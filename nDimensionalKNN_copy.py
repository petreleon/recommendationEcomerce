from collections import defaultdict
import math
from copy import copy
import matplotlib.pyplot as plot
from statistics import mean
import csv
import random
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client.testing_database
collection = db.test_shop
collection.create_indexes([
    pymongo.IndexModel([("product",pymongo.ASCENDING)]),
    pymongo.IndexModel([("user",pymongo.ASCENDING)]),
    pymongo.IndexModel([("product",pymongo.ASCENDING), ("user",pymongo.ASCENDING)]),
])

#to do:
# de inlocuit functia add cu una de adaugare in baza de date
# extrage din baza de date doar ratingurile care de care e nevoie pentru predictie

sum_ = 0
iterations = 0

def sum_perIterations():
    return sum_/iterations
K=20
userRatings = dict()
productRatings = dict()

def addRating(userID, productID, rating):
    global sum_, iterations
    if userID not in userRatings.keys():
        userRatings[userID] = dict()
    if productID in userRatings[userID].keys():
        sum_ += rating - userRatings[userID][productID]
    else:
        sum_ += rating
        iterations += 1
    userRatings[userID][productID] = rating

def deleteRating(userID, productID):
    global sum_, iterations
    if userID in userRatings.keys():
        if productID in userRatings[userID].keys():
            sum_ -= userRatings[userID][productID]
            del userRatings[userID][productID]
            iterations -= 1

def deleteAll():
    global sum_, iterations, userRatings
    userRatings.clear()
    sum_ = 0
    iterations = 0
    


userRatings_update = {
    "a":{1:2, 2:5},
    "b":{1:3, 2:3, 3:1, 4:5}
}

# for user in userRatings_update.keys():
#     for product in userRatings_update[user].keys():
#         addRating(user, product, userRatings_update[user][product])


# userRatings["a"][4]

def getDistancefromUser(userID_1, userID_2):
    distance = 0
    for rating_ in set(userID_1.keys()).union(userID_2.keys()):
        distance += pow(userID_1.get(rating_, sum_perIterations()) - userID_2.get(rating_, sum_perIterations()),2)
    return pow(distance,1/2)
# print(getDistancefromUser(userRatings["a"],userRatings["b"]))

def getProductMeanRecommendations(productID, listOfUsers):
    product_sum = 0
    product_count = len( listOfUsers )
    for user in listOfUsers:
        product_sum += userRatings[user].get(productID, sum_perIterations())
    try:
        return product_sum/product_count
    except:
        return sum_perIterations()

def getKNearestNeighbors(userID, filter_ = lambda X: X):
    distanceDict = dict()
    for differentUserID in filter_(userRatings): 
        if differentUserID != userID:
            try:
                distanceDict[differentUserID] = getDistancefromUser(userRatings[userID], userRatings[differentUserID])
            except:
                pass
    return sorted(distanceDict.keys(), key=lambda X: distanceDict[X])[:K]

def getNRecommendationsFromKNN(userID, numberOfRecommendations):
    KNN = getKNearestNeighbors(userID)
    possibleProducts = set()
    possibleProductsDict = dict()
    for neighbor in KNN:
        possibleProducts.update(userRatings[neighbor].keys())
    possibleProducts.difference_update(userRatings[userID].keys())
    for product in possibleProducts:
        possibleProductsDict[product] = getProductMeanRecommendations(product, KNN)
    for neighbor in KNN:
        for product in possibleProducts:
            possibleProductsDict[product] += userRatings.get(product, sum_perIterations())
    return sorted(possibleProducts, key=lambda product: possibleProductsDict[product], reverse=True)[:numberOfRecommendations]
# prima abordare
def getPrediction(userID, productID):
    KNearestNeighbors = getKNearestNeighbors(userID)
    return getProductMeanRecommendations(productID, KNearestNeighbors)
# a doua abordare ar fi cei mai apropriati care au dat review la produsul respectiv
def getPrediction2(userID, productID):
    KNearestNeighbors = getKNearestNeighbors(userID, lambda users: [user for user in users if productID in userRatings[user].keys() ] )
    return getProductMeanRecommendations(productID, KNearestNeighbors)


# print("prediction:",getPrediction2("a", 4))

# print(getKNearestNeighbors("a"))
# print(getNRecommendationsFromKNN("a", 2))
# print(sum_, iterations)
# deleteRating("b", 3)
# print(userRatings)
def rootMeanSquaredError(predictions: list, realities: list):
    return math.sqrt(mean([(prediction-reality)**2 for prediction, reality in zip(predictions, realities)]))

def average():
    return list(collection.aggregate([{
        "$group":{
            "_id":1,
            "average":{"$avg":"$rating"}
        }
    }]))[0]["average"]

# print(rootMeanSquaredError([1,3],[2,4]))
import pprint
if __name__ == '__main__':
    list_of_ratings = list()
    with open('ratings_Books.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for index, row in enumerate(csv_reader):
            # if index == 1000000:
            #     break
            try:
                list_of_ratings.append({"product":row[0], "user":row[1], "rating":float(row[2])})
            except:
                print(row)
        
    # list_of_ratings = list_of_ratings
    random.shuffle(list_of_ratings)
    splitter = len(list_of_ratings)*70//100
    train, test = list_of_ratings[:splitter], list_of_ratings[splitter:]
    collection.insert_many(train)
    # for product,user,rating in train:
    #     addRating(user, product, rating)
    # find the users that rewviewed a the product
    # then find the products that are rated by filtered users
    average_value = average()
    prediction_list = []
    real_list = []
    for review in test:
        # print(average())
        product, user, rating = review['product'], review['user'], review['rating']
        real_list.append(rating)
        users = [review['user'] for review in list(collection.aggregate([
            {"$match":{"product":product}},
        ]))]
        # pprint.pprint(users)
        related_reviews = list(collection.aggregate([
            {"$match":{"user":{"$in":users}, "product":{"$ne":product}}}
        ]))
        own_reviews = list(collection.aggregate([
            {"$match":{"user":{"$eq":user}, "product":{"$ne":product}}}
        ]))
        if len(related_reviews) == 0:
            prediction_list.append(average_value)
        elif len(own_reviews) == 0:
            prediction_list.append(list(collection.aggregate([
                {"$match":{"product":product}},
                {"$group":
                    {
                        "_id":1,
                        "average":{"$avg":"$rating"}
                    }
                }
            ]))[0]["average"])
        else:
            for review_iteration in own_reviews + related_reviews:
                addRating(review_iteration["user"], review_iteration["product"], review_iteration["rating"])
            prediction_list.append(getPrediction(user, product))
            deleteAll()
        # pprint.pprint(related_reviews)
    print("RMSE:", rootMeanSquaredError(real_list, prediction_list))
