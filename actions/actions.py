# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# from audioop import reverse
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker,FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from nltk.corpus import stopwords
import requests
from googlesearch import search
import bs4
import lxml
import pickle    
import pandas as pd 
import numpy as np
import pyodbc
from rasa_sdk.types import DomainDict
from  datetime import date
import regex
import os

def update_appointment_details(first_name,last_name,appointment_date):
    ''' 
    This method updates the given details to sql server using pyodbc connector
    
    '''
    try:
        db_obj=pyodbc.connect('Driver={SQL Server};'
                    'Server=VIJAY-SRINIVASA\SQLEXPRESS;'
                    'Database=medibot_database;'
                    'Trusted_Connection=yes;')
        db_cursor=db_obj.cursor()
        sql_result=db_cursor.execute("select  appointment_no from medibot_database.dbo.appointment_table order by appointment_no Desc").fetchall()
        
        if len(sql_result)!=0:   
            cc=[int(x[0][4:]) for x in sql_result]
            cc.sort(reverse=True)
            print("cc",cc)
            last_apointment_no=cc[0]

            current_appointment_no="med-"+str(last_apointment_no+1)
            sql = "insert into medibot_database.dbo.appointment_table(appointment_no,first_name,last_name,appointment_date,appointment_status) values (?,?,?,?,?)"
            val = (current_appointment_no,first_name,last_name,appointment_date,"confirmed")
            db_cursor.execute(sql, val)
            db_obj.commit()
            db_obj.close()
            return current_appointment_no
        else:
            current_appointment_no="med-1"
            sql = "insert into medibot_database.dbo.appointment_table(appointment_no,first_name,last_name,appointment_date,appointment_status) values (?,?,?,?,?)"
            val = (current_appointment_no,first_name,last_name,appointment_date,"confirmed")
            db_cursor.execute(sql, val)
            db_obj.commit()
            db_obj.close()
            return current_appointment_no
    except Exception as e:
        print("The following error occured")
        print(e)
        return False

def get_appointment_status(appointment_no):
    appointment_no=appointment_no.strip()
    try:
        db_obj=pyodbc.connect('Driver={SQL Server};'
                    'Server=VIJAY-SRINIVASA\SQLEXPRESS;'
                    'Database=medibot_database;'
                    'Trusted_Connection=yes;')
        db_cursor=db_obj.cursor()
        result=db_cursor.execute("select * from medibot_database.dbo.appointment_table where appointment_no = ?",appointment_no).fetchall()
    except Exception as e:
        print("The following error occured in get_appointment_status method")
        print(e)
        return "We are facing issues currently.Please try after sometime."
    if len(result)!=0:
        return f"Appointment for {result[0][1]} {result[0][2]} is in {result[0][4]} status on {result[0][3]}"
    else:
        return "We do not have any records with the given appointment number."

def remove_stopwords(list_words):
    return [x for x in list_words if x not in stopwords.words("english")]

def get_medicine_info(sentence=None,entity_word=None):
    s= open("artifacts/medicine_database.pickle","ab+")
    s.seek(0)
    try:
        medi_data=pickle.load(s)
        print("medi data loaded")
    except EOFError:
        print("Pickle file empty and empty df loaded for medi data")
        medi_data=pd.DataFrame([np.zeros(shape=4)],columns=["Name","Composition","About","Possible_side_effects"])
    df=pd.DataFrame([np.zeros(shape=4)],columns=["Name","Composition","About","Possible_side_effects"])




    links={}
    medicine_name=[]
    if sentence is not None:    
        for medicine in remove_stopwords(sentence.split(" ")):
            for link in [x for x in search(medicine,num=10,stop=10)]:
                # print("Links:",link)
                for key_word in ["www.apollopharmacy.in","www.netmeds.com"]:
                    if key_word in link:
                        links[key_word]=link
                        medicine_name.append(medicine.lower())

    if entity_word is not None:
        for link in [x for x in search(entity_word,num=10,stop=10)]:
            for key_word in ["www.apollopharmacy.in","www.netmeds.com"]:
                if key_word in link:
                    links[key_word]=link
                    medicine_name.append(entity_word.lower())


    if len(links.keys())==0:
        print("Nothing found: ",links)
        return "We are very sorry, We are not able to fetch the required medicine information now."

    if medicine_name[0] in np.array(medi_data["Name"]):
        print("Info already present in our medi data, fetching from it and not doing webscrapping")
        df=medi_data.loc[medi_data["Name"]==medicine_name[0]]
        output="Composition:"+df["Composition"][0]+" About:"+df["About"][0]+" Possible side effects are "+df["Possible_side_effects"][0]
        s.close()
        return output



    if "www.apollopharmacy.in" in list(links.keys()): 
        # print("Found apollo link")
        response=requests.get(links["www.apollopharmacy.in"])
        bs4_obj=bs4.BeautifulSoup(response.content,"lxml")
        Composition=bs4_obj.select(" a>p ")[6].text
        about=bs4_obj.select(".text-align-justify")[0].text
        possible_side_effects=",".join( [i.text for i in bs4_obj.select(".ProductDetailsGeneric_txtListing__1g4QG > ul >li")])
        output="Composition:"+Composition+" About:"+about+" Possible side effects are "+possible_side_effects
        df["Name"]=medicine_name[0]
        df["Composition"]=Composition
        df["About"]=about
        df["Possible_side_effects"]=possible_side_effects
        medi_data=pd.concat((medi_data,df),axis=0)
        pickle.dump(medi_data,s) 
        s.close()
        print("dumped to medi data from apollo")
        return output
    if "www.netmeds.com" in list(links.keys()):
        print("found Netmeds link")
        response=requests.get(links["www.netmeds.com"])
        bs4_obj=bs4.BeautifulSoup(response.content,"lxml")
        overall=bs4_obj.find_all("div",class_="inner-content")
        possible_side_effects=overall[3].p.text
        about=overall[0].p.text
        Composition=overall[1].ul.text.strip().replace(" ",",")
        output="Composition:"+Composition+" About:"+about+" Possible side effects :"+possible_side_effects
        df["Name"]=medicine_name[0]
        df["Composition"]=Composition
        df["About"]=about
        df["Possible_side_effects"]=possible_side_effects
        medi_data=pd.concat((medi_data,df),axis=0)
        pickle.dump(medi_data,s) 
        s.close()
        print("dumped to medi data from Netmeds")
        return output
    

