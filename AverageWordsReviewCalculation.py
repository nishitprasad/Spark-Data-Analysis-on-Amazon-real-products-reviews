#import necessary library
import json
import re
from pyspark import SparkConf, SparkContext
from operator import add

conf = SparkConf()
conf.setMaster("--Spark-Master-URL--")# set to your spark master url
conf.setAppName("averageCalculation")
sc = SparkContext(conf = conf)

#Define a function to get the asin (common column) values and respective review wordcount
def getCount(line):
	lineData = json.loads(line)
	setOfWords = re.split(ur"[A-Za-z]+", lineData.get("reviewText"), flags = re.UNICODE)
	return (str(lineData.get("asin")), len(setOfWords))

#Define a function to get Music category records having respective asin (commun column) values and an extra dummy value column (=1)
def getMusicRecords(line):
	lineData = json.loads(line)
	if lineData.get("categories")=="Music":
		return (str(lineData.get("asin")), "1")
	return None

#Read the review file and convert into RDD
reviewRDD = sc.textFile("file:///home/../review.data")
reviewRDD = reviewRDD.map(getCount) #Map the review RDD with new RDD containing asin and respective review wordcount

#Read the meta file and convert into RDD
metaRDD = sc.textFile("file:///home/../meta.data")
metaRDD = metaRDD.map(getMusicRecords) #Map the meta RDD with new RDD containing either None values, or asin and dummy value
metaRDD = metaRDD.filter(lambda line: line!=None) #Filter the RDD with only those values that do not have None values

#Joined RDD containing one common column having asid values, followed by respective nested tuple of other column values)
#The nested tuple contains just the dummy value and the wordcount
joinedRDD = sc.parallelize(sorted(metaRDD.join(reviewRDD).collect())) #sorted lexicographically
joinedRDD.saveAsTextFile("file:///home/../joinedRDD_result") # save file to a local path, starting with prefix file://
joinedRDD = joinedRDD.map(lambda line: int(line[1][1])) #Map this RDD with new RDD containing just the wordcounts

#Calculate the total sum and count to calculate the average review wordcount, store the result in a text file
totalSum = joinedRDD.reduce(add)
count = joinedRDD.count()
with open('AverageNumberOfReviewWords.txt', 'w') as f:
	f.write("Total Sum: "str(totalSum) + " Total Count: " + str(count) + " Required Average: " + str(round(totalSum/float(count), 2)))

#Save respective RDDs in a folder (may contain multiple files as work is ditributed among the slaves)
reviewRDD.saveAsTextFile("file:///home/../reviewRDD_AvgCalc_MidResult")
metaRDD.saveAsTextFile("file:///home/../metaRDD_AvgCalc_MidResult")
