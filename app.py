from flask import Flask, request, jsonify
import redis
from rq import Queue
import time
import numpy as np 
import pickle
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
CORS(app)

r = redis.Redis()
q = Queue(connection=r)

def background_task(n):

    """ Function that returns len(n) and simulates a delay """

    delay = 2

    print("Task running")
    print(f"Simulating a {delay} second delay")

    time.sleep(delay)

    print(len(n))
    print("Task complete")

    return len(n)

models = ['model_5s',
 'model_6s',
 'model_7',
 'model_iphone_11',
 'model_iphone_11_pro',
 'model_iphone_11_pro_max',
 'model_iphone_12',
 'model_iphone_12_pro',
 'model_iphone_12_pro_max',
 'model_iphone_12_mini',
 'model_iphone_13',
 'model_iphone_13_pro',
 'model_iphone_13_pro_max',
 'model_iphone_13_mini',
 'model_iphone_5',
 'model_iphone_5c',
 'model_iphone_5s',
 'model_iphone_6',
 'model_iphone_6_plus',
 'model_iphone_6s',
 'model_iphone_6s_plus',
 'model_iphone_7',
 'model_iphone_7_plus',
 'model_iphone_8',
 'model_iphone_8_plus',
 'model_iphone_se',
 'model_iphone_se_(2._generation)',
 'model_iphone_se_2',
 'model_iphone_se_2020',
 'model_iphone_x',
 'model_iphone_xr',
 'model_iphone_xs',
 'model_iphone_xs_max',
 'model_se',
 'model_xs',
 'model_xs_max']

# todo:'model_iphone_se_(2._generation)','model_iphone_se_2','model_iphone_se_2020', should be the same !take model_iphone_se_2 as in th ui
# also remove model_7

colors = [
 'color_blau',
 'color_gelb',
 'color_gold',
 'color_grau',
 'color_grün',
 'color_nan',
 'color_rosa',
 'color_rot',
 'color_schwarz',
 'color_silber',
 'color_spacegrau',
 'color_weiß']

memory = [
 'memory_1TB',
 'memory_128GB',
 'memory_16GB',
 'memory_256GB',
 'memory_32GB',
 'memory_512GB',
 'memory_64GB',
 'memory_8GB',
 'memory_Nichtzutreffend',
 'memory_nan']

return_policy = [
 'return_policy_Keine_Rücknahme',
 'return_policy_Verbraucher_können_den_Artikel_zu_den_unten_angegebenen_Bedingungen_zurückgeben',
 'return_policy_Verbraucher_können_den_Artikel_zu_den_unten_angegebenen_Bedingungen_zurückgeben_Käufer_zahlt_Rückversand' ]
 
#'no_feedback_yet',
# 'price',
# 'shipping_cost',
# 'number_of_reviews',
# 'number_of_photos',
# 'selers_feedback'

model = pickle.load(open('finalized_model.sav', 'rb'))
columns = pickle.load(open("columns.sav", 'rb'))
mean_prices = pickle.load(open("mean_prices", 'rb'))
median_active_days = pickle.load(open("median_active_days", 'rb'))



#req_test = {"model": "model_iphone_7", "color": "color_schwarz", "memory": 32, "return_policy": "return_policy_no_return", "no_feedback_yet": 0, "selers_feedback": 100, "price": 190, "shipping_cost": 0, "number_of_reviews": 2, "number_of_photos": 1}


        
def set_mean_price(row):
    price = mean_prices.loc[(mean_prices.model == row["model"]) & (mean_prices.memory  == "memory_{}GB".format(row["memory"])) 
                            & (mean_prices.color == row["color"])].total_price
    if (price.shape[0] == 0):
        price = mean_prices.loc[(mean_prices.model == row["model"]) & (mean_prices.memory  == "memory_{}GB".format(row["memory"]))].total_price
    if (price.shape[0] == 0):
        price = mean_prices.loc[mean_prices.model == row["model"]].total_price
    return price.iloc[0]

def set_return_policy(res):
    #it's a workaround. Currently for all types of return we have "return_policy_buyer_pays" in data (Because of teh bug). 
    if (res["return_policy"] != "return_policy_no_return"):
        res["return_policy"] = "return_policy_buyer_pays"
        
def set_feedback(res):
    if (res["no_feedback_yet"]):
        res["no_feedback_yet"] = 1
        res["selers_feedback"] = 100
        res["number_of_reviews"] = 0 #todo. actually it's also a number of very old reviews. Check may be it's beter to put and avareage of oldreviews there.
    else:
        res["no_feedback_yet"] = 0
        
def prepare_data(res, columns = columns):
    all_colors = [x for x in columns if 'color_' in x]
    if not(res["color"] in all_colors):
        res["color"] = "color_other"
    set_return_policy(res)
    set_feedback(res)
    data_for_model = np.zeros(len(columns))
    categorical = ["color", "return_policy", "model"]
    for cat in categorical:
        print(cat)
        print(res[cat])
        data_for_model[columns.index(res[cat])] = 1
    data_for_model[columns.index("memory_{}GB".format(res["memory"]))] = 1
    numerical = ["no_feedback_yet", "selers_feedback", "shipping_cost", "number_of_reviews"]
    for num in numerical:
        print(num)
        data_for_model[columns.index(num)] = res[num]
    data_for_model[columns.index("mean_price")] = set_mean_price(res)
    if res["condition"] == 1:
      data_for_model[columns.index("very_good_condition")] = 1
    elif res["condition"] == -1:
      data_for_model[columns.index("very_bad_condition")] = 1
    return data_for_model

def get_number_of_expected_days(row):
    selected = median_active_days.loc[(median_active_days.model == row["model"]) & (median_active_days.memory  == "memory_{}GB".format(row["memory"])) 
                            & (median_active_days.color == row["color"])]
    days = selected["median"]
    if ((days.shape[0] == 0) or (selected["count"].iloc[0] < 10)): #if there are less than 10 examples, it could misleading
        selected = median_active_days.loc[(median_active_days.model == row["model"]) & (median_active_days.memory  == "memory_{}GB".format(row["memory"]))]
        days = selected["median"]
    if ((days.shape[0] == 0) or (selected["count"].iloc[0] < 10)):
        days = median_active_days.loc[median_active_days.model == row["model"]]["median"]
    days = int(round(days.iloc[0], 0))
    #never take the day 7. Some people choose 'decrease pricie on the day 7', as the result, data is corrpted at this day
    return 6 if days == 7 else days




@app.route("/get_sales_estimation", methods=['POST'])
def index():
    #print(request.json.get("model"))
    print(request.json)
    # find the price for the 0 category
    model_data = prepare_data(request.json, columns)
    number_of_days = get_number_of_expected_days(request.json)
    model_data[columns.index("listing_was_active_before_closure")] = number_of_days
    price = round(model.predict(np.array([model_data]))[0])
    
    
    return jsonify({'price': price, 'days': number_of_days})


if __name__ == "__main__":
    app.debug = True 
    http_server = WSGIServer(('', 8000), app)
    http_server.serve_forever()
    #app.run(debug=True, host = '127.0.0.1', port = 8000)
    #app.run()
    
# predict sale endpoint
# GET predict_sale
# params: json model fields
# response: json [{"price": 100, "max_days": 4}, {"price": 200, "max days": 5}]