import MySQLdb
conn = MySQLdb.connect(host='alfred.sparktools.us', user='test', passwd='test', db='test')
sql = 'select name from team where sport=%s'
name = http.args['name']
args=(name,)
cur = conn.cursor()
cur.execute(sql, args)
teams = [name for (name,) in cur]

