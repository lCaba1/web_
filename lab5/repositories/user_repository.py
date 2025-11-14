class UserRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
    
    def get_by_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
            user = cursor.fetchone()
        return user
    
    def get_by_username_and_password(self, username, password):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s and password_hash = SHA2(%s, 256);", (username, password,))
            user = cursor.fetchone()
        return user
    
    def all(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT users.*, roles.name AS role FROM users LEFT JOIN roles ON users.role_id = roles.id")
            # print(cursor.statement)
            users = cursor.fetchall()
            # print(users)
        return users
    
    def create(self, username, password, first_name, middle_name, last_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = (
                "INSERT INTO users (username, password_hash, first_name, middle_name, last_name, role_id) VALUES "
                "(%s, SHA2(%s, 256), %s, %s, %s, %s);"
            )
            user_data = (username, password, first_name, middle_name, last_name, role_id)
            cursor.execute(query, user_data)
            connection.commit()
    
    def update(self, user_id, first_name, middle_name, last_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = ("UPDATE users SET first_name = %s, "
                     "middle_name = %s, last_name = %s, "
                     "role_id = %s WHERE id = %s")
            user_data = (first_name, middle_name, last_name, role_id, user_id)
            cursor.execute(query, user_data)
            connection.commit()

    def delete(self, user_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()

    def update_password(self, user_id, new_password):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            cursor.execute("UPDATE users SET password_hash = SHA2(%s, 256) WHERE id = %s", (new_password, user_id))
            connection.commit()        