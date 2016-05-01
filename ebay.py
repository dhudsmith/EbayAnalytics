# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

from optparse import OptionParser
import pandas as pd
import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError

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
        'keywords': u'MacBook Pro',
        'categoryId': u'111422',
        'outputSelector': [u'SellerInfo', u'AspectHistogram'],
        'sortOrder': u'StartTimeNewest',
        'itemFilter': [
            {'name': 'AvailableTo',
             'value': 'US'},
            {'name': 'Currency',
             'value': 'USD'},
            {'name': 'HideDuplicatedItems',
             'value': 'true'}
        ]
    }

    return api_request




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

def get_page(opts, api_request, page_number=1):

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

# This gets up to 10,000 items matching the API request
# The limit of 10,000 items is enforced by the ebay API
def get_all(opts, api_request):
    num_pages = get_number_pages(opts, api_request)

    if num_pages > 100:
        num_pages = 100

    # Get the data from all the pages
    data_ls = []
    for i in range(1, 3 + 1):
        print(i, "% complete.")

        listings = get_page(opts, api_dict, i)

        if 'searchResult' in listings:
            data_ls.append(get_relevant_data(listings['searchResult']['item']))

    # Combine all the data frames into one:
    return pd.concat(data_ls)

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


if __name__ == "__main__":

    print("Finding samples for SDK version %s" % ebaysdk.get_version())
    (opts, args) = init_options()

    api_dict = get_api_dict()

    # Get number of pages of entries
    num_pages = get_number_pages(opts, api_dict)
    print("Number of entries:", num_pages * 100)

    # Get all of the listings in a data frame
    data = get_all(opts, api_dict)

    # Print the data frame to a file
    data.to_csv("Data/ebay_data.csv", na_rep = "NA", index = False)


