 @get("/")
    def index():
        return 'Welcome to the chat sentiment analysis API'


    @get('/chat/<chat_id>/list')
    def getMessages(chat_id):
        '''
        Get all messages from 'chat_id'
        input: chat_id
        output: json array with all messages from this chat_id
        '''
        db, coll = connectCollection('chats','messages_linked')
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
        '''
        Analyzes messages from chat_id. Uses 'NLTK' sentiment analysis package for this task.
        input: chat_id
        output: json with all sentiments from messages in the chat
        '''
        messages = getMessages(chat_id)
        if 'Exception' in messages:
            return messages
        else:
            messagesSentiment = sentimentAnalyzer(messages)
            plotSentiments(messagesSentiment)
            return messagesSentiment


    @get('/user/<user_id>/recommend')
    def recommendUsers(user_id):
        '''
        Recommends a friend to a user based on chat contents
        input: user_id
        output: json array with top 3 similar users
        '''
        db, coll = connectCollection('chats','messages_linked')
        data = list(coll.find({}))
        if int(user_id) not in list(set([e['idUser'] for e in data])):
            error = 'Sorry, this user does not exist in the database'
            return {'Exception':error}
        tokenizer = RegexpTokenizer(r'\w+')
        stop_words = set(stopwords.words('english'))       
        TokensDict = {}
        for userId in list(set([e['idUser'] for e in data])):
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
        # import seaborn as sns
        # sns.heatmap(sim_df,annot=True)
        return {'recommended_users': [int(e) for e in list(sim_df[str(user_id)].sort_values(ascending=False)[0:3].index)]}


            @get('/chat/create')
    def chatForm():
        return '''<form method="post" action="/chat/create">
                    Insert an array of user ids (e.g. [8, 10]): <input name="users" type="text" />
                    <input type="submit" />
                </form>'''


@post('/chat/create')
def createChat():
    '''
    Creates a conversation to load messages
    input: A dictionary containing an array of user ids: e.g. {'users': '[8, 9, 10]'}
    output: chat_id
    '''
    users = str(request.forms.get('users'))
    print(users)
    db, coll = connectCollection('chats','chats')
    data = list(coll.aggregate([{'$project':{'idChat':1}}]))
    newChat = {'idChat':max([e['idChat'] for e in data])+1, 'users': users}
    print(newChat)
        # Checking if users exist in the database
    db2, coll2 = connectCollection('chats','users')
    usersData = list(coll2.aggregate([{'$project':{'idUser':1}}]))
    chatUsers = [int(e) for e in re.sub('\[|\]','',newChat['users']).split(', ')]
    for e in chatUsers:
        if e not in [f['idUser'] for f in usersData]:
            error = 'Sorry, one or more of the users you are trying to include do not exist in the database. You must create them first.'
            return {'Exception':error}
    # Inserting new chat to the database:
    chat_id = coll.insert_one(newChat).inserted_id
    return {'ObjectId': str(chat_id), 'ChatId': newChat['idChat']}