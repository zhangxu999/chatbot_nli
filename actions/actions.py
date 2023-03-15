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
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
from transformers import AutoTokenizer, BlenderbotSmallForConditionalGeneration
from Levenshtein import distance
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

entity_df = pd.read_excel("../project/listado.xlsx")
entity_df = entity_df[pd.notnull(entity_df['name'])]
entity_df['name'] = entity_df['name'].apply(lambda x:x.lower().strip())
def split_name(full_name):
    full_names = full_name.replace(',',' ').replace('   ',' ').replace('  ',' ').strip()
    names = full_name.split()
    names = [n.strip() for n in names]
    names = [n.strip('') for n in names if n not in ['',',']]
    return names + [full_names]
entity_df['full_name'] = entity_df['name'].apply(split_name)

def group_pre(group):
    return group.replace("\n",' ').lower().strip()
    
entity_df['group'] =entity_df['group'].apply(group_pre)
entity_df['office'] =entity_df['office'].apply(lambda x:str(x))


full_names = set([s for l in entity_df['full_name'].tolist()  for s in l])
groups = [g.lower() for g in entity_df['group'].unique().tolist()]
embed_entities =  groups

#Sentences are encoded by calling model.encode()
embeddings = model.encode(embed_entities)


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
        value = None
        entities = tracker.latest_message['entities']
        for entity in entities:
            if entity['entity'] == 'name':
                value = entity['value'].lower()
                if value in full_names:
                    break
        if value is None:
            response = f"I do not find any people's name  in the question, sorry."
            dispatcher.utter_message(text=response)
            return []

        name,match = None,True
        for i,row in  entity_df.iterrows():
            for n in row['full_name']:
                if value == n:
                    name,group,office = row['name'],row['group'],row['office']
                    break
        if name is None:
            match = False
            answers = sorted([(name,distance(value,name)) for name in full_names],key=lambda x:x[1])
            print(value, answers[:10])
            value,d = answers[0]
            for i,row in  entity_df.iterrows():
                for n in row['full_name']:
                    if value == n:
                        name,group,office = row['name'],row['group'],row['office']
                        break

        response = f"{' ' if match else 'Maybe'} the staff you are looking for is {name}, a member of {group}, the office number is {office}."            
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
        print("-------------in group")
        entities = tracker.latest_message['entities']
        value = None
        for entity in entities:
            if entity['entity'] == 'group':
                value = entity['value']
                break
        if value is None:
            response = f" I am sorry I don't know  which group you are looking for"
            dispatcher.utter_message(text=response)

            return []



        search_embedding = model.encode([value])
        # 计算向量之间的余弦相似度
        similarity = cosine_similarity(search_embedding, embeddings)
        print(similarity.shape)
        ranked_entities = sorted(list(zip(similarity.reshape(-1),embed_entities)),reverse=True)
        print(ranked_entities)
        score, answer = ranked_entities[0]


        staff_number = entity_df[entity_df.group==answer].shape[0]

        some_staffs = ', '.join([n.lower() for n in entity_df[entity_df.group\
        ==answer].iloc[:10]['name'].values.tolist()])


        response = f" the group {answer} have {staff_number} members, some members of this group are {some_staffs}"
        dispatcher.utter_message(text=response)

        return []


class ActionAskOffice(Action):

    def __init__(self):
        pass


    def name(self) -> Text:
        return "action_ask_room"


    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict]:
        entities = tracker.latest_message['entities']
        value = None
        for entity in entities:
            if entity['entity'] == 'room':
                value = entity['value']
                break
        
        name,group,office = get_row_by_item('office',value)
        if name:
            response = f" the office {office} is belong to {name},  he is a member of {group}"
        else:
            response = f" there is no office name {office}"

        dispatcher.utter_message(text=response)

        return []


class ActionChitchat(Action):

    def __init__(self):
        mname = "facebook/blenderbot_small-90M"
        self.model = BlenderbotSmallForConditionalGeneration.from_pretrained(mname)
        self.tokenizer = AutoTokenizer.from_pretrained(mname)


    def name(self) -> Text:
        return "action_chitchat"


    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict]:
        UTTERANCE = tracker.latest_message['text']
        inputs = self.tokenizer([UTTERANCE], return_tensors="pt")
        reply_ids = self.model.generate(**inputs,do_sample=True)
        response = self.tokenizer.batch_decode(reply_ids, skip_special_tokens=True,)[0]
        dispatcher.utter_message(text=response)

        return []
