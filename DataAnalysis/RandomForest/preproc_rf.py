import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.feature_selection import VarianceThreshold
from dateutil.parser import parse as parse


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
                          'expeditedShipping', 'shippingType', 'isShippingFree', 'returnsAccepted', 'sellingState',
                          'feedbackRatingStar', 'topRatedSeller')

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
# Set value to zero for auction items
#######################################################

def set_auction_value_zero(record):
    if record['listingType'] == 'Auction':
        return 0
    else:
        return record['value']

#######################################################
# Convert datetime fields categorical variables
#######################################################

# Convert the times to the following categorical variables
# Hour (0-23)
# Weekday (0-6)
# Monthday (0-[28-31])
# Month (0-11)

# First, get the datetime

def times_to_categorical(data):
    # Start times:
    data['startHour'] = [parse(x).hour for x in data.startTime]
    data['startWeekday'] = [parse(x).weekday() for x in data.startTime]
    data['startMonthday'] = [parse(x).day for x in data.startTime]
    data['startMonth'] = [parse(x).month for x in data.startTime]

    # End times:
    data['endHour'] = [parse(x).hour for x in data.endTime]
    data['endWeekday'] = [parse(x).weekday() for x in data.endTime]
    data['endMonthday'] = [parse(x).day for x in data.endTime]
    data['endMonth'] = [parse(x).month for x in data.endTime]

    return(data)

#######################################################
# Delete unwanted columns
#######################################################

def delete_unwanted(data):
    data.drop(['itemId','title','startTime'
               ,'postalCode','bidCount',
               'topRatedListing','gift', 'categoryName',
               'categoryId','startHour','startMonth',
               'endMonth','startMonthday','endMonthday','startWeekday'],
              axis=1, inplace=True)
    return(data)

#######################################################
# Remove columns with zero variance
#######################################################

def remove_const(data):
    selector = VarianceThreshold()
    selector.fit_transform(data)

    return data

#######################################################
# Remove duplicate columns
#######################################################

def remove_duplicate_cols(data):
    colsToRemove = []
    columns = data.columns
    for i in range(len(columns)-1):
        v = data[columns[i]].values
        for j in range(i+1,len(columns)):
            if np.array_equal(v,data[columns[j]].values):
                colsToRemove.append(columns[j])

    data.drop(colsToRemove, axis=1, inplace=True)

    return data

#######################################################
# Helper
#######################################################

def preproc_rf(data):
    data['value'] = data.apply(set_auction_value_zero, axis=1)
    data = encode(data)
    data = times_to_categorical(data)
    data = delete_unwanted(data)

    return(data)



#######################################################
# Main
#######################################################

if __name__ == '__main__':
    print("Reading from csv...")
    data = pd.read_csv('../../Data/ebay_data.csv', index_col=False)

    print("Preprocessing...")
    data = preproc_rf(data)

    print("Final shape:", data.shape)

    # print("Writing to csv...")
    data.to_csv("ebay_data_rf_endtime.csv", na_rep="NA", index=False)

    print("Done.")

