# <p align="center"> Api Sentiment Chat Analyzer </p>


  <p align="center"> <img  src="https://github.com/Juliopdata/chat-analyzer-api/blob/master/images/chatcaptura.png"></p>

  ----
## Description

The goal of this project is create an Api to analyze chat messages and create sentiment metrics of the different people using an API (bottle),NLTK sentiment analysis, Docker, Heroku, Cloud databases and recommender systems.

## Steps

- Write an API in bottle just to store chat messages in a database like mongodb.
- Extract sentiment from chat messages and perform a report over a whole conversation.
- Deploy the service with docker to heroku and store messages in a cloud database.
- Recommend friends to a user based on the contents from chat `documents` using a recommender system with `NLP` analysis.

## Project Structure

The project folder is structured in the following way:

* __api.py__ : that contains the code of my data pipeline.

* __INPUT__ : Folder where the chats should be placed in json format.

* __OUTPUT__ : Folder that contains the new jsons from the output of my data pipeline.

* __SRC__: Functions and resources.

* __IMAGES__: Images to illustrate.

* __VIEWS__: html templates.


## Link to the Html Beta Api in Heroku

## https://ironapichat.herokuapp.com/ 

## Resources

### API dev in python
- [https://bottlepy.org/docs/dev/]
- [https://www.getpostman.com/]
​
### NLP & Text Sentiment Analysis
- [https://www.nltk.org/]
- [https://towardsdatascience.com/basic-binary-sentiment-analysis-using-nltk-c94ba17ae386]
- [https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk]
​
### Heroku & Docker & Cloud Databases
- [https://docs.docker.com/engine/reference/builder/]
- [https://runnable.com/docker/python/dockerize-your-python-application]
- [https://devcenter.heroku.com/articles/container-registry-and-runtime]
- [https://devcenter.heroku.com/categories/deploying-with-docker]
- Mongodb Atlas [https://www.mongodb.com/cloud/atlas]
- MySQL ClearDB [https://devcenter.heroku.com/articles/cleardb]