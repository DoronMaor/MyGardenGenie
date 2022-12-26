from pymongo import MongoClient


class LogDatabase:
    def __init__(self):
        # Connect to the MongoDB server
        self.client = MongoClient("mongodb://localhost:27017/")

        # Get the "logs" database and the "events" collection
        self.db = self.client["Logs"]
        self.events = self.db["events"]

    def insert_event(self, event):
        # Insert a log event into the collection
        self.events.insert_one(event)

    def find_events(self, query):
        # Find log events that match the given query
        return self.events.find(query)

    def add_action_args(self, user_id, time: str, level: str, action: str):
        try:
            user_events = self.events[str(user_id)]

            cevent = {
                "time": time,
                "level": level,
                "action": action,
            }

            user_events.insert_one(cevent)
            return True
        except Exception as e:
            print(e)
            return False


    def get_events_for_user(self, user_id):
        user_events = self.events[str(user_id)]

        # Find all events in the sub-collection
        cursor = user_events.find()

        # Return the events as a list
        return list(cursor)



