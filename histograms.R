library(readr)
library(ggplot2)
library(plyr)

# Read in the data
df <-read_csv("Development/EbayAnalytics/Data/ebay_data.csv")

str(df)

# Subset to sold data
df.sold <- subset(df, sellingState == "EndedWithSales")
df$feedbackRatingStar

#################################
# Product histogram
#################################

# Subset to desired products
products = names(sort(table(df.sold$productId_value), decreasing = F)[1:6])
df.sold.prod = subset(df.sold, productId_value %in% products)
df.sold.prod$productId_value <- factor(df.sold.prod$productId_value)
df.sold.prod$productId_value <- reorder(df.sold.prod$productId_value, df.sold.prod$value, mean)

# Plot the histograms
hist_prod <- ggplot(df.sold.prod, aes(x = value, color = isShippingFree)) + 
  xlim(c(0,1500)) +
  ggtitle("Distribution of sale prices for top selling products")+
  xlab("Sale value in USD")+
  geom_line(stat="density", bw=37)+
  facet_wrap(~productId_value, ncol = 1)+
  theme(legend.position = "top")

hist_prod
# Save the plot as a png
ggsave("Development/EbayAnalytics/static/product_hist.png", hist_prod,
       width = 6, height = 11, units = "in")

#################################
# Effect of free shipping on value histogram
#################################

# df.2 <- df
# products.2 = names(sort(table(df.sold$productId_value), decreasing = TRUE)[1:10])
# 
# sort(table(df.sold$productId_value), decreasing = TRUE)[1:10]
# 
# df.sold.prod.2 = subset(df.sold, productId_value %in% products.2)
# df.sold.prod.2$productId_value <- factor(df.sold.prod.2$productId_value)
# df.sold.prod.2$productId_value <- reorder(df.sold.prod.2$productId_value, df.sold.prod.2$value, mean)
# 
# df.sold.prod.2 <- ddply(.data = df.sold.prod.2,
#                 .variables = .(productId_value), 
#                 .fun = function(x){
#                   x$value <- scale(x$value, scale = F)
#                   return(x)
#                   })
# 
# box_shipping <- ggplot(df.sold.prod.2, aes(x = productId_value, y=value, fill=isShippingFree)) +
#   ylim(c(-350,350))+
#   ggtitle("Distribution of feedback scores")+ 
#   geom_boxplot()
#   
# box_shipping
# 
# # Save the plot as a png
# ggsave("Development/EbayAnalytics/static/freeshipping_boxplot.png", 
#        box_shipping,
#        width = 1.15*8,
#        height = 1.15*5,
#        units = "in")


