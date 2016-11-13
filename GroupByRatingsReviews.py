import json
import re
from pyspark import SparkConf, SparkContext

conf = SparkConf()
conf.setMaster("--Spark-Master-URL--")# set to your spark master url
conf.setAppName("GroupByRatingsReview")
sc = SparkContext(conf = conf)

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
reviewRDD = sc.textFile("file:///home/../review.data")
reviewRDD = reviewRDD.map(getRatingAndReview) #Map with new RDD containing just Rating and Respective Review
reviewRDD = reviewRDD.filter(lambda line: line!=None) #Filter the RDD with any record having no 'None' values

#Convert to new RDD containing Ratings and consolidated reviews (grouped by ratings)
reviewRDD = sc.parallelize(reviewRDD.groupByKey().map(lambda line: (line[0], list(line[1]))).collect())

#Save respective RDD in a folder (may contain multiple files as work is ditributed among the slaves)
reviewRDD.saveAsTextFile("file:///home/../GroupByRatingsReview_Result")
