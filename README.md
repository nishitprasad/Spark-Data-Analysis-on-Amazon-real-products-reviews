# Amazon-real-products-reviews-data-analysis-via-Spark
Data Analysis of Amazon's real products' reviews using Python and Spark

Using Spark and Python, couple of data analysis criteria have been implemented to get an overall behavior from the reviews data.

The following are the two criterias that have been implemented:  
1. Calculate the average number of review words (based on wordcount).  
2. Group the reviews based on Ratings provided that the wordcount of review-text is more than 100 for each review.  

The input sets used are:  
1. **review.data** - json file containing keys (*"reviewerID", "asin", "reviewText", "overall", "reviewTime"*)  
2. **meta.data** - json file containing keys (*"asin", "price", "categories", "title"*)  

**Operating System** - Ubuntu 14.04  
**Frameworks** - Spark 2.0.1 (in a standalone environment)  
**Language** - Python  
**Spark APIs used** - *groupBy, join, map, filter, reduce* (pySpark)  

Number of master nodes - 1  (Localhost:8080)
Number of slave nodes - 2 (Based on the number of cores, NUMBER_OF_INSTANCES = 2)  

Implementation file names  
Criteria 1 - **AverageWordsReviewCalulcation.py**  
Criteria 2 - **GroupByRatingReviews.py**
