# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

from optparse import OptionParser
from datetime import datetime as dt
from dateutil.parser import parse
import pandas as pd
import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError
from math import ceil

from pprint import pprint as pp
from pprint import pformat


#######################################################
# Setup
#######################################################
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


#######################################################
# Specify the API request
#######################################################
def get_api_dict():
    api_request = {
        'keywords': u'MacBook',
        'categoryId': u'111422',
        'outputSelector': [u'SellerInfo', u'AspectHistogram'],
        'sortOrder': u'EndTimeNewest',
        'itemFilter': [
            {'name': 'AvailableTo',
             'value': 'US'},
            {'name': 'Currency',
             'value': 'USD'},
            {'name': 'HideDuplicatedItems',
             'value': 'true'}
        ],
        'aspectFilter': [
            {'aspectName': 'Product Family',
             'aspectValueName': 'MacBook Pro'}
        ]
    }

    return api_request


#######################################################
# Making the api request and table filtering
#######################################################

# This is the primitive api call
# Given the input api_request, returns the input page
# of listings. This returns the full JSON table dict.
# Use the API helper functions for normal interface
def _get_page(opts, api_request, page_number=1):
    api_request['paginationInput'] = {"entriesPerPage": 100,
                                      "pageNumber": page_number}

    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml, warnings=True)

        # Strip the list of results
        response = api.execute('findCompletedItems', api_request).dict()

        return (response)

        # dump(api)
    except ConnectionError as e:
        print(e)
        print(e.response.dict())


# Should return a pandas df
def _get_relevant_data(listings):
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
                 'postalCode': _get_key_value(item, 'postalCode'),
                 'categoryId': item['primaryCategory']['categoryId'],
                 'categoryName': item['primaryCategory']['categoryName'],
                 'productId_type': _get_key_value(_get_key_value(item, 'productId'), '_type'),
                 'productId_value': _get_key_value(_get_key_value(item, 'productId'), 'value'),
                 'returnsAccepted': item['returnsAccepted'] == 'true',
                 'value': float(item['sellingStatus']['currentPrice']['value']),
                 'bidCount': _get_key_value(_get_key_value(item, 'sellingStatus'), 'bidCount'),
                 'sellingState': item['sellingStatus']['sellingState'],
                 'expeditedShipping': item['shippingInfo']['expeditedShipping'] == 'true',
                 # 'handlingTime': item['shippingInfo']['handlingTime'],
                 'shippingType': item['shippingInfo']['shippingType'],
                 'title': item['title'],
                 'topRatedListing': item['topRatedListing'] == 'true',
                 'feedbackRatingStar': _get_key_value(_get_key_value(item, 'sellerInfo'), 'feedbackRatingStar'),
                 'feedbackScore': _get_key_value(_get_key_value(item, 'sellerInfo'), 'feedbackScore'),
                 'positiveFeedbackPercent': _get_key_value(_get_key_value(item, 'sellerInfo'),
                                                           'positiveFeedbackPercent'),
                 'topRatedSeller': _get_key_value(_get_key_value(item, 'sellerInfo'), 'topRatedSeller')}
        dicts.append(entry)

    return (pd.DataFrame(dicts))


def _get_key_value(dict, key):
    if key in dict:
        return (dict[key])
    else:
        return ('NA')


#######################################################
# API interface
#######################################################
def get_number_pages(opts, api_request):
    return int(_get_page(opts, api_request)['paginationOutput']['totalPages'])


# This gets up to 100 pages of items matching the API request
# Since each page can have up to 100 items, this call returns a maximum of
# 10,000 listings. This limit is enforced by the ebay API
def get_all_100(opts, api_request):
    num_pages = get_number_pages(opts, api_request)

    if num_pages > 100:
        num_pages = 100

    ##
    ##
    # num_pages=2
    ##
    ##

    # Get the data from all the pages
    data_ls = []
    for i in range(1, num_pages + 1):
        print(int(float(i) / num_pages * 100), "% complete.")

        listings = _get_page(opts, api_request, i)

        if 'searchResult' in listings:
            data_ls.append(_get_relevant_data(listings['searchResult']['item']))

    # Combine all the data frames into one:
    return pd.concat(data_ls)


