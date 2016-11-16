# Amazon real products reviews data analysis via Spark
Data Analysis of Amazon's real products' reviews using Python and Spark

Using Spark and Python, couple of data analysis criteria have been implemented to get an overall behavior from the reviews data.

The following are the two criterias that have been implemented:  
1. Calculate the average number of review words (based on wordcount).  
2. Group the reviews based on Ratings provided that the wordcount of review-text is more than 100 for each review.  

The input sets used are:  
1. **review.data** - json file containing keys (*"reviewerID", "asin", "reviewText", "overall", "reviewTime"*)  
2. **meta.data** - json file containing keys (*"asin", "price", "categories", "title"*)  
```
Operating System - Ubuntu 14.04  
Framework - Spark 2.0.1 (in a standalone environment)  
Language - Python  
Spark APIs used - *groupBy, join, map, filter, reduce* (pySpark)  
```
Number of master nodes - 1  (Localhost:8080)  
Number of slave nodes - 2 (Based on the number of cores, NUMBER_OF_INSTANCES = 2)  

Implementation file names  
Criteria 1 - **AverageWordsReviewCalulcation.py**  
Criteria 2 - **GroupByRatingReviews.py**

Spark Data Processing Program

##Summary

The program GroupByRatingsReviews.py focuses on grouping those reviews having more than 100 words by "Overall" rating.
The prorgram AverageWordsReviewCalculation.py focuses on calculating the required average of the review wordcount for each review belonging to "Music" category

##Design

For group by ratings, map function is called to mark those reviews that have word count > 100. The map function will take the following function implementation:
```
if(line json key "reviewText" has word value length > 100)
	return (rating by the key "Overall", reviewText)
else
	return None
```
- The resultant RDD will be filter by removing all *None* rows.
- Now the RDD will have only rating and respective review text.
- groupByKey() is called to group this RDD's contents by rating.
- The resultant data is saved in files as distributed by the slaves in a specified folder GroupByRatingsReview_Result.

For Average words calculation, first the map function is called to replace the review RDD's contents with values of key **"```asin```"** along with respective review text word count.

Then meta RDD's contents are replaced by those meta data that belong to category "Music". The map function will take the following function implmentation:
```
if(line json key "categories" has value "Music")
	return (asin number by key "asin", dummy_value 1)
else
	return None
```
- This meta RDD is filtered by removing all *None* rows.
- Now this RDD will have only asin numbers (with respective dummy value 1) belonging to **"Music"** category.
- The meta RDD and review RDD are joined with common values being the asin numbers
- The resultant joined RDD will have asin numbers with respective review text word count (and a dummy value 1)
- This joined RDD is mapped and updated with respective word counts. So the resultant joined RDD will have rows of the word counts.
- Now the reduce() method is used to calculate the total sum of the word counts in the joined RDD.
- The count() method is used to calculate the the total number of rows (total number of reviews).
- The average is calculated via (total sum)/(total count) which is stored in a text file.


##Implementation

- Group By Ratings

    The following is the necessary implementation in Python:
    ```python
    #Define a function that returns rating and respective reviewID per record
    def getRatingAndReview(line):
    	lineData = json.loads(line)
    	setOfWords = re.split(ur"[A-Za-z]+", lineData.get("reviewText"), flags = re.UNICODE)
    	reviewerText = lineData.get("reviewText")
    	rating = lineData.get("overall")
    	if len(setOfWords) > 100:
    		return (rating, str(reviewerText))
    	return None
    
    #Read the review file and convert into RDD
    reviewRDD = sc.textFile("file:///home/hduser/Desktop/DIC_Spark/review.data")
    reviewRDD = reviewRDD.map(getRatingAndReview) #Map with new RDD containing just Rating and Respective Review
    reviewRDD = reviewRDD.filter(lambda line: line!=None) #Filter the RDD with any record having no 'None' values
    
    #Convert to new RDD containing Ratings and consolidated reviews (grouped by ratings)
    reviewRDD = sc.parallelize(reviewRDD.groupByKey().map(lambda line: (line[0], list(line[1]))).collect())
    
    #Save respective RDD in a folder (may contain multiple files as work is ditributed among the slaves)
    reviewRDD.saveAsTextFile("file:///home/hduser/Desktop/DIC_Spark/GroupByRatingsReview_Result")
    ```
- Average Calculation:
    The following is the necessary implementation in Python:
    ```python
    #Define a function to get the asin (common column) values and respective review wordcount
    def getCount(line):
        lineData = json.loads(line)
        setOfWords = re.split(ur"[A-Za-z]+", lineData.get("reviewText"), flags = re.UNICODE)
    	return (str(lineData.get("asin")), len(setOfWords))
        
    #Define a function to get Music category records having respective asin (commun column) values and an extra dummy column
    def getMusicRecords(line):
    	lineData = json.loads(line)
    	if lineData.get("categories")=="Music":
    		return (str(lineData.get("asin")), "1")
    	return None
    
    #Read the review file and convert into RDD
    reviewRDD = sc.textFile("file:///home/hduser/Desktop/DIC_Spark/review.data")
    reviewRDD = reviewRDD.map(getCount) #Map the review RDD with new RDD containing asin and respective review wordcount
        
    #Read the meta file and convert into RDD
    metaRDD = sc.textFile("file:///home/hduser/Desktop/DIC_Spark/meta.data")
    metaRDD = metaRDD.map(getMusicRecords) #Map the meta RDD with new RDD containing either None values, or asin and dummy
    metaRDD = metaRDD.filter(lambda line: line!=None) #Filter the RDD with only those values that do not have None values
    
    #Joined RDD containing one common column having asid values, followed by respective nested tuple of other column values)
    #The nested tuple contains just the dummy value and the wordcount
    joinedRDD = sc.parallelize(sorted(metaRDD.join(reviewRDD).collect())) #sorted lexicographically
    joinedRDD.saveAsTextFile("file:///home/hduser/Desktop/DIC_Spark/joinedRDD_result") # save file to a local path, starting with prefix file://
    joinedRDD = joinedRDD.map(lambda line: int(line[1][1])) #Map this RDD with new RDD containing just the wordcounts
    
    #Calculate the total sum and count to calculate the average review wordcount
    totalSum = joinedRDD.reduce(add)
    count = joinedRDD.count()
    with open('AverageNumberOfReviewWords.txt', 'w') as f:
    	f.write("Total Sum: "str(totalSum) + " Total Count: " + str(count) + " Required Average: " + str(round(totalSum/float(count), 2)))
    
    #Save respective RDDs in a folder (may contain multiple files as work is ditributed among the slaves)
    reviewRDD.saveAsTextFile("file:///home/hduser/Desktop/DIC_Spark/reviewRDD_AvgCalc_MidResult")
    metaRDD.saveAsTextFile("file:///home/hduser/Desktop/DIC_Spark/metaRDD_AvgCalc_MidResult")
    ```

##Build Commands
	
For starting the master node:
```./start-master.sh```

For starting the slave nodes: (NUMBER_OF_INSTANCES = 2)
```./start-slave.sh spark://nishit:7077``` (Can give your own Master Node URL)

The following are the commands that shall be run for the respective files:
```./spark-submit GroupByRatingsReviews.py```

```./spark-submit AverageWordsReviewCalculation.py```

Please note all required files are in the same folder but the average calculation done is stored in a text file that gets saved on the current command line folder location (where these commands are getting executed)


```
Copyright [2016] [Nishit Prasad]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
