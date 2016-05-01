from DataAnalysis.RandomForest.preproc_rf import preproc_rf
from DataAnalysis.preproc import preproc
import ExtractEbayData as ebay
import os
import os.path
from apscheduler.schedulers.blocking import BlockingScheduler
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix, roc_auc_score
import numpy as np
import pandas as pd
import datetime
from bokeh.plotting import figure, output_file, save
import logging
logging.basicConfig()

sched = BlockingScheduler()

def api_request():
    # Specify the API request
    api_request = {
        'keywords': u'MacBook Pro',
        'categoryId': u'111422',
        'outputSelector': [u'SellerInfo', u'AspectHistogram'],
        'sortOrder': u'StartTimeNewest',
        'itemFilter': [
            # {'name': 'Condition',
            #  'value': 'Used'},
            {'name': 'AvailableTo',
             'value': 'US'},
            {'name': 'Currency',
             'value': 'USD'},
            {'name': 'HideDuplicatedItems',
             'value': 'true'}
        ],
    }
    api_request['paginationInput'] = {"entriesPerPage": 100,
                                      "pageNumber": 1}

    (opts, args) = ebay.init_options()

    listings = ebay.get_relevant_data(ebay.request_completed_listings(opts, api_request=api_request)['searchResult']['item'])

    listings = preproc(listings)

    listings = preproc_rf(listings)

    return(listings)

def predict_and_compare(X, y):
    clf = joblib.load('static/model_pkl/rf_model_april_27_2016.pkl')

    y_pred = clf.predict(X)

    cmat = confusion_matrix(y, y_pred)
    auc = roc_auc_score(y, clf.predict_proba(X)[:, 1], average="weighted")

    return [cmat, auc]

def update_data(datetime, cmat, auc):
    # calculate the quantities to write to the dataframe
    num = np.sum(cmat)
    cmat_norm = cmat/num
    tpos = cmat_norm[0,0]
    tneg = cmat_norm[1,1]
    fpos = cmat_norm[1,0]
    fneg = cmat_norm[0,1]
    acc = cmat_norm[0,0] + cmat_norm[1,1]

    data = [{"Time": datetime, "True pos.": tpos, "False pos.":fpos,"True neg.": tneg, "False neg.":fneg, "ROC-AUC": auc , "Accuracy": acc}]

    # create a pandas dataframe with one row
    df = pd.DataFrame(data)

    # update the files
    if os.path.isfile("static/running_data.csv"):
        df.to_csv("static/running_data.csv", header=False, mode='a', index=False)
    else:
        df.to_csv("static/running_data.csv", header=True, index= False)

def to_dt(dt_str):
    format = '%Y-%m-%d %H:%M:%S.%f'
    return datetime.datetime.strptime(dt_str, format)

def make_plots():
    data = pd.read_csv("static/running_data.csv", index_col=False)

    time = [to_dt(x) for x in data.Time]

    dt = max(time)
    last_time = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    x_name = "date (last updated: " + str(last_time) +")"

    acc = data.Accuracy
    auc = data["ROC-AUC"]
    tp = data["True pos."]
    tn = data["True neg."]
    fp = data["False pos."]
    fn = data["False neg."]


    plot = figure(title='Live feed of random forest scores',
                  x_axis_label=x_name,
                  x_axis_type='datetime',
                  y_axis_label='Random forest scores')

    plot.line(time, acc, color = 'black', legend='accuracy', line_width=3)
    plot.line(time, auc, color='blue', legend='ROC AUC', line_width=3)
    plot.line(time, tp, color='green', legend='True positive')
    plot.line(time, tn, color='green', legend='True negative',line_dash=[4, 4])
    plot.line(time, fp, color='red', legend='False positive')
    plot.line(time, fn, color='red', legend='False negative',line_dash=[4, 4])

    plot.legend.orientation = "top_left"

    output_file("templates/runningscore.html")

    save(plot)

##################################################
# DataAnalysis.RandomForest.preproc_rf
##################################################

@sched.scheduled_job('interval', minutes=2)
def timed_job():
    # Get the new data
    timestamp = datetime.datetime.now()
    new_data = api_request()

    # Separate the target and inputs
    y = new_data.sellingState
    new_data.drop('sellingState', axis=1, inplace=True)

    # Predict the selling outcome of new listings
    cmat, auc = predict_and_compare(new_data, y)

    # Update the data files
    update_data(timestamp, cmat, auc)

    # Make new plots
    make_plots()

sched.start()