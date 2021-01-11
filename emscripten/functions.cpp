#include <emscripten.h>
#include <emscripten/bind.h>
#include <emscripten/val.h>
#include <string>
#include <vector>
#include <numeric>
#include <cmath>
#include <map>
#include <iostream>
#include <fstream>
#include <algorithm>
#include <set>
#include <cstdio>
using namespace std;
using namespace emscripten;

int count = 0;
double sumOfRatings = 0;

map<string, set<string>> usersThatRatedProduct;
map<string, set<string>> productsRatedPerUser;
map<pair<string, string>, float> ratings;


double mean(){
    return sumOfRatings/::count;
}

void addRating(const string& Product, const string& User, const float& Rating){
    pair<string, string> Product_User(Product, User);
    if(ratings.count({Product_User})){
        sumOfRatings += Rating - ratings[Product_User];
    }
    else {
        ::count += 1;
        sumOfRatings += Rating;
        productsRatedPerUser[User].insert(Product);
        usersThatRatedProduct[Product].insert(User);
    }
    ratings[Product_User] = Rating;
}


void deleteRating(const string& Product, const string& User){
    map<pair<string, string>, float>::iterator Iterator = ratings.find({Product, User});
    if( Iterator != ratings.end() ){
        sumOfRatings -= ratings[{Product, User}];
        ::count -= 1;
        ratings.erase(Iterator);
        productsRatedPerUser[User].erase(Product);
        if( productsRatedPerUser[User].size() == 0 ) {
            productsRatedPerUser.erase(User);
        }
        usersThatRatedProduct[Product].erase(User);
        if( usersThatRatedProduct[Product].size() == 0 ) {
            usersThatRatedProduct.erase(Product);
        }
    }
}

double getRating(const string& Product, const string& User){
    if(ratings.count({Product, User})) return ratings[{Product, User}];
    return mean();
}

double distance(const string& User1, const string& User2){
    set<string>products = productsRatedPerUser[User1];
    set<string> &productOfUser2 = productsRatedPerUser[User2];
    products.insert(productOfUser2.begin(), productOfUser2.end());
    double sum_ = 0;
    for(auto product: products){
        sum_ += getRating(product, User1) - getRating(product, User2);
    }
    return sum_/products.size();
}
int K = 5;
double estimation(const string& User, const string& Product){
    set<string> users = usersThatRatedProduct[Product];
    vector<pair<double, string>> distances;
    for(const string &userCompared: users){
        if(productsRatedPerUser[userCompared].size()) distances.push_back({distance(User, userCompared), userCompared});
    }
    double sum_ = 0;
    sort(distances.begin(), distances.end());
    if (distances.size()){
        if(distances.size()>K){
            distances.resize(K);
        }
        for(const auto &distance: distances){
            sum_ += ratings[{Product, distance.second()}];
        }
        return sum_/distances.size();
    }
    return mean();
}

int sum(const val& list_) {
    vector<int> list = convertJSArrayToNumberVector<int>(list_);
    return std::accumulate(list.begin(), list.end(), 0);
}

val getEstimations(const val &estimationsRequest){
    vector<val>arrayOfEstimationsRequest = vecFromJSArray<val>(estimationsRequest);
    vector<vector<string>> CPPFormatOfEstimationRequest;
    for(val &iterator: arrayOfEstimationsRequest){
        CPPFormatOfEstimationRequest.push_back(vecFromJSArray<string>(iterator));
    }
    vector<double> estimations(arrayOfEstimationsRequest.size());

    return val::array(estimations);
}

double rmse(const val& list_1, const val& list_2) {
    vector<double> list1 = convertJSArrayToNumberVector<double>(list_1);
    vector<double> list2 = convertJSArrayToNumberVector<double>(list_2);
    double sum_ = 0;
    for(std::size_t iterator = 0; iterator < list1.size(); iterator++){
        sum_ += pow(list1[iterator] - list2[iterator], 2);
    }
    return sqrt( sum_/list1.size() );
}

int init(int howMany){
    EM_ASM(
        FS.mkdir('/temp');                         // (1)
        FS.mount(NODEFS, {root : '.'}, '/temp');); // (2)
    ifstream input("/temp/ratings_Books.csv");
    string line;
    float rating;
    char Product_C[100], User_C[100];
    string Product;
    string User;
    int Counting = 0;
    while(getline(input, line)) {
        if (Counting++ >= howMany) break;
        sscanf(line.c_str(), "%[^,],%[^,],%f,%*s", Product_C, User_C, &rating);
        Product = Product_C;
        User = User_C;
        // cout << User << endl;
        // cout << Product <<endl;
        // cout << line <<endl;
        // cout << rating << endl;
        addRating(Product, User, rating);
    }
    return ::count;
}

EMSCRIPTEN_BINDINGS(my_module) {
    emscripten::function("sum", &sum);
    emscripten::function("rmse", &rmse);
    emscripten::function("getEstimations", &getEstimations);
    emscripten::function("addRating", &addRating);
    emscripten::function("deleteRating", &deleteRating);
    emscripten::function("mean", &mean);
    emscripten::function("init", &init);

    
    emscripten::register_vector<double>("vector<double>");
    emscripten::register_vector<string>("vector<string>");
    emscripten::register_vector<vector<string>>("vector<vector<string>>");
    emscripten::register_vector<pair<string, string>>("vector<pair<string, string>>");

}
