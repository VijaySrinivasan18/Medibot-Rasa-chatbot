# MediBot-A-RASA-chat-Bot

Chat Bot using RASA Framework for health care industry.This Bot can assist the users to book appointment, confirm the appointment status and users can enquire about usage and side effects of any medicine. 
Bot will web scrape that information and will provide it to the user. Appointment details would be stored in SQL server using pyodbc.  

This bot has 3 major functionalities.
It can be used to book appointment, confirm the exising appointment and to know about the uses, side effects and dosage  of an medicine/tablet.
Custom actions has been created to do web scrapping from third party websites when information about any medicine has been asked for.
When users ask to book appointment, RASA forms would be triggered to get the information about First name, Last name, appointment date from user and these information would be added to sql server table , appointment number would be generated and provided to user.
When user ask to confirm their appointment status, another Rasa form would be used to get the appointment number which would have been provided while booking appointment , connects to sql server to check status of that appointment using given appointment number.


Tools:  Python and sql 
Libraries:Bs4,lxml,requests,pyodbc,pandas,regex,nltkpickle,google search,rasa_sdk,Flask.