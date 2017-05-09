import MySQLdb
conn = MySQLdb.connect(host='alfred.sparktools.us', user='test', passwd='test', db='test')
sql = 'select name from sport'
cur = conn.cursor()
cur.execute(sql)
sports = [name for (name,) in cur] 
# print('conn={}'.format(conn))
