import csv
import uuid, os
import json
from cassandra.query import tuple_factory
import pandas as pd
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
pd.options.mode.chained_assignment = None  # default='warn'


#************************************************************************************
#**************************  Connect with astra.datastax  ***************************
#************************************************************************************

'''
cloud_config= {
        'secure_connect_bundle': 'C:\\Users\\Αρχοντία\\Desktop\\secure-connect-baseis2.zip'
}
auth_provider = PlainTextAuthProvider('aZRLBKibZPunOhLdCTYTOMrD', 'Ho3fz6b.ZpLScuYunSq0NJ8xhrEw8l+-_0wdb1aDWG2qZvzf.jooH8D.BgejmH02dnPeEJ4sStrgtR5vd+-GmIfKPp4bhI72B2Zfm4rB7vKmzwqZ++x2oiNa5LPh2ilB')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

row = session.execute("select release_version from system.local").one()
if row:
    print(row[0])
else:
    print("An error occurred.")

session.execute("USE ssandra;")
'''
#******************************************************************************
#********************  Read from 4 csvs the 50 first rows  ********************
#******************************************************************************


#Read and open movie.csv
csv_filemovie = csv.reader(open('./movie.csv', 'r', encoding="utf-16-le"))
dc1 = []
movie_df = pd.read_csv("movie.csv", sep=';', header=0, on_bad_lines='skip')

#Read and open rating.csv
csv_filerating = csv.reader(open('./rating.csv', 'r', encoding="utf8"))
dc2 = []
rating_df = pd.read_csv("rating.csv", sep=';', header=0, on_bad_lines='skip')

#Read and open tag.csv
csv_filetag = csv.reader(open('./tag.csv', 'r', encoding="utf-16-le"))
dc3 = []
tag_df = pd.read_csv("tag.csv", sep=',', header=0, on_bad_lines='skip')

#Read and open genome_tags.csv
csv_filegenome = csv.reader(open('./genome_tags.csv', 'r', encoding="utf8"))
dc4 = []
genome_tags_df = pd.read_csv("genome_tags.csv", sep=',', header=0, on_bad_lines='skip')


#Q1
#Πρώτο merge για το Q1

q1 = pd.merge(left=rating_df, right=movie_df, how='left', left_on='movieId', right_on='movieId')

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 0)
q1['timestamp']=pd.to_datetime(q1['timestamp'])
#print(q1.head(50))

#Groupby and get sum() and count() {εύρεση του averageRating}
avq1 = q1.groupby('movieId')['rating'].agg(['sum','count'])
avq1['avg_rating'] = avq1['sum'] / avq1['count']
#print(avq1.head(70))

dfq1 = pd.merge(left=q1, right=avq1, how='left', left_on='movieId', right_on='movieId')
#print('\nfinal\n', dfq1.head(50))

#dataframe με τις στήλες που θέλω μόνο
predf1 = dfq1[['movieId', 'avg_rating', 'timestamp', 'rating', 'title']]
predf1['timestamp'] = pd.to_datetime(predf1['timestamp'])
df1 = predf1.head(200)
#print("\nQ1:\n", df1)
#csv_data = df1.to_csv('moviesbyRMIKRO.csv', index=False)


#Q2
#Εμφάνιση των ταινιών που περιέχουν τη λέξη “star”

df2 = movie_df.head(200)
newdf2 = df2.copy()
newdf2['title']= newdf2['title'].str.split(" ", expand =False)

newdf2=newdf2.rename(columns={"title": "new title"})
del newdf2['movieId']
del newdf2['genres']
#print(newdf2)

df2['new'] = newdf2['new title'].values

df2_final = df2.head(200)


#df2_new=df2["title"].astype(str).values.tolist()   res = pd.Series(df2_new)
#df2 = df2.append(pd.DataFrame([df2_new],index=[],columns=df2.columns))
#df2 = df2({'test_set': value for value in df2_new})
#df2 = df2.append(pd.Series(df2_new, index=df2.columns[:len(df2_new)]), ignore_index=True)
#df2.loc[len(df2)]=df2_new
#for i,item in df2.iterrows():
    #col_list = df2["title"].values.tolist()
    #print(col_list)
   #df2["title"] = df2.replace('\n', ' ').split(".")
   #df2['title'] = df2['title'].apply(lambda x: x.split())

#df2.fillna(0)
#print("\nQ2:\n", df2_final.head(100))


#Q3
#Τρίτο merge για το Q3

dfq3 = pd.merge(left=q1, right=avq1, how='left', left_on='movieId', right_on='movieId')
predf3 = dfq3[['movieId', 'timestamp', 'genres', 'avg_rating', 'title']]

