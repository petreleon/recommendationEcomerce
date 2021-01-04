from collections import defaultdict
import math
from copy import copy
import matplotlib.pyplot as plot
from statistics import mean
import csv
import random

sum_ = 0
iterations = 0

def sum_perIterations():
    return sum_/iterations
K=10
userRatings = dict()
productRatings = dict()

def addRating(userID, productID, rating):
    global sum_, iterations
    if userID not in userRatings.keys():
        userRatings[userID] = dict()
    if productID not in productRatings:
        productRatings[productID] = dict()
    if productID in userRatings[userID].keys():
        sum_ += rating - userRatings[userID][productID]
    else:
        sum_ += rating
        iterations += 1
    userRatings[userID][productID] = rating
    productRatings[productID][userID] = rating

def deleteRating(userID, productID):
    global sum_, iterations
    if userID in userRatings.keys():
        if productID in userRatings[userID].keys():
            sum_ -= userRatings[userID][productID]
            del userRatings[userID][productID]
            del productRatings[productID][userID]


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
# print(rootMeanSquaredError([1,3],[2,4]))

list_of_ratings = list()
with open('ratings_Books.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        try:
            list_of_ratings.append((row[0], row[1], float(row[2])))
        except:
            print(row)

list_of_ratings = list_of_ratings[:100000]
random.shuffle(list_of_ratings)
splitter = len(list_of_ratings)*70//100
train, test = list_of_ratings[:splitter], list_of_ratings[splitter:]
for user,product,rating in train:
    addRating(user, product, rating)

print(iterations)

prediction = [getPrediction2(user, product) for user, product, _ in test]
prediction_test = [real_value for _, _, real_value in test]
random_prediction = [random.randint(1,5) for _ in range(len(test))] 
print(rootMeanSquaredError(prediction, prediction_test))
print(rootMeanSquaredError(random_prediction, prediction_test))
