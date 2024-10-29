import os
import sys
from flask import Flask, request, render_template
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from RetriveAnalysis import RetriveAnalysis
from .AzureTextAnalytics import AzureTextAnalyticsApi
from .models.Model import SqliteDatabase

class TextApp:
    def __init__(self):
        self.App : Flask = Flask(__name__)
        self.App.secret_key = os.getenv('SECRET_KEY')
        self.database = SqliteDatabase()

        try:
            self.TextAnalizer : AzureTextAnalyticsApi = AzureTextAnalyticsApi()
            # self.TextAnalizer.client.analyze_sentiment(['s'])

        except ResourceNotFoundError as err:
             print(f'Check your endpoint {err.message}')
             sys.exit()
        except ClientAuthenticationError as err:
             print(f'Check your Api Key {err.message}')
             sys.exit()

        self.register_routes()

    def register_routes(self):
         self.App.add_url_rule('/', 'index', methods=['GET', 'POST'], view_func=self.analyze)
         # self.App.add_url_rule('/<input_id>', 'get_tags', methods=['GET'], view_func=self.get_tags)

    def analyze(self):
        context = {}

        if request.method == 'POST':
            payload : dict = request.form.to_dict()
            user_input = payload.get('text')

            self.TextAnalizer.document = user_input

            actions_to_execute = payload.keys()


            if 'all_actions' in actions_to_execute or len(actions_to_execute) > 3:

                retrived_analyze = RetriveAnalysis(user_input=user_input)


                if retrived_analyze.input_id:
                    context['sentiment'] = retrived_analyze.get_sentences()

                    context['entities'] = retrived_analyze.get_entities_inputs()
                    context['linked_entities'] = retrived_analyze.get_linked_entities()
                    context['key_phrases'] = retrived_analyze.get_tags()
                    context['language'] = retrived_analyze.get_language()

                else:
                    
                    completed_analyze = self.TextAnalizer.GetAllInformation()

                    context['sentiment'] = completed_analyze.sentiment
                    context['entities'] = completed_analyze.entities
                    context['linked_entities'] = completed_analyze.linked_entities
                    context['key_phrases'] = completed_analyze.key_phrases
                    context['language'] = completed_analyze.language
                
                self.database.Insert(user_input, 'English', context['sentiment'], context['entities'], context['linked_entities'], context['key_phrases'] )
            else:
                # Individual analyzers
                if 'sentiment' in actions_to_execute:
                    context['sentiment'] = self.TextAnalizer.GetSentiment()
                if 'entities' in actions_to_execute:
                    context['entities'] = self.TextAnalizer.GetEntities()
                if 'linked_entities' in actions_to_execute:
                    context['linked_entities'] = self.TextAnalizer.GetLinkedEntities()
                if 'key_phrases' in actions_to_execute:
                    context['key_phrases'] = self.TextAnalizer.GetKeyPhrases()
            context['language'] = self.TextAnalizer.GetLanguage()
        else:
            pass

        return render_template('index.html', **context)
    

app = TextApp().App