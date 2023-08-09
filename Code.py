from simplegmail import Gmail
from simplegmail.query import construct_query
import os.path
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Replace with the path to your credentials JSON file
credentials_path = r'C:\Users\musin\IdeaProjects\\SpreadSheets\model-fastness-394513-95470a5ec8a5.json'

# Authenticate with Google Sheets API using credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
gc = gspread.authorize(credentials)

# Replace with your Google Sheets spreadsheet key (can be found in the URL)
spreadsheet_key = '14CFtQ1TRB7jYrkQUCGMf1hDHTB_1qVwHvu6hvmBtW5Y'

# Replace with the name of the worksheet where you want to add the row
worksheet_name = 'transactions'
worksheet_name2 = 'scheduler-history'

# Replace with the data you want to add in the new row

row_number_to_insert = 1

# Open the worksheet and append the new row
worksheet = gc.open_by_key(spreadsheet_key).worksheet(worksheet_name)
worksheet2 = gc.open_by_key(spreadsheet_key).worksheet(worksheet_name2)



gmail = Gmail()

query_params = {
    "newer_than": (12, "hours"),
}

#messages = gmail.get_starred_messages()
emails = []
messages = gmail.get_messages(query=construct_query(query_params))
x = 0
for message in messages:

    odeslana = message.subject
    if "zůstatku na účtu Běžný účet 1" in str(odeslana): 
        email = [message.sender,message.date,message.subject,message.plain]
        emails.append(email)
        while x != 1:
            new_data = [message.date]
            worksheet2.append_row(new_data,2)
            x = 1

for email in emails:
    if "Zvýšení" in email[2]:
        name_of_member = ""
        date = email[1]
        list_of_enters = email[3].split("\n")
        for enter in list_of_enters:
            if "Dostupný zůstatek k" in str(enter):
                list_of_words = enter.split(" ")
                zůstatek = str(list_of_words[len(list_of_words) - 3]) + " " + str(list_of_words[len(list_of_words) - 2])
                if "je" in zůstatek:
                    zůstatek = str(list_of_words[len(list_of_words) - 2])
            if "Příchozí úhrada z účtu" in str(enter):
                list_of_words = enter.split(" ")
                for index,word in enumerate(list_of_words):
                    if word == "číslo":
                        numbers = [i for i in range(4,index)]
                        words = [list_of_words[int(c)] for c in numbers]
                        name_of_member = " ".join(words)
                    if "/" in word:
                        account_number = word.replace("\r","")
            if "Částka:" in str(enter):
                amount = enter
                erasers = ["Částka:","CZK"," ",">","\r"]
                for eraser in erasers:
                    amount = amount.replace(eraser,"")
            if "Dostupný zůstatek k" in enter:
                list_of_words = enter.split(" ")
                zůstatek = str(list_of_words[len(list_of_words) - 3]) + str(list_of_words[len(list_of_words) - 2])
                if "je" in zůstatek:   
                    zůstatek = int(list_of_words[len(list_of_words) - 2])
            if "Kód transakce:" in str(enter):
                list_of_words1 = enter.split(" ")
                transaction_code = list_of_words1[2].replace("\r","")
            if "Zpráva pro příjemce:" in str(enter):
                note = enter.replace("Zpráva pro příjemce: ","") 
                note = note.replace("\r","")    
        infos = "Příchozí" 
        new_row_data = [date,transaction_code,account_number,name_of_member,amount,note,"Příchozí",zůstatek]
        worksheet.insert_rows(new_row_data,row_number_to_insert)


        

    if "Snížení" in email[2]:
        amount_ = ""
        date = email[1]
        list_of_enters = email[3].split("\n")
        for enter in list_of_enters:
            if "Dobrý den, zůstatek na účtu" in enter:
                list_of_sentences = enter.split(".")
                for sentence in list_of_sentences:
                    if "snížil o částku" in sentence:
                        list_of_words = sentence.split(" ")
                        for index,word in enumerate(list_of_words):
                            if word == "částku":
                                first = index
                            if word == "CZK":
                                second = index
                                for i in range(first + 1, second):
                                    amount_ += list_of_words[i]
                                    amount = "-" + amount_
                    if " v " in sentence:
                        list_of_words = sentence.split(" ")
                        zůstatek = str(list_of_words[len(list_of_words) - 3]) + str(list_of_words[len(list_of_words) - 2])
                        if "je" in zůstatek:   
                            zůstatek = int(list_of_words[len(list_of_words) - 2])
                    if "na účet číslo" in sentence:
                        list_of_words = sentence.split(" ")
                        for index,word in enumerate(list_of_words):
                            if "/" in word:
                                recieving_acc_num = word
                    if "transakce" in sentence:
                        list_of_words = sentence.split(" ")
                        for index,word in enumerate(list_of_words):
                            if word == "transakce:":
                                transaction_code = list_of_words[index + 1]
        infos = "Odchozí"
        new_row_data = [date,transaction_code,recieving_acc_num,"SK Slavia Praha",amount,"","Odchozí",zůstatek]
        worksheet.insert_rows(new_row_data,row_number_to_insert)
