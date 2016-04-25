import pandas as pd
import numpy as np
import pprint as pp
from bokeh.charts import Bar, BoxPlot, output_file, show
from bokeh.models import Range1d
from bokeh.io import hplot
from bokeh.plotting import figure
from datetime import datetime

#######################################################
# Read in the data
#######################################################

# Read in the pandas.DataFrame from csv
data = pd.read_csv('../../Data/ebay_data_cleaned.csv', index_col=False)

#######################################################
# Features: starred features will be encoded as digits
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

#######################################################
# Encode categorical variables
#######################################################

# takes a python list and returns the list where the categories are
# mapped onto integers from 0 to <number unique categories> - 1
def map_categories(column_cat):
    unique_cat = column_cat.unique()
    num_unique = len(unique_cat)
    mapping = {}
    # TODO: handle NaNs
    for i in range(0,num_unique):
        mapping[unique_cat[i]] = i

    y=[]
    for x in column_cat:
        y.append(mapping.get(x))

    return(y)


#######################################################
# Test
#######################################################

pp.pprint(map_categories(data.conditionId))