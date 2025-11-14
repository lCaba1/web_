class RoleRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector
    
    def all(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT roles.* FROM roles")
            # print(cursor.statement)
            roles = cursor.fetchall()
        return roles
    
    def get_by_id(self, role_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT roles.* FROM roles WHERE roles.id = %s", (role_id,))
            # print(cursor.statement)
            role = cursor.fetchone()
        return role
    
    def get_by_name(self, role_name):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT roles.* FROM roles WHERE roles.name = %s", (role_name,))
            # print(cursor.statement)
            role = cursor.fetchone()
        return role