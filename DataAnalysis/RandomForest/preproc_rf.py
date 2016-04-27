import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.feature_selection import VarianceThreshold
import pprint as pp
from bokeh.charts import Bar, BoxPlot, output_file, show
from bokeh.models import Range1d
from bokeh.io import hplot
from bokeh.plotting import figure
from datetime import datetime
import time


#######################################################
# Encode categorical features:
# starred features will be encoded as digits
#######################################################
# itemId
# title
# productId_type
# productId_value *
# conditionDisplayName *
# conditionId *
# categoryId *
# categoryName *
# startTime
# endTime
# postalCode
# country *
# listingType *
# bidCount
# buyItNowAvailable *
# bestOfferEnabled *
# topRatedListing *
# gift *
# paymentMethod *
# expeditedShipping *
# shippingType *
# isShippingFree *
# returnsAccepted *
# sellingState *
# value


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


#######################################################
# Convert datetime fields categorical variables
#######################################################

# Convert the times to the following categorical variables
# Hour (0-23)
# Weekday (0-6)
# Monthday (0-[28-31])
# Month (0-11)

# First, get the datetime

def to_dt(dt_str):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return datetime.strptime(dt_str, format)

def times_to_categorical(data):
    # Start times:
    data['startHour'] = [to_dt(x).hour for x in data.startTime]
    data['startWeekday'] = [to_dt(x).weekday() for x in data.startTime]
    data['startMonthday'] = [to_dt(x).day for x in data.startTime]
    data['startMonth'] = [to_dt(x).month for x in data.startTime]

    # End times:
    data['endHour'] = [to_dt(x).hour for x in data.endTime]
    data['endWeekday'] = [to_dt(x).weekday() for x in data.endTime]
    data['endMonthday'] = [to_dt(x).day for x in data.endTime]
    data['endMonth'] = [to_dt(x).month for x in data.endTime]

    return(data)

#######################################################
# Delete unwanted columns
#######################################################

def delete_unwanted(data):
    data.drop(['itemId','title','startTime',
               'endTime','postalCode','bidCount',
               'topRatedListing','gift', 'categoryName', 'categoryId','value'],
              axis=1, inplace=True)
    return(data)


#######################################################
# Helper
#######################################################

def preproc_rf(data):
    return delete_unwanted(times_to_categorical(encode(data)))