newpredf3 = predf3.copy()
#for index, row in predf3.iterrows():
newpredf3['new genres']= newpredf3['genres'].str.split("|", expand =False)
del predf3['genres']

#print("\nNEWpredf3:\n", newpredf3.head(200))
#predf3.concat([predf3,newpredf3], axis=0, ignore_index=True)
#predf3=predf3['genres'].str.split("|")
predf3['genres'] = newpredf3['new genres'].values
FINALpredf3 = predf3.copy()
FINALpredf3['title'] = ( FINALpredf3.title.str.split().apply(lambda x: ' '.join(x[::-1]).rstrip(' '))  .where(FINALpredf3['title'].str.contains(' '),FINALpredf3['title']) .str.replace(' ','  ') )
FINALpredf3['title']= FINALpredf3['title'].str.split(" ", expand =False)
#FINALpredf3[['title1','title2','title3']] = pd.DataFrame(FINALpredf3.title.tolist(), index= FINALpredf3.index)
FINALpredf3["new_col"] = FINALpredf3["title"].str[0]
FINALpredf3= FINALpredf3.replace(to_replace='\(', value="", regex=True)
FINALpredf3= FINALpredf3.replace(to_replace='\)', value="", regex=True)
del FINALpredf3['timestamp']
del FINALpredf3['title']
del FINALpredf3['genres']
del FINALpredf3['movieId']
del FINALpredf3['avg_rating']
#FINALpredf3['new_col'] = FINALpredf3['new_col'].str.replace(r"\(.*\)","")
#FINALpredf3=FINALpredf3.head(50)
print(FINALpredf3)
predf3['new TITLE'] = FINALpredf3['new_col'].values
df3 = predf3.head(200)

#df3.fillna(0)
print("\nQ3:\n", df3)


#Q4
#Τέταρτο merge για το Q4

#premergedQ4 = dfq3[['movieId', 'title', 'genres', 'avg_rating']]
#print("\npremergedQ4:\n", premergedQ4.head(10))

dfq4 = pd.merge(left=movie_df, right=tag_df, how='left', left_on='movieId', right_on='movieId')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 0)
#print("\ndfq4:\n", dfq4.head(100))

Q4 = dfq4.groupby('movieId').head(5)
#print("\nQ4:\n", Q4.head(100))

del Q4['userId']
del Q4['timestamp']

Q4.rename(columns={"tag":"topn_tag"}, inplace=True)
#print("\nQ4:\n", Q4.head(100))

Q4['s']=Q4.groupby(['movieId', 'title', 'genres']).cumcount()+1
Q4=Q4.set_index(['s', 'movieId', 'title', 'genres']).unstack(0)
Q4.columns=[f"{x}" for x in Q4.columns]
Q4=Q4.reset_index()

Q4['topn_tags'] = Q4["('topn_tag', 1)"] + (', ' + Q4["('topn_tag', 2)"]).fillna('') + (', ' + Q4["('topn_tag', 3)"]).fillna('') + (', ' + Q4["('topn_tag', 4)"]).fillna('') + (', ' + Q4["('topn_tag', 5)"]).fillna('')

del Q4["('topn_tag', 1)"]
del Q4["('topn_tag', 2)"]
del Q4["('topn_tag', 3)"]
del Q4["('topn_tag', 4)"]
del Q4["('topn_tag', 5)"]


prefinaldf4 = pd.merge(left=Q4, right=avq1, how='left', left_on='movieId', right_on='movieId')


#dataframe με τις στήλες που θέλω μόνο
prepredfQ4 = prefinaldf4[['movieId', 'title', 'genres', 'topn_tags', 'avg_rating']]
#del prepredfQ4["avg_rating"]
df4 = prepredfQ4.head(200)
df4['avg_rating'] = df4['avg_rating'].fillna(0)
#print("\nQ4:\n", df4)


#Q5
predf5 = pd.merge(left=df1, right=tag_df, how='left', left_on='movieId', right_on='movieId')
preQ5 = predf5[['movieId', 'title', 'avg_rating', 'tag']]
df5 = preQ5.head(200)
#df5.fillna(0)
#print("\nQ5:\n", df5)

