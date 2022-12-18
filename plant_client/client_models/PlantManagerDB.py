import sqlite3 as lite
import os
import pickle


class PlantManagerDB:
    """
    A class that handles sql connection to users data base.
    Database contains:
        "type"	TEXT,
        "light"	INTEGER,
        "light_hours"	INTEGER,
        "moisture"	INTEGER
    """

    def __init__(self, db_path=None, file_name="plants_conditions.db"):
        """
        Initializes the class
        """
        if not db_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_name = file_name
            self.db_path = os.path.join(base_dir, file_name)
        else:
            self.db_path = db_path + file_name
        self.table_name = file_name[:-3]
        self.conn = lite.connect(self.db_path)
        self.cur = self.conn.cursor()

    def disconnect(self):
        """
        Disconnects from the database
        """
        self.conn.close()

    def db_query(self, query):
        """
        Executes a query
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def add_plant(self, plant_type, light, light_hours, moisture):
        self.cur.execute(
            '''
            INSERT INTO plants (type, light, light_hours, moisture)
            VALUES (?, ?, ?, ?)
            ''',
            (plant_type, light, light_hours, moisture)
        )

    def update_plant(self, plant_type, light, light_hours, moisture):
        self.cur.execute(
            '''
            UPDATE plants
            SET type = ?, light = ?, light_hours = ?, moisture = ?
            WHERE type = ?
            ''',
            (plant_type, light, light_hours, moisture, plant_type)
        )

    def delete_plant(self, plant_type):
        self.cur.execute(
            '''
            DELETE FROM plants
            WHERE type = ?
            ''',
            (plant_type,)
        )

    def get_plant(self, plant_type):
        self.cur.execute(
            '''
            SELECT * FROM plants
            WHERE type = ?
            ''',
            (plant_type,)
        )
        return self.cur.fetchone()

    def get_all_plants(self):
        self.cur.execute(
            '''
            SELECT * FROM plants
            '''
        )
        return self.cur.fetchall()



    # # region for future refrence
    #
    # def sign_up(self, name, password, is_admin, email, age):
    #     """
    #     Signs up a user
    #     """
    #     self.cur.execute("""
    #     INSERT INTO users (username, password, is_admin, email, age, reservations, rated)
    #     VALUES (?, ?, ?, ?, ?)
    #     """, (username, password, is_admin, email, age, pickle.dumps([]), pickle.dumps([])))
    #
    # def add_user(self, us):
    #     """
    #     Adds a user to the database
    #     """
    #     self.cur.execute("""
    #     INSERT INTO users (id, username, password, is_admin, email, age, reservations, rated)
    #     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    #     """, (us.id, us.name, us.password, us.is_admin, us.email, us.age, pickle.dumps(us.reservations)
    #                                    , pickle.dumps(us.rated_apartments)))
    #     self.conn.commit()
    #     return 1
    #
    # def query_to_user(self, query):
    #     """
    #     Queries the database and returns a list of users and converts it to a list of User objects
    #     """
    #     self.cur.execute(query)
    #     users = self.cur.fetchall()
    #     user_list = []
    #     for user in users:
    #         user_list.append(User.User(user[0], user[1], user[2], user[3], user[4], user[5], pickle.loads(user[6]),
    #                                    pickle.loads(user[7])))
    #     return user_list
    #
    # def result_to_user(self, user):
    #     """
    #     Converts a query result to a list of User objects
    #     """
    #     return User.User(user[0], user[1], user[2], user[3], user[4], user[5],
    #                      pickle.loads(user[6]) if user[6] is not None else None,
    #                      pickle.loads(user[7]) if user[7] is not None else None)
    #
    # def add_reservation(self, ap_id, user_id, res_lst):
    #     """
    #     Adds a reservation to the database
    #     """
    #
    #     check_in = res_lst[2]
    #     check_out = res_lst[3]
    #     reserv = [ap_id, check_in, check_out]
    #
    #     self.cur.execute("""
    #     SELECT reservations FROM users
    #     WHERE id = ?
    #     """, (user_id,))
    #     try:
    #         reservations = pickle.loads(self.cur.fetchone()[0])
    #     except:
    #         reservations = []
    #
    #     if reservations:
    #         # append
    #         reservations.append(reserv)
    #     else:
    #         # create
    #         reservations = [reserv]
    #
    #     user_id = user_id if user_id is not None else -1
    #     if user_id:
    #         self.cur.execute("""
    #         UPDATE users
    #         SET reservations = ?
    #         WHERE id = ?
    #         """, (pickle.dumps(reservations), user_id))
    #         self.conn.commit()
    #     return True
    #
    # def add_rating(self, review, logged):
    #     self.cur.execute("""
    #     SELECT rated FROM users
    #     WHERE id = ?
    #     """, (logged.id,))
    #     try:
    #         rated = pickle.loads(self.cur.fetchone()[0])
    #     except:
    #         rated = []
    #
    #     if rated:
    #         # append
    #         rated.append(review)
    #     else:
    #         # create
    #         rated = [review]
    #
    #     self.cur.execute("""
    #     UPDATE users
    #     SET rated = ?
    #     WHERE id = ?
    #     """, (pickle.dumps(rated), logged.id))
    #     self.conn.commit()
    #     return True
    #
    # def get_all_reservations(self):
    #     """
    #     Returns all reservations in the database
    #     """
    #     self.cur.execute("""
    #                    SELECT reservations FROM users
    #                    """)
    #     reservations = self.cur.fetchall()
    #     res_list = []
    #     for res in reservations:
    #         if res is not None:
    #             try:
    #                 res_list.extend(pickle.loads(res[0]))
    #             except:
    #                 pass
    #     return res_list
    #
    # def get_specific_user_resvs(self, user_id):
    #     """
    #     Returns all reservations of a specific user
    #     """
    #     self.cur.execute("""
    #             SELECT reservations FROM users
    #             WHERE id = ?
    #             """, (user_id,))
    #     reservations = self.cur.fetchall()
    #     reservations = reservations[0]
    #     return pickle.loads(reservations[0])
    #
    # def cancel_reservation(self, user_id, house_id):
    #     """
    #     Cancels a reservation
    #     """
    #     query = "SELECT reservations FROM users WHERE id = '" + str(user_id) + "'"
    #     self.cur.execute(query)
    #     reservations = self.cur.fetchone()
    #     if reservations is not None:
    #         reservations = pickle.loads(reservations[0])
    #         for i in range(len(reservations)):
    #             # reservations structure: [[ap_id, check_in, check_out], [ap_id, check_in, check_out], ...]
    #             if reservations[i][0] == house_id:
    #                 reservations.pop(i)
    #                 break
    #         self.cur.execute("UPDATE users SET reservations = ? WHERE id = " + str(user_id),
    #                          (pickle.dumps(reservations),))
    #         self.conn.commit()
    #         return True
    #     else:
    #         return False
    #
    # # endregion
