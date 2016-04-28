import os
import os.path
from apscheduler.schedulers.blocking import BlockingScheduler
from sklearn.externals import joblib
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn import preprocessing
import numpy as np
import pandas as pd
import datetime
from bokeh.plotting import figure, output_file, save
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError
from optparse import OptionParser

sched = BlockingScheduler()

def api_request():
    # Specify the API request
    api_request = {
        'keywords': u'MacBook Pro',
        'categoryId': u'111422',
        'outputSelector': [u'SellerInfo', u'AspectHistogram'],
        'sortOrder': u'EndTimeNewest',
        'itemFilter': [
            {'name': 'Condition',
             'value': 'Used'},
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

    (opts, args) = init_options()

    listings = get_relevant_data(request_completed_listings(opts, api_request=api_request)['searchResult']['item'])

    listings = preproc(listings)

    listings = preproc_rf(listings)

    return(listings)

def predict_and_compare(X, y):
    clf = joblib.load('static/model_pkl/rf_model_april_27_2016.pkl')

    y_pred = clf.predict(X)

    cmat = confusion_matrix(y, y_pred)
    auc = roc_auc_score(y, clf.predict_proba(X)[:, 1])

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

    plot = figure(title='Live feed of random forest scores',
                  x_axis_label=x_name,
                  x_axis_type='datetime',
                  y_axis_label='Random forest scores')

    plot.line(time, acc, color = 'red', legend='accuracy')
    plot.line(time, auc, color='green', legend='ROC AUC')

    plot.legend.orientation = "top_left"

    output_file("templates/runningscore.html")

    save(plot)

##################################################
# ExtractEbayData
##################################################

def init_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enabled debugging [default: %default]")
    parser.add_option("-y", "--yaml",
                      dest="yaml", default='ebay.yaml',
                      help="Specifies the name of the YAML defaults file. [default: %default]")
    parser.add_option("-a", "--appid",
                      dest="appid", default=None,
                      help="Specifies the eBay application id to use.")

    (opts, args) = parser.parse_args()
    return opts, args


def get_number_pages(opts, api_request):

    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml, warnings=True)



        # Strip the list of results
        response = int(api.execute('findCompletedItems', api_request).dict()['paginationOutput']['totalPages'])

        return(response)

        # dump(api)
    except ConnectionError as e:
        print(e)
        print(e.response.dict())

def request_completed_listings(opts, api_request, page_number=1):

    api_request['paginationInput'] = {"entriesPerPage": 100,
                                      "pageNumber": page_number}

    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml, warnings=True)



        # Strip the list of results
        response = api.execute('findCompletedItems', api_request).dict()

        return(response)

        # dump(api)
    except ConnectionError as e:
        print(e)
        print(e.response.dict())

# Should return a pandas df
def get_relevant_data(listings):

    dicts = []
    for item in listings:
        entry = {'conditionDisplayName': item['condition']['conditionDisplayName'],
                 'conditionId': item['condition']['conditionId'],
                 'country': item['country'],
                 'itemId': item['itemId'],
                 'bestOfferEnabled': item['listingInfo']['bestOfferEnabled'] == 'true',
                 'buyItNowAvailable': item['listingInfo']['buyItNowAvailable'] == 'true',
                 'gift': item['listingInfo']['gift'] == 'true',
                 'listingType': item['listingInfo']['listingType'],
                 'startTime': item['listingInfo']['startTime'],
                 'endTime': item['listingInfo']['endTime'],
                 # item['location'],
                 'paymentMethod': item['paymentMethod'],
                 'postalCode': get_key_value(item, 'postalCode'),
                 'categoryId': item['primaryCategory']['categoryId'],
                 'categoryName': item['primaryCategory']['categoryName'],
                 'productId_type':  get_key_value(get_key_value(item, 'productId'),'_type'),
                 'productId_value':  get_key_value(get_key_value(item, 'productId'),'value'),
                 'returnsAccepted': item['returnsAccepted'] == 'true',
                 'value': float(item['sellingStatus']['currentPrice']['value']),
                 'bidCount': get_key_value(get_key_value(item, 'sellingStatus'), 'bidCount'),
                 'sellingState': item['sellingStatus']['sellingState'],
                 'expeditedShipping': item['shippingInfo']['expeditedShipping'] == 'true',
                 # 'handlingTime': item['shippingInfo']['handlingTime'],
                 'shippingType': item['shippingInfo']['shippingType'],
                 'title': item['title'],
                 'topRatedListing': item['topRatedListing'] == 'true'}
        dicts.append(entry)

    return(pd.DataFrame(dicts))

