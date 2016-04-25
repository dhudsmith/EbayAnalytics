import pandas as pd
import numpy as np
from sklearn import preprocessing
import pprint as pp
from bokeh.charts import Bar, BoxPlot, output_file, show
from bokeh.models import Range1d
from bokeh.io import hplot
from bokeh.plotting import figure
from datetime import datetime
import time

#######################################################
# Read in the data
#######################################################

# Read in the pandas.DataFrame from csv
data = pd.read_csv('../../Data/ebay_data_cleaned.csv', index_col=False)

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


#######################################################
# Convert datetime fields to seconds since Jan 1, 1970, 00:00:00
# TODO: convert datetimes to categorical variables, instead. e.g.: hour of day, day of week, month
#######################################################

# A function for stripping datetime objects from strings
def convert_datetime(datetime_string):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return datetime.strptime(datetime_string, format)

# A function to convert datetime to seconds since Jan 1, 1970, 00:00:00
def conv_sec(dt):
    return(time.mktime(dt.timetuple()))

# Convert all times to datetimes
data['startTime'] = [conv_sec(convert_datetime(datetime_string)) for datetime_string in data['startTime']]
data['endTime'] = [conv_sec(convert_datetime(datetime_string)) for datetime_string in data['endTime']]

print(data.head())
