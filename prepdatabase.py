import json
import pandas as pd
from pymongo import MongoClient
from functions.mongo import connectCollection

db, coll = connectCollection('api-project','chats')
with open('./input/chats.json', encoding="utf8") as f:
    chats_json = json.load(f)
coll.insert_many(chats_json)

df = pd.read_json('./input/chats.json', orient='records')

dfNew = df[['userName', 'idUser']]

dfNew = dfNew[['userName', 'idUser']].mask(dfNew[['userName', 'idUser']].duplicated())

dfNew = dfNew.dropna()

dfNew.to_json('./output/users.json', orient='records')

coll2 = db['users']
coll2.insert_many(dfNew.to_dict('records'))

dfchats = dfchats.drop(['index'], axis=1)

coll3 = db['chatsid']
coll3.insert_many(dfchats.to_dict('records'))

dfchats.to_json("./output/justchats.json", orient='records')

db, coll = connectCollection('api-project','users')
data = list(coll.find({}))
user_id_list = []
for i in range(len(df)):
    for e in data:
        if df.at[i,'idUser'] == e['idUser']:
            user_id_list.append(e['_id'])
df['user_id'] = user_id_list
coll4 = db['messages']
coll4.insert_many(df.to_dict('records'))