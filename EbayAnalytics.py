# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
from optparse import OptionParser
import pprint
import pandas as pd

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

# from common import dump

import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError

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

def get_completed_listings(opts, api_request, page_number=1):

    api_request['paginationInput'] = {"entriesPerPage": 100,
                                      "pageNumber": page_number}

    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml, warnings=True)



        # Strip the list of results
        response = api.execute('findCompletedItems', api_request).dict()['searchResult']['item']

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
                 # item['postalCode'],
                 'categoryId': item['primaryCategory']['categoryId'],
                 'categoryName': item['primaryCategory']['categoryName'],
                 # 'productId_type': item['productId']['_type'],
                 # 'productId_value': item['productId']['value'],
                 'returnsAccepted': item['returnsAccepted'] == 'true',
                 'value': float(item['sellingStatus']['currentPrice']['value']),
                 'sellingState': item['sellingStatus']['sellingState'],
                 'expeditedShipping': item['shippingInfo']['expeditedShipping'] == 'true',
                 # 'handlingTime': item['shippingInfo']['handlingTime'],
                 'shippingType': item['shippingInfo']['shippingType'],
                 'title': item['title'],
                 'topRatedListing': item['topRatedListing'] == 'true'}
        dicts.append(entry)

    return(pd.DataFrame(dicts))



if __name__ == "__main__":

    api_request = {
        'keywords': u'2014 MacBook Pro',
        'itemFilter': [
            {'name': 'Condition',
             'value': 'Used'},
            {'name': 'AvailableTo',
             'value': 'US'},
            {'name': 'Currency',
             'value': 'USD'}
        ],
    }

    print("Finding samples for SDK version %s" % ebaysdk.get_version())
    (opts, args) = init_options()

    # Get number of pages of entries
    num_pages = get_number_pages(opts, api_request)
    print("Number of pages:", num_pages)

    # Get the data from all the pages
    data_ls = []
    for i in range(1, num_pages+1):
        listings = get_completed_listings(opts, api_request, i)
        data_ls.append(get_relevant_data(listings))

    # Combine all the data frames into one:
    data = pd.concat(data_ls)

    print(data.loc[:,'value'].describe())
    print(sys.getsizeof(data))