def get_key_value(dict, key):
    if key in dict:
        return(dict[key])
    else:
        return('NA')

##################################################
# DataAnalysis.preproc
##################################################

# Add a free shipping column
def is_free_shipping(shippingType):
    if shippingType in ['Calculated', 'Flat',
                        'FreePickup', 'FlatDomesticCalculatedInternational',
                        'CalculatedDomesticFlatInternational', 'NotSpecified']:
        return (False)
    elif shippingType == 'Free':
        return (True)
    else:
        print("Warning: invalid shipping type!")
        return ('NaN')

# Simplify listing types to Auction or Fixed Price
def simplify_listing_type(listing_type):
    if listing_type in ['Auction', 'AuctionWithBIN']:
        return ('Auction')
    elif listing_type in ['FixedPrice', 'StoreInventory']:
        return ('FixedPrice')
    else:
        print("Warning: invalid listing type!")
        return ('NaN')

# Reorder the columns in a reasonable way
new_col_order = ['itemId',
                 'title',
                 'productId_type',
                 'productId_value',
                 'conditionDisplayName',
                 'conditionId',
                 'categoryId',
                 'categoryName',
                 'startTime',
                 'endTime',
                 'postalCode',
                 'country',
                 'listingType',
                 'bidCount',
                 'buyItNowAvailable',
                 'bestOfferEnabled',
                 'topRatedListing',
                 'gift',
                 'paymentMethod',
                 'expeditedShipping',
                 'shippingType',
                 'isShippingFree',
                 'returnsAccepted',
                 'sellingState',
                 'value']

def preproc(data):
    data['isShippingFree'] = [is_free_shipping(ship_type) for ship_type in data.loc[:, 'shippingType']]
    data['listingType'] = [simplify_listing_type(list_type) for list_type in data.loc[:, 'listingType']]
    data['listingType'] = [simplify_listing_type(list_type) for list_type in data.loc[:, 'listingType']]

    return(data)

##################################################
# DataAnalysis.RandomForest.preproc_rf
##################################################


def encode(data):
    # These are the encoded features
    features_to_encode = ('productId_type', 'productId_value', 'conditionDisplayName', 'conditionId',
                          'categoryId', 'categoryName', 'country', 'listingType', 'buyItNowAvailable',
                          'bestOfferEnabled', 'topRatedListing', 'gift', 'paymentMethod', 'expeditedShipping',
                          'expeditedShipping', 'shippingType', 'isShippingFree', 'returnsAccepted', 'sellingState')

    # Convert them all to string for sorting
    for feat in features_to_encode:
        data[feat] = [str(i) for i in data[feat]]

    # This is the label encoder
    le = preprocessing.LabelEncoder()

    # Encode all the features (This only makes sense for tree-based model!)
    for feat in features_to_encode:
        le.fit(data[feat])
        data[feat] = le.transform(data[feat])

    return(data)

def to_dt_ebay(dt_str):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return datetime.datetime.strptime(dt_str, format)

def times_to_categorical(data):
    # Start times:
    data['startHour'] = [to_dt_ebay(x).hour for x in data.startTime]
    data['startWeekday'] = [to_dt_ebay(x).weekday() for x in data.startTime]
    data['startMonthday'] = [to_dt_ebay(x).day for x in data.startTime]
    data['startMonth'] = [to_dt_ebay(x).month for x in data.startTime]

    # End times:
    data['endHour'] = [to_dt_ebay(x).hour for x in data.endTime]
    data['endWeekday'] = [to_dt_ebay(x).weekday() for x in data.endTime]
    data['endMonthday'] = [to_dt_ebay(x).day for x in data.endTime]
    data['endMonth'] = [to_dt_ebay(x).month for x in data.endTime]

    return(data)

def delete_unwanted(data):
    data.drop(['itemId','title','startTime',
               'endTime','postalCode','bidCount',
               'topRatedListing','gift', 'categoryName', 'categoryId','value'],
              axis=1, inplace=True)
    return(data)

def preproc_rf(data):
    return delete_unwanted(times_to_categorical(encode(data)))

##################################################
# DataAnalysis.RandomForest.preproc_rf
##################################################

@sched.scheduled_job('interval', minutes=1)
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