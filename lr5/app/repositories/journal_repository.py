class JournalRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def create(self, path, user_id = None):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple = True) as cursor:
            query = (
                "INSERT INTO visit_logs (path, user_id) VALUES "
                "(%s, %s);"
            )
            visit_data = (path, user_id)
            cursor.execute(query, visit_data)
            connection.commit()

    def get_all(self):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            cursor.execute("SELECT visit_logs.*, user.last_name, user.first_name, user.middle_name " \
            "FROM visit_logs " \
            "LEFT JOIN users AS user ON user.id = visit_logs.user_id;")            
            logs = cursor.fetchall()
        return logs

    def get_all_with_user_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            cursor.execute("SELECT visit_logs.*, user.last_name, user.first_name, user.middle_name " \
            "FROM visit_logs " \
            "LEFT JOIN users AS user ON user.id = visit_logs.user_id " \
            "WHERE visit_logs.user_id = %s ", (user_id, ))            
            logs = cursor.fetchall()
        return logs

    def get_total_count(self):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            cursor.execute("SELECT COUNT(*) as total_count FROM visit_logs")
            role = cursor.fetchone()
        return role.total_count

    def get_total_count_with_user_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            cursor.execute("SELECT COUNT(*) as total_count FROM visit_logs WHERE visit_logs.user_id = %s", (user_id, ))
            print(cursor.statement)
            role = cursor.fetchone()
        return role.total_count

    def get_page(self, limit = 10, page = 1):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            query_params = (limit, (page - 1)*limit )
            cursor.execute("SELECT visit_logs.*, user.last_name, user.first_name, user.middle_name " \
            "FROM visit_logs " \
            "LEFT JOIN users AS user ON user.id = visit_logs.user_id " \
            "ORDER BY visit_logs.id DESC " \
            "LIMIT %s " \
            "OFFSET %s;", query_params)
            logs = cursor.fetchall()
        return logs
    
    def get_page_with_user_id(self, user_id, limit = 10, page = 1):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            query_params = (user_id, limit, (page - 1)*limit)
            cursor.execute("SELECT visit_logs.*, user.last_name, user.first_name, user.middle_name " \
            "FROM visit_logs " \
            "LEFT JOIN users AS user ON user.id = visit_logs.user_id " \
            "WHERE visit_logs.user_id = %s " \
            "ORDER BY visit_logs.id DESC " \
            "LIMIT %s " \
            "OFFSET %s;", query_params)            
            logs = cursor.fetchall()
        return logs
    
    def log_page_aggregation(self, user_id = None):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            if user_id != None:
                cursor.execute("SELECT path, COUNT(*) as number_of_visits " \
                "FROM visit_logs " \
                "WHERE user_id = %s " \
                "GROUP BY path " \
                "ORDER BY COUNT(*) DESC;", (user_id,))
            else:
                cursor.execute("SELECT path, COUNT(*) as number_of_visits " \
                "FROM visit_logs " \
                "GROUP BY path " \
                "ORDER BY COUNT(*) DESC;")
            page_statistics = cursor.fetchall()
        return page_statistics

    def log_user_aggregation(self, user_id = None):
        with self.db_connector.connect().cursor(named_tuple = True) as cursor:
            if user_id != None:
                cursor.execute("SELECT user_id, COUNT(*) AS number_of_visits, " \
                "CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) AS user_full_name " \
                "FROM visit_logs " \
                "LEFT JOIN users as u on u.id = visit_logs.user_id " \
                "WHERE user_id = %s " \
                "GROUP BY " \
                "user_id " \
                "ORDER BY COUNT(*) DESC;", (user_id,))
            else:
                cursor.execute("SELECT user_id, COUNT(*) AS number_of_visits, " \
                "CASE " \
                "WHEN user_id IS NULL THEN 'Неаутентифицированный пользователь'" \
                "ELSE CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name) " \
                "END AS user_full_name " \
                "FROM visit_logs " \
                "LEFT JOIN users as u on u.id = visit_logs.user_id " \
                "GROUP BY user_id " \
                "ORDER BY " \
                "COUNT(*) DESC;")            
            user_statistics = cursor.fetchall()
            print(user_statistics)
        return user_statistics
