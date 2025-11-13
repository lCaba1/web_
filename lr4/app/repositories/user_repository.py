class UserRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
    
    def get_all(self):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            cursor.execute("SELECT users.*, roles.name AS role_name FROM users LEFT JOIN roles ON users.role_id = roles.id")
            users = cursor.fetchall()
        return users
    
    def get_with_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
            user = cursor.fetchone()
        return user
    
    def get_with_login_password(self, login, password):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            cursor.execute("SELECT * FROM users WHERE login = %s and password_hash = SHA2(%s, 256);", (login, password,))
            user = cursor.fetchone()
        return user
    
    def create(self, login, password, last_name, first_name, middle_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple = True) as cursor:
            query = (
                "INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id) VALUES "
                "(%s, SHA2(%s, 256), %s, %s, %s, %s);"
            )
            data = (login, password, last_name, first_name, middle_name, role_id)
            cursor.execute(query, data)
            connection.commit()
    
    def update(self, id, last_name, first_name, middle_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple = True) as cursor:
            query = ("UPDATE users SET last_name = %s, "
                     "first_name = %s, middle_name = %s, "
                     "role_id = %s WHERE id = %s")
            data = (last_name, first_name, middle_name, role_id, id)
            cursor.execute(query, data)
            connection.commit()

    def delete(self, id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple = True) as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (id,))
            connection.commit()

    def update_password(self, id, new_password):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple = True) as cursor:
            cursor.execute("UPDATE users SET password_hash = SHA2(%s, 256) WHERE id = %s", (new_password, id))
            connection.commit()        
