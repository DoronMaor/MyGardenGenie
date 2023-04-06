from datetime import datetime

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
            user_events = self.events[str(user_id[:-1])]
            log_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

            cevent = {
                "by": user_id,
                "time": log_time,
                "level": level,
                "action": action,
            }

            user_events.insert_one(cevent)
            return True
        except Exception as e:
            print(e)
            return False

    def get_events_by_date(self, user_id, start_date, end_date):
        user_events = self.events[str(user_id[:-1])]

        # convert start_date and end_date to datetime objects
        start_datetime = datetime.strptime(start_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        # build your MongoDB query based on the date range and user ID
        query = {
            "time": {"$gte": start_datetime, "$lte": end_datetime}
        }

        # execute the query and get all matching log events
        logs = user_events.find(query)

        return list(logs)
