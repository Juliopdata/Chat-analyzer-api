from bottle import route, run, get, post, request
import datetime
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
db, msgs = connectCollection('api-project', 'messages')


@get("/")
def test():
    return ''' '''

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
    print(userslist)
    chatsids = list(chatsCR.aggregate([{'$project':{'idChat':1}}]))
    usersdata = list(users.aggregate([{'$project': {'idUser': 1}}]))
    chatID = max([e['idChat'] for e in chatsids])+1
    listausers = []
    for h in usersdata:
        listausers.append(int(h['idUser']))
    for e in userslist:
        if int(e) not in listausers:
            return 'ERROR! Unknown Users. You must <a href="http://localhost:8080/user/create">CREATE</a> the User first'
        else:
            newchat = {'idChat': int(chatID),'users': userslist}
            message_id = chatsCR.insert_one(newchat).inserted_id
            return dumps(newchat)
            
@post('/chat/<chat_id>/adduser')
def addUserToChat(chat_id):
    db, coll = connectCollection('chats','chats')
    data = list(coll.find({'idChat': int(chat_id)}))
    # Checking if chat exists:
    if len(data) == 0:
        error = "Sorry, this chat doesn't exist. You must create it first."
        return {'Exception':error}
    user = int(request.forms.get('userId'))
    db2, coll2 = connectCollection('chats','users')
    usersData = list(coll2.aggregate([{'$project':{'idUser':1}}]))
    # Checking if user exists:
    if user not in [e['idUser'] for e in usersData]:
        error = 'Sorry, the user you are trying to include does not exist in the database. You must create it first.'
        return {'Exception':error}
    users = [int(e) for e in re.sub('\[|\]','',data[0]['users']).split(', ')]        
    # Checking if user is already part of the chat:
    if user in users:
        error = 'Sorry, this user is already part of the chat'
        return {'Exception':error}
    users.append(user)
    # Adding the new user to the chat:
    coll.update_one({'idChat': int(chat_id)}, {'$set':{'users':str(users)}})
    return {'UserId': user, 'ChatId': int(chat_id)}




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
    # Checking the chat
    chats = list(chatsCR.aggregate([{'$project': {'idChat': 1}}]))
    chats = [int(x.get('idChat')) for x in chats]
    if chatID not in chats:
        error = "Sorry, this chat doesn't exist. You must create it first."
        return {'Exception': error}
    # Check the user
    chato = list(chatsCR.find({'idChat': int(chatID)}))
    print(chato)
    chatusers = [int(e) for e in re.sub('\[|\]','',chato[0]['users']).split(', ')]
    if user not in chatusers:
        error = 'Sorry, this user is not part of the chat. You must add him/her first.'
        return {'Exception': error}
    # Adding the new message:
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

    for index,dictionary in enumerate(data):
        index += 1
        messages[f'message_{index}'] = {'user': dictionary['userName'],
                                        'date': str(dictionary['datetime'])[0:10],
                                        'time': str(dictionary['datetime'])[11:19],
                                        'text': dictionary['text']}
    if len(messages) == 0:
        error = 'Sorry, this chat does not exist in the database'
        return {'Exception':error}
    else:
        return messages

@get('/chat/<chat_id>/sentiment')
def getSentiment(chat_id):
    messages = getMessages(chat_id)
    if 'Exception' in messages:
        return messages
    else:
        messagesSentiment = sentimentAnalyzer(messages)
        return messagesSentiment


run(host='localhost', port=8080)