class ActionMedicineEnquiry(Action):

    def name(self) -> Text:
        return "action_medicine_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("raw message",tracker.latest_message)
        my_text=tracker.latest_message["text"]
        entity_text=tracker.latest_message["entities"]
        print("Entity received", entity_text)

        if len(entity_text)!=0:
            print("Received entity:",entity_text[0]["value"])
            output=get_medicine_info(entity_word=entity_text[0]["value"])
        else:
            print("No entity received, using text")
            output=get_medicine_info(my_text)

        dispatcher.utter_message(output)

        return []

class ActionAppointmentBooking(Action):

    def name(self) -> Text:
        return "action_appointment_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        first_name=tracker.get_slot("first_name") 
        last_name=tracker.get_slot("last_name")
        appointment_date=tracker.get_slot("appointment_date")
        appoint_no=update_appointment_details(first_name,last_name,appointment_date)
        if appoint_no==False:
            output="We are sorry, we are currently experiencing issue. Please try later"
            
        else:
            output=f"Appointment booked for {first_name} {last_name} on {appointment_date}, your appointment number is {appoint_no}"
        
        dispatcher.utter_message(output)

        return []        

class ActionAppointmentConfirmation(Action):

    def name(self) -> Text:
        return "action_appointment_confirmation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        if len(tracker.latest_message["entities"])!=0:
            required_appointment_no=tracker.latest_message["entities"][0]["value"]
            print("Received entity:",required_appointment_no)
            output=get_appointment_status(required_appointment_no)
            dispatcher.utter_message(output)

        else:
            dispatcher.utter_message("No Appointment number found in your message,Could you please provide the Appointment number starting wit med- ")

        return []


### validation classes
def clean_name(name):
    return "".join([c for c in name if c.isalpha()])

class ValidateAppointmentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_appointment_form"

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"first_name": None}
        return {"first_name": name}

    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"last_name": None}
        
        first_name = tracker.get_slot("first_name")
        if len(first_name) + len(name) < 3:
            dispatcher.utter_message(text="That's a very short name. We fear a typo. Restarting!")
            return {"first_name": None, "last_name": None}
        return {"last_name": name}

    def validate_appointment_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        date_val = slot_value.replace(" ","")
        ss=regex.search("\d{4}/\d{2}/\d{2}",date_val)
        print(ss)
        if ss:
            y=int(ss.string.split("/")[0])
            m=int(ss.string.split("/")[1])
            d=int(ss.string.split("/")[2])
            try:

                if date(y,m,d)>=date.today():
                    return {"appointment_date": date_val}
                else:
                    dispatcher.utter_message(text="Please enter future date.It seems past date has been entered")
                    return {"appointment_date": None}
            except Exception as e:
                if str(e) =="day is out of range for month":
                    dispatcher.utter_message(text="Given date is out of range for the given month")
                    return {"appointment_date": None}
                elif str(e)=="month must be in 1..12":
                    dispatcher.utter_message(text="Month cannot have value more than 12")
                    return {"appointment_date": None}

        else:
            dispatcher.utter_message(text="Please enter date in proper format")
            return {"appointment_date": None}


# ______________________________________________________________________________


class ValidateAppointmentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_appointment_confirmation_form"

    def validate_required_appointment_no(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `appointment_no for confirming the appointment status` """

        if regex.search("^med-[^ a-z][0-9]*",slot_value)== None:
            dispatcher.utter_message(text="Seems the entered appointment number is in incorrect format ")
            return {"required_appointment_no": None}

        return {"required_appointment_no": slot_value}


