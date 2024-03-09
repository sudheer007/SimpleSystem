import psycopg2
import bcrypt

from psycopg2 import sql


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

db_params = {
    'host' : 'localhost',
    'port' : '5432', 
    'user' : 'postgres',
    'password' : 'postgres',
    'database': 'project1',
}

def create_users_table():
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS usersDB(
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    Role VARCHAR(255) NOT NULL,
    Public_TODO VARCHAR(255) NOT NULL,
    Private_TODO VARCHAR(255) NOT NULL,
    hashed_password BYTEA NOT NULL,
    salt BYTEA NOT NULL
    );
    """
    # cursor.execute("DROP TABLE usersDB")
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    connection.close()

def insert_user(username, role, permissions, password):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    salt = bcrypt.gensalt()
    print("salt", salt)

    hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt) 
    print(hashed_password)

    insert_query = sql.SQL("""
    INSERT INTO usersDB (username, role, Public_TODO, Private_TODO, hashed_password, salt) VALUES ({}, {}, {}, {}, {}, {});
    """).format(sql.Literal(username), sql.Literal(role), sql.Literal(permissions), sql.Literal(permissions), sql.Literal(psycopg2.Binary(hashed_password)),  sql.Literal(psycopg2.Binary(salt)))
    
    cursor.execute(insert_query)
    connection.commit()
    cursor.close()
    connection.close()

def authenticate_user(ip_username, ip_password):
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    authenticate_query = "SELECT hashed_password, salt FROM usersDB WHERE username = %s"
    
    cursor.execute(authenticate_query,(ip_username,))
    
    user_data = cursor.fetchone()
    if user_data == None:
        return None
    stored_pwd = user_data[0]
    stored_salt = user_data[1]
    # print(stored_salt, type(stored_salt))
    # hashed_ip_pwd = bcrypt.hashpw(ip_password.encode('utf-8'),stored_salt.tobytes())
    result = bcrypt.checkpw(ip_password.encode('utf-8'), stored_pwd.tobytes())
    # result = True if hashed_ip_pwd == stored_pwd else None
    

    # print(hashed_ip_pwd, stored_pwd.tobytes())
    # print(stored_salt.tobytes())

    cursor.close()
    connection.close()

    return result
def get_todo(username):
    
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()

    public_query = "SELECT Public_TODO FROM usersDB WHERE username = %s"
    private_query = "SELECT Private_TODO FROM usersDB WHERE username = %s"
    
    cursor.execute(public_query,(username,))
    public_todos = cursor.fetchone()

    cursor.execute(private_query,(username,))
    private_todos = cursor.fetchone()
    return {'public_todos': public_todos, 'private_todos': private_todos}


# create_users_table()

# insert_user('sachin', 'SuperAdmin', 'CRUD', 'password1')
# insert_user('jk','Admin', 'RUD', 'password2')
# insert_user('AmalDavis','Customer', 'RU', 'password3')
