import psycopg2
import bcrypt

from psycopg2 import sql
from enum import Enum


# db_params_1 = {
#     'host' : 'localhost',
#     'port' : '5432', 
#     'user' : 'postgres',
#     'password' : 'postgres',
# }

# def create_database():
#     new_database_name = 'project1'
#     connection = psycopg2.connect(**db_params_1)
#     connection.autocommit = True
#     cursor = connection.cursor()

#     create_database_query = f"CREATE DATABASE {new_database_name};"
#     cursor.execute(create_database_query)
#     connection.commit()
#     cursor.close()
#     connection.close()

# create_database()

class Role(Enum):
    SuperAdmin = 1
    Admin = 2
    Customer = 3

class Permissions(Enum):
    CRUD = 'CRUD'
    RUD = 'RUD'
    RU = 'RU'

class CredentialsDB:

    db_params = {
        'host' : 'localhost',
        'port' : '5432', 
        'user' : 'postgres',
        'password' : 'postgres',
        'database': 'project1',
    }
        
    def __init__(self):
        self.connection = psycopg2.connect(**self.db_params)
        self.cursor = self.connection.cursor()
    
    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def _insert_user(self, username, role, permissions, hashed_password, salt):
        insert_query = sql.SQL("""
        INSERT INTO usersDB (username, role, Public_TODO, Private_TODO, hashed_password, salt) VALUES ({}, {}, {}, {}, {}, {});
        """).format(sql.Literal(username), sql.Literal(role.value), sql.Literal(permissions.value), sql.Literal(permissions.value), sql.Literal(psycopg2.Binary(hashed_password)),  sql.Literal(psycopg2.Binary(salt)))
        
        self.cursor.execute(insert_query)
        self.connection.commit()

    def _authenticate_user(self,ip_username, ip_password):
        authenticate_query = "SELECT hashed_password, salt FROM usersDB WHERE username = %s"
        self.cursor.execute(authenticate_query,(ip_username,))
        user_data = self.cursor.fetchone()
        if user_data == None:
            print("user data is none")
            return None
        stored_pwd = user_data[0]
        # stored_salt = user_data[1]
        result = bcrypt.checkpw(ip_password.encode('utf-8'), stored_pwd.tobytes())
        # print("checkpwd",result)
        return result
    
    def _get_todo(self, username):
        public_query = "SELECT Public_TODO FROM usersDB WHERE username = %s"
        private_query = "SELECT Private_TODO FROM usersDB WHERE username = %s"
        
        self.cursor.execute(public_query,(username,))
        public_todos = self.cursor.fetchone()

        self.cursor.execute(private_query,(username,))
        private_todos = self.cursor.fetchone()
        return {'public_todos': public_todos, 'private_todos': private_todos}

    def create_users_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS usersDB(
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        Role INTEGER NOT NULL,
        Public_TODO VARCHAR(255) NOT NULL,
        Private_TODO VARCHAR(255) NOT NULL,
        hashed_password BYTEA NOT NULL,
        salt BYTEA NOT NULL
        );
        """
        self.cursor.execute("DROP TABLE usersDB")
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def insert_user(self, username, role, permissions, password):
        salt = bcrypt.gensalt()
        # print("salt", salt)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt) 
        print(hashed_password)
        self._insert_user(username, role, permissions, hashed_password, salt)

    def authenticate_user(self, ip_username, ip_password):
        return self._authenticate_user(ip_username, ip_password)

    def get_todo(self, username):
        return self._get_todo(username)

if __name__ == "__main__":
    db = CredentialsDB()
    db.create_users_table()
    db.insert_user('sachin', Role.SuperAdmin, Permissions.CRUD, 'password1')
    db.insert_user('jk', Role.Admin, Permissions.RUD, 'password2')
    db.insert_user('AmalDavis', Role.Customer, Permissions.CRUD, 'password3')

    # db.authenticate_user('sachin', 'password1')