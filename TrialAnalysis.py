import pandas as pd
import pprint as pp
from bokeh.charts import Bar, BoxPlot, Histogram, output_file, show
from bokeh.models import Range1d
from bokeh.io import hplot
from bokeh.plotting import figure
from datetime import datetime

#######################################################
# Data import and cleanup
#######################################################

# Read in the pandas.DataFrame from csv
data = pd.read_csv('Data/ebay_data.csv', index_col=False)



#######################################################
# Examine the effect of free shipping on "value"
# for sold _Buy it now_ and sold _Auction_ items
#######################################################

# print(data.shippingType.unique())
# ['Calculated' 'Free' 'Flat' 'FreePickup'
# 'FlatDomesticCalculatedInternational'
# 'CalculatedDomesticFlatInternational' 'NotSpecified']

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


data['isShippingFree'] = [is_free_shipping(ship_type) for ship_type in data.loc[:, 'shippingType']]


# Simplify listing types to Auction or Fixed Price
def simplify_listing_type(listing_type):
    if listing_type in ['Auction', 'AuctionWithBIN']:
        return ('Auction')
    elif listing_type in ['FixedPrice', 'StoreInventory']:
        return ('FixedPrice')
    else:
        print("Warning: invalid listing type!")
        return ('NaN')


data['listingType'] = [simplify_listing_type(list_type) for list_type in data.loc[:, 'listingType']]

# Subset to sold data
data_sold = data[data.sellingState == 'EndedWithSales']

# Generate the plot
TOOLS = ''
plt = BoxPlot(data_sold, values='value', label=['listingType', 'isShippingFree'],
              title="Impact of listing type and free shipping",
              xlabel="(Listing Type, Free Shipping)",
              ylabel="Sale price ($)",
              color='listingType',
              outliers=True,
              tools=TOOLS)
plt.logo = None
plt.toolbar_location = None



# Save the plot
output_file("./templates/plot1_new.html")
# show(plt)

#######################################################
# Examine the effect of different factors on
# on sale outcome
#######################################################

# Calculate the portions sold for features of interest:

portions_sold = []
# Used items true
portions_sold.append(('Condition--used',len(
    data[(data.conditionDisplayName == 'Used') & (data.sellingState == 'EndedWithSales')].index) / len(
    data[data.conditionDisplayName == 'Used'].index),'True','Sold', 'Condition'))
# Used items false
portions_sold.append(('Condition--new',len(
    data[(data.conditionDisplayName != 'Used') & (data.sellingState == 'EndedWithSales')].index) / len(
    data[data.conditionDisplayName != 'Used'].index),'False','Sold', 'Condition'))
# Auction true
portions_sold.append(('Type--Auction',len(
    data[(data.listingType == 'Auction') & (data.sellingState == 'EndedWithSales')].index) / len(
    data[data.listingType == 'Auction'].index),'True','Sold','Listing'))
# Auction false
portions_sold.append(('Type--Fixed Price',len(
    data[(data.listingType != 'Auction') & (data.sellingState == 'EndedWithSales')].index) / len(
    data[data.listingType != 'Auction'].index),'False','Sold','Listing'))
# Free shipping true
portions_sold.append(('Shipping--free',len(
    data[(data.isShippingFree == True)  & (data.sellingState == 'EndedWithSales')].index) / len(
    data[(data.isShippingFree == True)].index),'True','Sold', 'Shipping'))
# Free shipping false
portions_sold.append(('Shipping--not free',len(
    data[(data.isShippingFree != True)  & (data.sellingState == 'EndedWithSales')].index) / len(
    data[(data.isShippingFree != True)].index),'False','Sold', 'Shipping'))
# # Returns accepted
# portions_sold.append(('Returns--accepted',len(
#     data[(data.returnsAccepted == True)  & (data.sellingState == 'EndedWithSales')].index) / len(
#     data[(data.returnsAccepted == True)].index),'True','Sold', 'Returns'))
# # Returns accepted
# portions_sold.append(('Returns--not accepted',len(
#     data[(data.returnsAccepted != True)  & (data.sellingState == 'EndedWithSales')].index) / len(
#     data[(data.returnsAccepted != True)].index),'False','Sold', 'Returns'))


# Calculate the portions unsold for features of interest:
portions_unsold =[]
for x in portions_sold:
    portions_unsold.append((x[0],1-x[1],x[2],'Unsold',x[4]))

portions = portions_sold + portions_unsold

# Put into a df
portions_df = pd.DataFrame.from_records(portions, columns=["Name", "Portion","HasFeature","SaleStatus", "Feature"] )


# Make the chart
TOOLS = ''
plt2 = Bar(portions_df,
           label="Name",
           values="Portion",
           stack = "SaleStatus",
           legend="bottom_right",
           color=['Green','Red'],
           xlabel="Listing feature",
           ylabel="Portion sold or unsold",
           title="Impact of listing features on likelihood of sale",
           tools=TOOLS)
plt2.logo = None
plt2.toolbar_location = None

plt2.y_range = Range1d(start=0,end=1)
# Save the plot
output_file("./templates/plot3_new.html")
# show(plt2)


#######################################################
# Look at dependence of sale outcome on seller feedback score
#######################################################


# hist = Histogram(data_sold, values='feedbackScore', color='listingType',
#                  title="Distribution of feedback scores for sold items", legend='top_left')
#
# # Save the plot
# output_file("./templates/data_exploration.html")
# show(hist)

#######################################################
# Look at distributions of sale prices by product
#######################################################


hist = Histogram(data_sold, values='value', color='productId_value',
                 title="Distribution of sale prices by product", legend='top_left')

# Save the plot
output_file("./templates/sales_histogram.html")
show(hist)