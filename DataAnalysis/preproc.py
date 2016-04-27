import pandas as pd
import pprint as pp
from bokeh.charts import Bar, BoxPlot, output_file, show
from bokeh.models import Range1d
from bokeh.io import hplot
from bokeh.plotting import figure
from datetime import datetime

#######################################################
# Add/simplify rows
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


#######################################################
# Reorder the columns
#######################################################

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

#######################################################
# general preprocessing helper function
#######################################################
def preproc(data):
    data['isShippingFree'] = [is_free_shipping(ship_type) for ship_type in data.loc[:, 'shippingType']]
    data['listingType'] = [simplify_listing_type(list_type) for list_type in data.loc[:, 'listingType']]
    data['listingType'] = [simplify_listing_type(list_type) for list_type in data.loc[:, 'listingType']]

    return(data)