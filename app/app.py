# Standart import
import os
import sys

# Third parties imports
from flask import Flask, request, render_template
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

# Local imports
from RetriveAnalysis import RetriveAnalysis
from .AzureTextAnalytics import AzureTextAnalyticsApi
from .models.Model import SqliteDatabase
from DTO import *

class App:
    def __init__(self):
        self.app : Flask = Flask(__name__)
        self.app.secret_key = os.getenv('SECRET_KEY')
        self.database = SqliteDatabase()

        try:
            self.text_analyzer : AzureTextAnalyticsApi = AzureTextAnalyticsApi()
            # TODO : Implement the test user credentials [fixme]
            # self.TextAnalizer.client.analyze_sentiment(['s'])

        except ResourceNotFoundError as err:
            print(f'Check your endpoint {err.message}')
            sys.exit()
        except ClientAuthenticationError as err:
            print(f'Check your Api Key {err.message}')
            sys.exit()

        self.register_routes()

    def register_routes(self):
        self.app.add_url_rule('/', 'index', methods=['GET', 'POST'], view_func=self.analyse_user_input)
        # self.App.add_url_rule('/<input_id>', 'get_tags', methods=['GET'], view_func=self.get_tags)

    def analyse_user_input(self):
        """
        The homepage of our application:
        Make sure, in the HTML the attributte name of the text input is 'document',
        The following checkboxes need to be in the form if you want to run it respectivily analyze:
            - sentiment to execute sentiment and sentences extraction
            - entities to extract the entities from the user input
            - linked_entities to extract the linked entities from the user input
            - key_phrases to extract the key phrases from the user input
            - all_actions to execute all the actions above
        
        This endpoint use the TextAnalizer class to get the information from the user input, so before running
        any analysis, the user input need to be passed to the TextAnalizer.document attributte. e.g. TextAnalizer.document = 'user_input_variable'

        Always the response will be an object with the following keys:
            - sentiment : SentencesResponseDTO
            - entities : EntitiesResponseDTO
            - linked_entities : LinkedEntitiesResponseDTO
            - key_phrases : TagsResponseDTO
            - language : LanguageResponseDTO

        Behavior:
            - All these keys will be None if the user doesn't check the respective checkbox.
            - All the keys will be filled with the information if the user check the 'all_actions' checkbox or if the user doesn't check any checkbox.
            - If more than 3 checkboxes are checked the system will execute all the actions.
            - If the user check only one checkbox, the system will execute only the action of the checkbox checked.
            - Only the all_actions performed will be saved in the database.

        Logging:
            - All call will be saved on log.txt file    
        """


        context : TextAnalyzedDTO = {}

        if request.method == 'POST':

            resquest_form : dict = request.form.to_dict()
            user_input = resquest_form.get('text')

            self.text_analyzer.document = user_input

            marked_checkboxes_on_form = resquest_form.keys()


            if 'all_actions' in marked_checkboxes_on_form or len(marked_checkboxes_on_form) > 3:

                # Verify if the user input exists in the database.
                # If found: Retrieve existing analysis from database
                # If not found: Perform new analysis and store in database
                # This caching mechanism helps avoid redundant API calls and improves performance
                # by reusing previously analyzed content.


                retrieved_analysis_data = RetriveAnalysis(user_input=user_input)

                

                if retrieved_analysis_data.input_id:
                    context['sentiment'] = retrieved_analysis_data.get_sentences()
                    context['entities'] = retrieved_analysis_data.get_entities_inputs()
                    # TODO: Implement the linked entities
                    context['linked_entities'] = retrieved_analysis_data.get_linked_entities()
                    context['key_phrases'] = retrieved_analysis_data.get_tags()
                    context['language'] = retrieved_analysis_data.get_language()

                    return context


                else:
                    analysis_result = self.text_analyzer.get_all_analysis()

                    context['sentiment'] = analysis_result.sentiment
                    context['entities'] = analysis_result.entities
                    context['linked_entities'] = analysis_result.linked_entities
                    context['key_phrases'] = analysis_result.key_phrases
                    context['language'] = analysis_result.language

                    # Save the analysis in the database
                    self.database.user_input = user_input
                    self.database.language = context['language']
                    self.database.sentiment = context['sentiment']
                    self.database.entities = context['entities']
                    self.database.linked_entities = context['linked_entities']
                    self.database.key_phrases = context['key_phrases']
                    
                    self.database.insert()

            else:
                # Individual analyzers
                if 'sentiment' in marked_checkboxes_on_form:
                    context['sentiment'] = self.text_analyzer.get_sentiment()

                if 'entities' in marked_checkboxes_on_form:
                    context['entities'] = self.text_analyzer.get_entities()

                if 'linked_entities' in marked_checkboxes_on_form:
                    context['linked_entities'] = self.text_analyzer.get_linked_entities()

                if 'key_phrases' in marked_checkboxes_on_form:
                    context['key_phrases'] = self.text_analyzer.get_tags()

            # TODO: Implement the logging system
            # TODO: Fix the language detection
            context['language'] = 'English'

        return render_template('index.html', **context)
    
app = App().app
