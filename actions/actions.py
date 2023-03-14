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


import pandas as pd
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

entity_df = pd.read_excel("../project/listado.xlsx")
entity_df = entity_df[pd.notnull(entity_df['name'])]
entity_df['name'] = entity_df['name'].str.lower()
def split_name(full_name):
    names = full_name.replace(',',' ').split()
    names = [n.strip() for n in names]
    names = [n.strip('') for n in names if n not in ['',',']]
    return names
entity_df['full_name'] = entity_df['name'].apply(split_name)


names = [name.lower() for name in entity_df['name'].unique().tolist()]
groups = [g.lower() for g in entity_df['group'].unique().tolist()]
entities =  names + groups

#Sentences are encoded by calling model.encode()
embeddings = model.encode(entities)


def get_row_by_item(col, value):
    for i,row in  entity_df.iterrows():
        if value == row[col]:
            name,group,office = row['name'],row['group'],row['office']
            return name,group,office
    return None,None,None
    



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
                value = entity['value'].lower()
                break
        name = None
        for i,row in  entity_df.iterrows():
            for n in row['full_name']:
                if value == n:
                    name,group,office = row['name'],row['group'],row['office']
                    break
        if name:
            response = f" the staff you are looking for is {name}, \
            a member of {group}, the office number is {office}"
        else:
            response = f'I do not find {value} in the lab.'
        dispatcher.utter_message(text=response)
        return []



class ActionAskGroup(Action):

    def __init__(self):
        pass

    def name(self) -> Text:
        return "action_ask_group"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict]:
        entities = tracker.latest_message['entities']
        for entity in entities:
            if entity['entity'] == 'group':
                value = entity['value']
                break

                search_words = [value]
        search_embedding = model.encode(search_words)
        # 计算向量之间的余弦相似度
        similarity = cosine_similarity(search_embedding, embeddings)
        print(similarity.shape)
        ranked_entities = sorted(list(zip(similarity.reshape(-1),entities)),reverse=True)
        score, answer = ranked_entities[0]


        staff_number = entity_df[entity_df.group==answer].shape[0]

        some_staffs = ''.join([n.lower() for n in entity_df[entity_df.group\
        =='WSSC: Web Science and Social Computing'].iloc[:3]['name'].values.tolist()])


        response = f" the group {answer} have {staff_number} members, some members of this group are {some_staffs}"
        dispatcher.utter_message(text=response)

        return []


class ActionAskOffice(Action):

    def __init__(self):
        pass

    def name(self) -> Text:
        return "action_ask_office"


    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict]:
        entities = tracker.latest_message['entities']
        for entity in entities:
            if entity['entity'] == 'office':
                value = entity['value']
                break
        
        name,group,office = get_row_by_item('office',value)

        response = f" the office {office} is belong to {name},  he is a member of {group}"

        dispatcher.utter_message(text=template)

        return []
