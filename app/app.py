import os
from typing import TypedDict
from flask import Flask, request, render_template, flash, jsonify
from .AzureTextAnalytics import *
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
import os
import sys
from .models.Model import SqliteDatabase, cur, conn


# import fileStorage
from werkzeug.datastructures import FileStorage

class ResponseAzure(TypedDict):
        sentiment : list[AnalyzeSentimentResult | DocumentError]
        entities : list[RecognizeEntitiesResult | DocumentError]
        linked_entities : list[RecognizeLinkedEntitiesResult | DocumentError]
        key_phrases : list[int | DocumentError]
        language : list[DetectLanguageResult | DocumentError]

class TextApp:
    def __init__(self):
        self.App : Flask = Flask(__name__)
        self.App.secret_key = os.getenv('SECRET_KEY')
        self.database = SqliteDatabase()

        try:
            self.TextAnalizer : AzureTextAnalyticsApi = AzureTextAnalyticsApi()
            # self.TextAnalizer.client.analyze_sentiment(['s'])

        except ResourceNotFoundError as err:
             print(f'Check your endpoint', err.message)
             sys.exit()
        except ClientAuthenticationError as err:
             print(f'Check your Api Key', err.message)
             sys.exit()

        self.register_routes()

    def register_routes(self):
         self.App.add_url_rule('/', 'index', methods=['GET', 'POST'], view_func=self.analyze)
         # self.App.add_url_rule('/<input_id>', 'get_tags', methods=['GET'], view_func=self.get_tags)

    def analyze(self):
        Context: ResponseAzure  = dict()

        if request.method == 'POST':
            
                Data : dict = request.form.to_dict()

                Document = Data.get('text')
                Actions = Data.keys()

                self.TextAnalizer.document = Document

                if 'all_actions' in Actions:
                    All = self.TextAnalizer.GetAllInformation()
                    Context['sentiment'] = All.sentiment
                    Context['entities'] = All.entities
                    Context['linked_entities'] = All.linked_entities
                    Context['key_phrases'] = All.key_phrases
                    Context['language'] = All.language
                    
                    self.database.Insert(Document, Context['sentiment'], Context['entities'], 
                                        Context['linked_entities'], Context['key_phrases'])
                else:
                    # Individual analyzers
                    if 'sentiment' in Actions:
                        Context['sentiment'] = self.TextAnalizer.GetSentiment()
                    if 'entities' in Actions:
                        Context['entities'] = self.TextAnalizer.GetEntities()
                    if 'linked_entities' in Actions:
                        Context['linked_entities'] = self.TextAnalizer.GetLinkedEntities()
                    if 'key_phrases' in Actions:
                        Context['key_phrases'] = self.TextAnalizer.GetKeyPhrases()
                Context['language'] = self.TextAnalizer.GetLanguage()   


        else:
            pass
        return render_template('index.html', **Context)
    

app = TextApp().App