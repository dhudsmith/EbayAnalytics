import pandas as pd
from sklearn import preprocessing
from datetime import datetime
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
    data.drop(['itemId','title','startTime',
               'endTime','postalCode','bidCount',
               'topRatedListing','gift', 'categoryName',
               'categoryId','value','startHour','startMonth',
               'endMonth','startMonthday','endMonthday','startWeekday'],
              axis=1, inplace=True)
    return(data)


#######################################################
# Helper
#######################################################

def preproc_rf(data):
    return delete_unwanted(times_to_categorical(encode(data)))

#######################################################
# Main
#######################################################

if __name__ == '__main__':
    print("Reading from csv...")
    data = pd.read_csv('../../Data/ebay_data_cleaned.csv', index_col=False)

    print("Preprocessing...")
    data = preproc_rf(data)

    print("Final shape:", data.shape)

    print("Writing to csv...")
    data.to_csv("ebay_data_rf.csv", na_rep="NA", index=False)

    print("Done.")

