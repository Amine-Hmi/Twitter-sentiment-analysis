from pymongo import MongoClient
import config
client = MongoClient(`mongodb+srv://${config.DB_USER}:${config.DB_PASS}@cluster0.udb8f.mongodb.net/myFirstDatabase?retryWrites=true&w=majority`)
#db = client.test
#print('databases:',client.list_database_names())    
#print('colections:',db.list_collection_names())
db = client['tweets_db']
db_names = client.list_database_names()
collection_names = db.list_collection_names()

#Create database if empty
def db_init():
    if 'tweets_db' not in db_names:
        print ("creating database!")
        client['tweets_db']
    #else:
    #    print ("deleting database!")
    #    client.drop_database('tweets_db')
#Create collection if empty
    if 'tweets_collection' in collection_names:
        print ("Collection exists!")
        client['tweets_db']["tweets_collection"].drop()

    else:
        client['tweets_db']["tweets_collection"]


#dummy tweet to insert in order to confirm databse creation(for test only)
#client['tweets_db']["tweets_collection"].insert_one({
#"_id" : "1510360267955347470",
#"created_at" : "2022-04-02 20:55:23+00:00",
#"user_screen_name" : "patrici82472047",
#"text" : "All the stars who have been expelled from the Academy",
#"text_neg" : 0.154,
#"text_neu" : 0.846,
#"text_pos" : 0.0,
#"text_com" : -0.25,
#"score" : "Negative"
#})
