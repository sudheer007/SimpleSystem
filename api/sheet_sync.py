import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from time import sleep

class SyncDBSheet:
    def __init__(self, service_account_file, folder_id, db_params):
        self.service_account_file = service_account_file
        self.folder_id = folder_id
        self.db_params = db_params
        self.scope = [r'https://www.googleapis.com/auth/spreadsheets', r"https://www.googleapis.com/auth/drive"]
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.service_account_file, self.scope)
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = self.client.open('project1')

    def create_spreadsheet(self):
        self.client.create('project1', folder_id=self.folder_id)


    def sync_db_to_sheet(self):
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()

        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cursor.fetchall()

        existing_sheets = [sheet.title for sheet in self.spreadsheet.worksheets()]
        for table in tables:
            table_name = table[0]
            if table_name not in existing_sheets:
                self.spreadsheet.add_worksheet(title=table_name, rows="100", cols="20")
                existing_sheets.append(table_name)

        for sheet in self.spreadsheet.worksheets():
            if sheet.title in existing_sheets:
                table_name = sheet.title
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                sheet.clear()
                converted_data = []
                # memoryview cannot add to spreadsheet , so converted to bytes then string
                for row in data:
                    converted_row = []
                    for elem in row:
                        if isinstance(elem, memoryview):
                            elem = str(bytes(elem))
                        converted_row.append(elem)
                    converted_data.append(converted_row)
                sheet.insert_rows(converted_data)

        cursor.close()
        conn.close()

    
    def sync_sheet_to_db(self):
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()

        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = cursor.fetchall()

        for sheet in self.spreadsheet.worksheets():
            table_name = sheet.title
            if table_name in [table[0] for table in tables]:
                data = sheet.get_all_values()
                cursor.execute(f"TRUNCATE {table_name}")
                converted_data = []
                for row in data:
                    converted_row = []
                    for elem in row:
                        if elem.startswith("b'$"):
                            byte_string = elem[2:-1]
                            elem = byte_string.encode('utf-8')
                        converted_row.append(elem)
                    converted_data.append(converted_row)
                    cursor.execute(f"INSERT INTO {table_name} VALUES ({','.join(['%s']*len(converted_row))})", converted_row)
        conn.commit()
        cursor.close()
        conn.close()

    def run(self):
        while True:
            self.sync_db_to_sheet()
            self.sync_sheet_to_db()
            sleep(3600)



if __name__ == "__main__":
    SERVICE_ACCOUNT_FILE = r"D:\Sudheer_study_projects\project1\SimpleSystem\creds\simplesystem-c6611061f775.json"
    FOLDER_ID = r"1JVPoM6HH0hte7tUoCxJORaQE6Tt_cnJu"

    DB_PARAMS = {'dbname' : 'project1',
                'host' : 'localhost',
                'port' : '5432', 
                'user' : 'postgres',
                'password' : 'postgres'
            }

    sync_db_sheet = SyncDBSheet(SERVICE_ACCOUNT_FILE, FOLDER_ID, DB_PARAMS)
    sync_db_sheet.sync_db_to_sheet()
    # sync_db_sheet.sync_sheet_to_db()
    # sync_db_sheet.run()


# create_spreadsheet()
#spreadsheet_url = https://docs.google.com/spreadsheets/d/1kvjDVuivp1k80DHY5IrzzucgxsMlAqGsZVN_3dUboiE
# sync_db_to_sheet()
# sync_sheet_to_db()

