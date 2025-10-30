name = http.args['name']
import MySQLdb
conn = MySQLdb.connect(host='alfred.sparktools.us', user='test', passwd='test', db='test')
cur = conn.cursor()
sql = 'insert into sport (name) values (%s)'
args = (name,)
cur.execute(sql, args)
conn.commit()
conn.close()
redirect('sports')

