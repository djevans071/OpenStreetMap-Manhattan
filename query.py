import sqlite3
import pandas as pd

def select(filename, QUERY):
	con = sqlite3.connect(filename)
	df = pd.read_sql_query(QUERY, con)
	con.close()
	return df

if __name__ == '__main__':

	# find the total number of tags with postal codes
	QUERY = """
		SELECT COUNT(a.value) AS total_postalTags
		FROM (SELECT * FROM nodes_tags UNION ALL
			  SELECT * FROM ways_tags) a
		WHERE a.key = 'postcode';
	"""

	# find number of tags with postal codes grouped by borough
	QUERY0 = """
		SELECT CASE
					WHEN (a.value BETWEEN 10000 AND 10299)
						THEN 'manhattan'
					WHEN (a.value LIKE '112%')
						THEN 'brooklyn'
					WHEN (a.value LIKE '104%' OR a.value = '11370')
						THEN 'bronx'
					WHEN (a.value LIKE '07%')
						THEN 'nj'
					WHEN (a.value LIKE '111%'
						OR	   (a.value LIKE '113%' AND a.value != '11370')
						OR 	   a.value LIKE '114%'
						OR 	   a.value LIKE '116%'
						OR 	   a.value between '11004' AND '11005')
						THEN 'queens'
					END as borough,
			   COUNT(a.value) AS numTags
		FROM (SELECT * FROM nodes_tags UNION ALL
			  SELECT * FROM ways_tags) a
		WHERE a.key = 'postcode'
		GROUP BY borough
		ORDER BY numTags DESC;
	"""

	# number of nodes
	QUERY_numNodes = """
		SELECT count(*) as numNodes FROM nodes;
	"""

	# number of ways
	QUERY_numWays = """
		SELECT count(*) as numWays FROM ways;
	"""

	# number of unique users
	QUERY_numUsers = """
		SELECT count(distinct(a.uid)) AS numUsers
		FROM (SELECT uid FROM nodes UNION ALL
			  SELECT uid FROM ways) a;
	"""

	# top 10 users by contribution
	QUERY_topUsers = """
		SELECT a.user, count(*) AS num
		FROM (SELECT user FROM nodes UNION ALL
			  SELECT user FROM ways) a
		GROUP BY 1
		ORDER BY 2 DESC
		LIMIT 10;
	"""

	# number of users contributing once
	QUERY_numOnetimeUsers = """
		SELECT count(*) as numOnetimeUsers
		FROM (
			SELECT a.user, count(*) as num
			FROM (SELECT user FROM nodes UNION ALL
				  SELECT user FROM ways) a
			GROUP BY 1
			HAVING num=1) u;
	"""

	QUERY_topZips = """
		SELECT a.value, count(*) as numTags
		FROM nodes_tags a
		WHERE a.key = 'postcode'
		GROUP BY 1
		ORDER BY 2 DESC
		LIMIT 5;
	"""

	# top 5 Manhattan zip codes
	QUERY_topManZips = """
		SELECT a.value, count(*) as numTags
		FROM nodes_tags a
		WHERE a.key = 'postcode'
		AND (a.value BETWEEN 10000 AND 10299)
		GROUP BY 1
		ORDER BY 2 DESC
		LIMIT 5;
	"""

	# top 10 amenities
	QUERY_topAmenities = """
		SELECT nodes_tags.value, COUNT(*) as num
		FROM nodes_tags
		WHERE nodes_tags.key='amenity'
		GROUP BY nodes_tags.value
		ORDER BY num DESC
		LIMIT 10;
	"""

	# return a list of values for the capacities of bikeracks
	QUERY_bikerackCaps = """
		SELECT value
		FROM nodes_tags
	    	JOIN (SELECT DISTINCT(id) FROM nodes_tags
				  WHERE value='bicycle_parking') i
	    	ON nodes_tags.id=i.id
		WHERE nodes_tags.key = 'capacity';
	"""

	# top 10 bike rack capacities
	QUERY__ = """
		SELECT value as capacity, count(*) as num
		FROM nodes_tags
			JOIN (SELECT DISTINCT(id) FROM nodes_tags
				  WHERE value='bicycle_parking') i
				  ON nodes_tags.id=i.id
		WHERE nodes_tags.key = 'capacity'
		GROUP BY 1
		ORDER BY 2 DESC
		LIMIT 10;
	"""

	# print select('opensm-manhattan.db', QUERY_numNodes)
	# print select('opensm-manhattan.db', QUERY_numWays)
	# print select('opensm-manhattan.db', QUERY_numUsers)
	# print select('opensm-manhattan.db', QUERY_topUsers)
	# print select('opensm-manhattan.db', QUERY_numOnetimeUsers)
	# print select('opensm-manhattan.db', QUERY)
	# print select('opensm-manhattan.db', QUERY0)
	# print select('opensm-manhattan.db', QUERY_topZips)
	# print select('opensm-manhattan.db', QUERY_topManZips)
	# print select('opensm-manhattan.db', QUERY_topAmenities)
	# print select('opensm-manhattan.db', QUERY_)

	df = select('opensm-manhattan.db', QUERY_bikerackCaps)
	df = df.apply(pd.to_numeric)
	print df[df.value == 0].size

	print select('opensm-manhattan.db', QUERY__)
