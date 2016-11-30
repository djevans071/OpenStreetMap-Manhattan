import sqlite3
import pandas as pd

def select(filename, QUERY):
	con = sqlite3.connect(filename)
	df = pd.read_sql_query(QUERY, con)
	con.close()
	return df

if __name__ == '__main__':

	QUERY = """
	    SELECT a.value, count(*) FROM nodes_tags a, nodes b
		WHERE a.id = b.id
		AND   a.key = 'postcode'
		GROUP BY a.value
		ORDER BY 2 DESC;
	"""

	QUERY1 = """
		SELECT *
		FROM (SELECT * FROM nodes_tags UNION All
			SELECT * FROM ways_tags) tags
		WHERE   tags.key = 'postcode'
		AND (length(tags.value) < 5) OR tags.value = '97657';
	"""

	print select('opensm-manhattan.db', QUERY1)
