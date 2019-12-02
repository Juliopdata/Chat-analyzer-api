from bottle import route, run, get, post, request
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity as distance
from src.recommender import *
import numpy as np
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')
import datetime
import os
import bson
from bson.json_util import dumps
import re
from src.sentiment import *
from functions.mongo import connectCollection
from dotenv import load_dotenv
load_dotenv()

db, coll = connectCollection('api-project', 'chats')
db, users = connectCollection('api-project', 'users')
db, chatsCR = connectCollection('api-project', 'chatsCR')
#db, msgs = connectCollection('api-project', 'messages')

def main():

    @get("/")
    def test():
        return ''' WELCOME TO MY API'''


    @get("/user/create")
    def userForm():
        return '''
            <form action="/user/create" method="post">
                Enter a new Username: <input name="username" type="text" />
                <input type="submit" />
            </form>'''


    @post("/user/create")
    def createUser():
        username = str(request.forms.get('username'))
        newUser = {'idUser': users.distinct(
            "idUser")[-1] + 1, 'userName': username}
        usersdata = list(users.aggregate([{'$project': {'userName': 1}}]))
        if newUser['userName'] in [e['userName'] for e in usersdata]:
            return {'Error! Username already in use'}
        else:
            user_id = users.insert_one(newUser).inserted_id
        return {'userName': username, 'UserId': int(newUser['idUser'])}


    @get("/chat/create")
    def userForm():
        return '''
            <form action="/chat/create" method="post">
                Enter 2 UsersID for a chat: <input name="users" type="text" />
                <input type="submit" />
            </form>
        '''


    @post('/chat/create')
    def createChat():
        userslist = str(request.forms.get('users'))
        userslist = list(userslist.split(","))
        userslistF = []
        for i in userslist:
            userslistF.append(int(i))
        print(userslistF)
        chatsids = list(chatsCR.aggregate([{'$project': {'idChat': 1}}]))
        usersdata = list(users.aggregate([{'$project': {'idUser': 1}}]))
        chatID = max([e['idChat'] for e in chatsids])+1
        listausers = []
        for h in usersdata:
            listausers.append(int(h['idUser']))
        for e in userslistF:
            if int(e) not in listausers:
                return 'ERROR! Unknown Users. You must <a href="/user/create">CREATE</a> the User first'
            else:
                
                newchat = {'idChat': int(chatID), 'users': str(userslistF)}
                message_id = chatsCR.insert_one(newchat).inserted_id
                return dumps(newchat)


    @get('/chat/adduser')
    def messageForm():
        return '''<form method="post" action="/chat/adduser">
                    Insert a UserID: <input name="user" type="text" />
                    Insert a ChatID: <input name="chatID" type="text" />
                    <input type="submit" />
                </form>'''


    @post('/chat/adduser')
    def addUserToChat():
        chatid = int(request.forms.get('chatID'))
        user = int(request.forms.get('user'))
        data = list(chatsCR.find({'idChat': int(chatid)}))
        if len(data) == 0:
            return 'ERROR! Unknown chat. You must <a href="/chat/create">CREATE</a> the Chat first.'
        usersData = list(users.aggregate([{'$project': {'idUser': 1}}]))
        if user not in [e['idUser'] for e in usersData]:
            return 'ERROR! Unknown User. You must <a href="/user/create">CREATE</a> the User first.'
        listusers = [int(e)
                    for e in re.sub('\[|\]', '', data[0]['users']).split(', ')]
        if user in listusers:
            return 'ERROR! User already in User List'
        listusers.append(user)
        coll.update_one({'idChat': int(chatid)}, {
                        '$set': {'users': str(listusers)}})
        return {'UserId': user, 'ChatId': int(chatid)}


    @get('/chat/addmessage')
    def messageForm():
        return '''<form method="post" action="/chat/addmessage">
                    Insert a UserID: <input name="user" type="text" />
                    Insert a ChatID: <input name="chatID" type="text" />
                    Insert a Message: <input name="message" type="text" />

                    <input type="submit" />
                </form>'''


    @post('/chat/addmessage')
    def addMessageToChat():

        chatID = int(request.forms.get('chatID'))
        user = int(request.forms.get('user'))
        message = str(request.forms.get('message'))
        data = list(coll.find({'idChat': int(chatID)}))
        chats = list(chatsCR.aggregate([{'$project': {'idChat': 1}}]))
        chats = [int(x.get('idChat')) for x in chats]
        if chatID not in chats:
            return 'ERROR! Unknown chat. You must <a href="/chat/create">CREATE</a> the Chat first.'
        chato = list(chatsCR.find({'idChat': int(chatID)}))
        usersData = list(users.aggregate([{'$project': {'idUser': 1}}]))
        if user not in [e['idUser'] for e in usersData]:
            return 'ERROR! Unknown User. You must <a href="/user/create">CREATE</a> the User first.'
        selectedUser = list(users.find({'idUser': user}))
        if len(data) == 0:
            newMessageId = 0
        else:
            newMessageId = max([e['idMessage'] for e in data])+1
        newMessage = {'datetime': datetime.datetime.utcnow(),
                    'idChat': int(chatID),
                    'idMessage': newMessageId,
                    'idUser': user,
                    'text': message,
                    'userName': selectedUser[0]['userName'],
                    'user_id': selectedUser[0]['_id']}
        message_id = coll.insert_one(newMessage).inserted_id
        return dumps(newMessage)


    @get('/chat/<chat_id>/list')
    def getMessages(chat_id):
        data = list(coll.find({'idChat': int(chat_id)}))
        messages = {}

        for index, dictionary in enumerate(data):
            index += 1
            messages[f'message_{index}'] = {'user': dictionary['userName'],
                                            'date': str(dictionary['datetime'])[0:10],
                                            'time': str(dictionary['datetime'])[11:19],
                                            'text': dictionary['text']}
        if len(messages) == 0:
            return 
        else:
            return messages


    @get('/chat/<chat_id>/sentiment')
    def getSentiment(chat_id):
        msgs = getMessages(chat_id)
        print(msgs)
        messagesSentiment = sentimentAnalyzer(msgs)
        return messagesSentiment

    @get('/user/<user_id>/recommend')
    def recommendUsers(user_id):
        data = list(coll.find({}))
        usersdata = list(users.aggregate([{'$project': {'idUser': 1}}]))
        listausers=[]
        for h in usersdata:
            listausers.append(int(h['idUser']))
        print (int(user_id))
        if int(user_id) not in listausers:
                return 'ERROR! Unknown User. You must <a href="/user/create">CREATE</a> the User first'
        tokenizer = RegexpTokenizer(r'\w+')
        stop_words = set(stopwords.words('english'))       
        TokensDict = {}
        for userId in listausers:
            usersData = list(coll.find({'idUser': userId}))
            usersTokens = [tokenizer.tokenize(e['text']) for e in usersData]
            usersTokens_clean = [word for message in usersTokens for word in message if word not in stop_words]
            TokensDict[f'{userId}'] = ' '.join(usersTokens_clean)
        count_vectorizer = CountVectorizer()
        sparse_matrix = count_vectorizer.fit_transform(TokensDict.values())
        Tokens_term_matrix = sparse_matrix.todense()
        df = pd.DataFrame(Tokens_term_matrix,columns=count_vectorizer.get_feature_names(),index=TokensDict.keys())
        similarity_matrix = distance(df, df)
        sim_df = pd.DataFrame(similarity_matrix, columns=TokensDict.keys(), index=TokensDict.keys())
        np.fill_diagonal(sim_df.values, 0)
        return {'recommended_users': [int(e) for e in list(sim_df[str(user_id)].sort_values(ascending=False)[0:3].index)]}
    
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('IP','0.0.0.0')
    run(host=host, port=port, debug=True)

    #run(host='localhost', port=8080)
if __name__=="__main__":
    main()