# Get all listings that ended before the input datetime
# GMT of the form "YYYY-MM-DDTHH:MM:SS.SSSZ"
def get_100_before(opts, api_request, datetime_str):
    item_filter_vals = api_request['itemFilter']
    item_filter_vals = [x for x in item_filter_vals if not x['name']=='EndTimeTo']
    item_filter_vals.append({'name': 'EndTimeTo', 'value': datetime_str})
    api_request['itemFilter'] = item_filter_vals

    return get_all_100(opts, api_request)


# Get all listings that ended after the input datetime
# GMT of the form "YYYY-MM-DDTHH:MM:SS.SSSZ"
def get_100_after(opts, api_request, datetime_str):
    item_filter_vals = api_request['itemFilter']
    item_filter_vals = [x for x in item_filter_vals if not x['name']=='EndTimeTo']
    item_filter_vals.append({'name': 'EndTimeFrom', 'value': datetime_str})
    api_request['itemFilter'] = item_filter_vals

    return get_all_100(opts, api_request)

# This function gets around the ebay api limitation of 10,000 items
# by making multiple api calls until all items are fetched. This
# can take a while depending on how many items meet the search
# criteria specified by api_request.
def get_all(opts, api_request):
    # Get the initial number of pages

    # Get the current time
    now = dt.utcnow()
    now_str = now.isoformat("T")[:-3] + "Z"

    time_str = now_str

    item_filter_vals = api_request['itemFilter']
    item_filter_vals = [x for x in item_filter_vals if not x['name']=='EndTimeTo']
    item_filter_vals.append({'name': 'EndTimeTo', 'value': now_str})
    api_request['itemFilter'] = item_filter_vals

    # Get the total number of pages of listings
    num_pages = get_number_pages(opts, api_request)

    # The number of calls required to get all the pages is the
    # ceiling of the number of pages divided by 100 (e.g. 463 pages
    # requires 5 api calls each fetching (100, 100, 100, 100, 63) pages.
    num_calls = int( ceil( num_pages/100.0 ) )

    # Make the first call:
    print "Call 1 of", num_calls, ":"
    data = get_100_before(opts, api_request, now_str)

    # Loop api calls to get all data:
    data_ls = [data]
    for i in range(1, num_calls):
        print "Call", 1+i, "of" , num_calls, ":"
        oldest_str = data_ls[i-1]['endTime'].iloc[-1]
        data_ls.append(get_100_before(opts, api_request, oldest_str))
    # return pd.concat(data_ls)

    return pd.concat(data_ls)

#######################################################
# Preprocessing
#######################################################

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


def preproc(data):
    data['isShippingFree'] = [is_free_shipping(ship_type) for ship_type in data.loc[:, 'shippingType']]
    data['listingType'] = [simplify_listing_type(list_type) for list_type in data.loc[:, 'listingType']]

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
                     'gift',
                     'paymentMethod',
                     'expeditedShipping',
                     'shippingType',
                     'isShippingFree',
                     'returnsAccepted',
                     'topRatedListing',
                     'feedbackRatingStar',
                     'feedbackScore',
                     'positiveFeedbackPercent',
                     'topRatedSeller',
                     'value',
                     'sellingState'
                     ]

    data = data[new_col_order]

    return (data)






#######################################################
# Building the database
#######################################################
# TODO: use SQL database
if __name__ == "__main__":
    print("Finding samples for SDK version %s" % ebaysdk.get_version())
    (opts, args) = init_options()

    api_request = get_api_dict()

    # Save one page for reference
    with open('Documents/PageExample.txt', 'w') as fout:
        pp(_get_page(opts, api_request), fout)

    # Get number of pages of entries
    num_pages = get_number_pages(opts, api_request)
    print("Number of pages:", num_pages)
    print("Number of entries:", 100 * num_pages)

    # Get all of the listings in a data frame
    data = get_all(opts, api_request)

    # Preprocess the data
    data = preproc(data)


    # Print the data frame to a file
    data.to_csv("Data/ebay_data.csv", na_rep="NA", index=False, encoding='utf-8')

    # data = get_all(opts, api_dict)
    #
    # now = dt.utcnow()
    # now_str = now.isoformat("T")[:-3] + "Z"
    #
    # time_str = now_str
    #
    # item_filter_vals = api_request['itemFilter']
    # item_filter_vals.append({'name': 'EndTimeTo', 'value': now_str})
    # api_request['itemFilter'] = item_filter_vals
    #
    # pp(_get_page(opts, api_request, 1)['paginationOutput'])

    # print(data.head(10), data.endDate)
