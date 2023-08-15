# SK_slavia_pokuty
K tomu, aby kód fungoval budou potřeba 2 složky s credentials, jedna na gmail_token a druhá s credentials na google sheets.

Co se potřebných knihoven týče, tak jsou potřeba tyto importy:
from simplegmail import Gmail
from simplegmail.query import construct_query
import os.path
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

A pak je ještě důležité myslet na to, že v kódu se nachází i tzv. spreadsheet_key, který se nachází v url našeho sheetu, ale přikaždé změně např. s pozváním nového správce či jakékoli změny s přístupem se ten kód změní, takže je potřeba ho pak vyměnit i v kódu.
