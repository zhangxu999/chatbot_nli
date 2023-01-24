# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
#
#



class ActionAskName(Action):

    def __init__(self):
        pass

    def name(self) -> Text:
        return "action_ask_name"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict]:
        entities = tracker.latest_message['entities']
        for entity in entities:
            if entity['entity'] == 'name':
                value = entity['value']
                break

        dispatcher.utter_message(text=f" the staff you are looking for is {value}, his is a member of ... office at ....")
        return []