'''
#***************************************************************
#**************  Create table moviesbyAVGRATE  *****************
#***************************************************************

session.execute("DROP TABLE IF EXISTS ssandra.moviesbyAVGRATE")


session.execute("CREATE TABLE IF NOT EXISTS moviesbyAVGRATE(movieId int, avg_rating float, timestamp timestamp, rating float, title text, PRIMARY KEY (movieId));")
query = "INSERT INTO moviesbyAVGRATE(movieId,avg_rating,timestamp,rating,title) VALUES (?,?,?,?,?)"
prepared = session.prepare(query)

from cassandra.query import dict_factory
session = cluster.connect('ssandra')
session.row_factory = dict_factory
#rows = session.execute("SELECT userId FROM moviesq1 LIMIT 1")

#FIRST TRY SELECT QUERY
for i,item in df1.iterrows():
        session.execute(prepared, (item[0],item[1],item[2],item[3],item[4]))

'''
'''
#***************************************************************
#*****************  Create table moviesbyT  ********************
#***************************************************************


session.execute("DROP TABLE IF EXISTS ssandra.moviesbyT")


session.execute("CREATE TABLE IF NOT EXISTS moviesbyT(movieId int, title text, genres ascii, new list<text>, PRIMARY KEY (movieId));")
query = "INSERT INTO moviesbyT(movieId, title, genres, new) VALUES (?,?,?,?)"
prepared = session.prepare(query)

from cassandra.query import dict_factory
session = cluster.connect('ssandra')
session.row_factory = dict_factory

#FIRST TRY SELECT QUERY
for i,item in df2_final.iterrows():
        session.execute(prepared, (item[0],item[1],item[2], item[3]))


#***************************************************************
#*****************  Create table moviesbyG  ********************
#***************************************************************
'''
'''
session.execute("DROP TABLE IF EXISTS ssandra.moviesbyG")


session.execute("CREATE TABLE IF NOT EXISTS moviesbyG(movieId int,timestamp timestamp,avg_rating  float ,title text, genres list<text>, PRIMARY KEY (movieId));")
query = "INSERT INTO moviesbyG(movieId, timestamp,avg_rating,title,genres) VALUES (?,?,?,?,?)"
prepared = session.prepare(query)

from cassandra.query import dict_factory
session = cluster.connect('ssandra')
session.row_factory = dict_factory

#FIRST TRY SELECT QUERY
for i,item in df3.iterrows():
        session.execute(prepared, (item[0],item[1],item[2],item[3],item[4]))


'''

#***************************************************************
#*****************  Create table movieinfo  ********************
#***************************************************************

'''
session.execute("DROP TABLE IF EXISTS ssandra.movieinfo")

session.execute("CREATE TABLE IF NOT EXISTS movieinfo(movieId int, title text, genres ascii, topn_tags text,avg_rating float, PRIMARY KEY (movieId));")
query = "INSERT INTO movieinfo(movieId, title,genres ,topn_tags,avg_rating) VALUES (?,?,?,?,?)"
prepared = session.prepare(query)

prepared.bind(str(avg_rating) for avg_rating in row)
prepared.bind(str(movieId) for movieId in row)
from cassandra.query import dict_factory
session = cluster.connect('ssandra')
session.row_factory = dict_factory

#FIRST TRY SELECT QUERY
for i,item in df4.iterrows():

        session.execute(prepared, (item[0],item[1],item[2],item[3],item[4]))

'''

#***************************************************************
#*****************  Create table topnmovies  ********************
#***************************************************************
'''

session.execute("DROP TABLE IF EXISTS ssandra.topnmovies")


session.execute("CREATE TABLE IF NOT EXISTS topnmovies(movieId int, title text, avg_rating float, tag text,  PRIMARY KEY (movieId));")
query = "INSERT INTO topnmovies(movieId, title, avg_rating, tag) VALUES (?,?,?,?)"
prepared = session.prepare(query)



from cassandra.query import dict_factory
session = cluster.connect('ssandra')
session.row_factory = dict_factory

#FIRST TRY SELECT QUERY
for i,item in df5.iterrows():
        session.execute(prepared, (item[0],item[1],item[2],item[3]))


cloud_config= {
        'secure_connect_bundle': 'C:\\Users\\Αρχοντία\\Desktop\\secure-connect-baseis2.zip'
}
auth_provider = PlainTextAuthProvider('aZRLBKibZPunOhLdCTYTOMrD', 'Ho3fz6b.ZpLScuYunSq0NJ8xhrEw8l+-_0wdb1aDWG2qZvzf.jooH8D.BgejmH02dnPeEJ4sStrgtR5vd+-GmIfKPp4bhI72B2Zfm4rB7vKmzwqZ++x2oiNa5LPh2ilB')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()


row = session.execute("select release_version from system.local").one()
if row:
    print(row[0])
else:
    print("An error occurred.")

cluster = Cluster()
cluster = Cluster(['192.168.0.1', '192.168.0.2'])

session.execute("USE ssandra;")

'''
