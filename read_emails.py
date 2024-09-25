import imaplib
import email
import os
from email.header import decode_header
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def is_email_not_older_than_2_days(email_date_str):
    # Parse the email date string into a datetime object
    email_date = datetime.strptime(email_date_str, "%Y-%m-%d %H:%M:%S")

    # Calculate the difference between the current time and the email date
    time_difference = datetime.now() - email_date

    # Check if the difference is less than 2 days
    return time_difference.days < 2


# Replace with the path to your credentials JSON file
credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
# Authenticate with Google Sheets API using credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
gc = gspread.authorize(credentials)

# Replace with your Google Sheets spreadsheet key (can be found in the URL)
spreadsheet_key = os.getenv("spreadsheet")

# Replace with the name of the worksheet where you want to add the row
worksheet_name = 'transactions'

# Replace with the data you want to add in the new row

row_number_to_insert = 2

# Open the worksheet and append the new row
worksheet_transactions = gc.open_by_key(spreadsheet_key).worksheet(worksheet_name)

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

imap_server = "imap.gmail.com"
imap_email = os.getenv("email")
password = os.getenv("password")

imap = imaplib.IMAP4_SSL(imap_server)

imap.login(imap_email, password)

imap.select("Inbox")

_, messuges = imap.search(None, "ALL")

list_messages = messuges[0].split()

transaction_code = ""
account_number = ""
amount = ""
note = ""
zustatek = ""
first = ""
recieving_acc_num = ""


for i in range(len(list_messages) - 1, -1, -1):
    _, data = imap.fetch(list_messages[i], "(RFC822)")

    message = email.message_from_bytes(data[0][1])
    subject = message.get("Subject")
    date = message.get("Date")
    tf = date.split()
    day, month, year, time_clock = tf[1], tf[2], tf[3], tf[4]
    try:
        decoded_subject, encoding = decode_header(subject)[0]
        string_subject = decoded_subject.decode("utf-8")
    except:
        continue
    index = months.index(month) + 1
    email_date = f"{year}-{index}-{day} {time_clock}"
    current_time = time.localtime()
    result = is_email_not_older_than_2_days(email_date)
    if result:

        if "zůstatku na účtu" in string_subject:
            content = ""
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset() or 'utf-8'
                    decoded_text = part.get_payload(decode=True).decode(charset)
                    content += decoded_text

            print(content)

            if "Zvýšení" in string_subject and "zůstatku na účtu" in string_subject:
                name_of_member = ""
                date = str(date)
                list_of_enters = content.split("\n")
                for enter in list_of_enters:
                    if "Dostupný zustatek k" in str(enter):
                        list_of_words = enter.split(" ")
                        zustatek = str(list_of_words[len(list_of_words) - 3]) + " " + str(
                            list_of_words[len(list_of_words) - 2])
                        if "je" in zustatek:
                            zustatek = str(list_of_words[len(list_of_words) - 2])
                    if "Příchozí úhrada z účtu" in str(enter):
                        list_of_words = enter.split(" ")
                        for index, word in enumerate(list_of_words):
                            if word == "číslo":
                                numbers = [i for i in range(4, index)]
                                words = [list_of_words[int(c)] for c in numbers]
                                name_of_member = " ".join(words)
                            if "/" in word:
                                account_number = word.replace("\r", "")
                    if "Částka:" in str(enter):
                        amount = enter
                        erasers = ["Částka:", "CZK", " ", ">", "\r"]
                        for eraser in erasers:
                            amount = amount.replace(eraser, "")
                    if "Dostupný zustatek k" in enter:
                        list_of_words = enter.split(" ")
                        zustatek = str(list_of_words[len(list_of_words) - 3]) + str(list_of_words[len(list_of_words) - 2])
                        if "je" in zustatek:
                            zustatek = int(list_of_words[len(list_of_words) - 2])
                    if "Kód transakce:" in str(enter):
                        list_of_words1 = enter.split(" ")
                        transaction_code = list_of_words1[2].replace("\r", "")
                    if "Zpráva pro příjemce:" in str(enter):
                        note = enter.replace("Zpráva pro příjemce: ", "")
                        note = note.replace("\r", "")
                infos = "Příchozí"
                new_row_data_text = ["hello", "why", "not", "working"]
                new_row_data = [date, transaction_code, account_number, name_of_member, amount, note, "Příchozí", zustatek]
                worksheet_transactions.insert_row(new_row_data, row_number_to_insert)

            if "Snížení" in string_subject and "zůstatku na účtu" in string_subject:
                amount_ = ""
                date = date
                list_of_enters = content.split("\n")
                for enter in list_of_enters:
                    if "Dobrý den, zustatek na účtu" in enter:
                        list_of_sentences = enter.split(".")
                        for sentence in list_of_sentences:
                            if "snížil o částku" in sentence:
                                list_of_words = sentence.split(" ")
                                for index, word in enumerate(list_of_words):
                                    if word == "částku":
                                        first = index
                                    if word == "CZK":
                                        second = index
                                        for c in range(first + 1, second):
                                            amount_ += list_of_words[c]
                                            amount = "-" + amount_
                            if " v " in sentence:
                                list_of_words = sentence.split(" ")
                                zustatek = str(list_of_words[len(list_of_words) - 3]) + str(
                                    list_of_words[len(list_of_words) - 2])
                                if "je" in zustatek:
                                    zustatek = int(list_of_words[len(list_of_words) - 2])
                            if "na účet číslo" in sentence:
                                list_of_words = sentence.split(" ")
                                for index, word in enumerate(list_of_words):
                                    if "/" in word:
                                        recieving_acc_num = word
                            if "transakce" in sentence:
                                list_of_words = sentence.split(" ")
                                for index, word in enumerate(list_of_words):
                                    if word == "transakce:":
                                        transaction_code = list_of_words[index + 1]
                infos = "Odchozí"
                new_row_data = [date, transaction_code, recieving_acc_num, "SK Slavia Praha", amount, "", "Odchozí",
                                zustatek]
                worksheet_transactions.insert_rows(new_row_data, row_number_to_insert)
