import pandas as pd
import pprint as pp
from bokeh.charts import Bar, BoxPlot, output_file, show
from bokeh.io import hplot
from bokeh.plotting import figure
from datetime import datetime

#######################################################
# Data import and cleanup
#######################################################

# Read in the pandas.DataFrame from csv
data = pd.read_csv('./ebay_data.csv', index_col=False)

# Reorder the columns in a reasonable way
new_col_order = [ 'itemId',
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
                  'returnsAccepted',
                  'sellingState',
                  'value']
data = data[new_col_order]

#######################################################
# Examine the effect of free shipping on "value"
# for sold _Buy it now_ and sold _Auction_ items
#######################################################

# print(data.shippingType.unique())
#['Calculated' 'Free' 'Flat' 'FreePickup'
# 'FlatDomesticCalculatedInternational'
# 'CalculatedDomesticFlatInternational' 'NotSpecified']

# Add a free shipping column
def is_free_shipping(shippingType):
    if shippingType in ['Calculated','Flat',
                        'FreePickup','FlatDomesticCalculatedInternational',
                        'CalculatedDomesticFlatInternational', 'NotSpecified']:
        return(False)
    elif shippingType == 'Free':
        return(True)
    else:
        print("Warning: invalid shipping type!")
        return('NaN')
data['isShippingFree'] = [is_free_shipping(ship_type) for ship_type in data.loc[:,'shippingType']]

# Simplify listing types to Auction or Fixed Price
def simplify_listing_type(listing_type):
    if listing_type in ['Auction','AuctionWithBIN']:
        return('Auction')
    elif listing_type in ['FixedPrice','StoreInventory']:
        return('Fixed Price')
    else:
        print("Warning: invalid listing type!")
        return('NaN')
data['listingType'] = [simplify_listing_type(list_type) for list_type in data.loc[:,'listingType']]

# Subset to sold data
data_sold = data[data.sellingState=='EndedWithSales']

# Generate the plot
TOOLS = 'box_zoom,box_select,crosshair,resize,reset'
plt = BoxPlot(data_sold, values = 'value', label= ['listingType','isShippingFree'],
              title = "Impact of listing type and free shipping",
              xlabel="(Listing Type, Free Shipping)",
              ylabel="Sale price ($)",
              color = 'listingType',
              outliers = False)

# Save the plot
output_file("./plots/plot1.html")
show(plt)

#######################################################
# Examine the effect of different factors on
# on sale outcome
#######################################################

# Factors to consider
factors = [('conditionDisplayName','Used'),
           ('buyItNowAvailable',True),
           ('topRatedListing',True),
           ('expeditedShipping',True),
           ('returnsAccepted',True),
           ('listingType','Auction'),
           ('isShippingFree',True)]

# Unsold item potions
data_unsold = data[data.sellingState=='EndedWithoutSales']
portions_unsold = {}
for factor in factors:
    portions_unsold[factor[0]] = len(data_unsold[data_unsold[factor[0]]==factor[1]].index) / len(data_unsold.index)

# Sold item potions
portions_sold = {}
for factor in factors:
    portions_sold[factor[0]] = len(data_sold[data_sold[factor[0]]==factor[1]].index) / len(data_sold.index)

# Put into a df for Bokeh
factorPortions_df = pd.DataFrame([portions_sold, portions_unsold], index=['sold','unsold'])
print(factorPortions_df.columns)
factorPortions_df.rename(columns={'buyItNowAvailable': "Buy-it-now avail.",
                                  'conditionDisplayName': "Used",
                                  'expeditedShipping': "Expedited shipping avail.",
                                  'isShippingFree': "Free shipping",
                                  'listingType': "Auction",
                                  'returnsAccepted': "Returns accepted",
                                  'topRatedListing': "Top rated listing"}, inplace=True)


factorPortions_df = factorPortions_df.transpose()
factorPortions_df['factor']=factorPortions_df.index

factorPortions_df = pd.melt(factorPortions_df, id_vars='factor', var_name="status")



# Make the chart
plt2 = Bar(factorPortions_df,
           label="factor",
           values="value",
           group="status",
           agg="mean",
           ylabel="Fraction of listings with feature",
           title="Impact of listing features on sale outcome",
           legend=True)

# Save the plot
output_file("./plots/plot2.html")
show(plt2)

#######################################################
# Examine the effect "endTime" on "value" on
# sold _Buy it now_ and sold _Auction_items
#######################################################

# Convert the TimeEnded Column into a datetime object

# def convert_datetime(datetime_string):
#     format = '%Y-%m-%dT%H:%M:%S.%fZ'
#     return datetime.strptime(datetime_string, format)
#
# data_sold['endTime'] = [convert_datetime(datetime_string) for datetime_string in data_sold.loc[:, 'endTime']]
# data_sold['startTime'] = [convert_datetime(datetime_string) for datetime_string in data_sold.loc[:, 'startTime']]
#
# # Add a sale hour to the data frame
# data_sold['endHour']= [x.hour for x in data_sold['endTime']]
# data_sold['startHour']= [x.hour for x in data_sold['startTime']]
# data_sold['duration']= data_sold['endTime'] - data_sold['startTime']
#
# pp.pprint(data_sold.head())

# Generate the plots
# First the Auction Data
# TOOLS = 'box_zoom,box_select,crosshair,resize,reset'
# plt2a = BoxPlot(data_sold[data_sold.listingType=="Auction"], values = 'value', label= ['startHour'],
#               title = "MacBook Pro Sale Values (Auction)",
#               xlabel="(Listing Type, Sale Hour (0-23)",
#               ylabel="Sale price ($)",
#               outliers = False)
# plt2b = BoxPlot(data_sold[data_sold.listingType=="Fixed Price"], values='value', label=['startHour'],
#                 title="MacBook Pro Sale Values (Fixed Price)",
#                 xlabel="(Listing Type, Sale Hour (0-23)",
#                 ylabel="Sale price ($)",
#                 outliers=False)

# plt3 = figure(tools=TOOLS,
#               title='MacBook Pro Sale Values (Auction)',
#               x_axis_label='Duration (days)')
#
# data_sold = data_sold.sort_values(by='duration')
#
# plt3.line(data_sold.duration, data_sold.value, color='navy', alpha=0.5)

# Save the plot
# output_file("plot2.html")
# # show(hplot(plt2a, plt2b))
# show(plt3)