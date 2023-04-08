import base64
import os
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import pymongo


class LogDatabase:
    def __init__(self):
        # Connect to the MongoDB server
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")

        # Get the "logs" database and the "events" collection
        self.db = self.client["Logs"]
        self.events = self.db["events"]
        self.growth = self.db["growth"]

    def insert_event(self, event):
        # Insert a log event into the collection
        self.events.insert_one(event)

    def find_events(self, query):
        # Find log events that match the given query
        return self.events.find(query)

    def add_action_args(self, user_id, time: str, level: str, action: str):
        try:
            user_events = self.events[str(user_id[:-1])]
            log_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

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
        start_datetime = datetime.datetime.strptime(start_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        # build your MongoDB query based on the date range and user ID
        query = {
            "time": {"$gte": start_datetime, "$lte": end_datetime}
        }

        # execute the query and get all matching log events
        logs = user_events.find(query)

        return list(logs)

    ###

    def insert_growth_event(self, event):
        self.growth.insert_one(event)

    def add_growth_args(self, user_id, plant_name: str, time: str, light_level, moisture_level, height_px):
        try:
            growth_events = self.growth[str(user_id[:-1])]
            log_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

            cevent = {
                "plant_name": plant_name,
                "time": log_time,
                "light_level": light_level,
                "moisture_level": moisture_level,
                "height_px": height_px,
            }

            growth_events.insert_one(cevent)
            return True
        except Exception as e:
            print(e)
            return False

    def get_oldest_height_px(self, user_id, plant_name):
        try:
            growth_events = self.growth[str(user_id[:-1])]
            query = {"plant_name": plant_name}
            sort = [("time", pymongo.ASCENDING)]
            projection = {"height_px": 1, "_id": 0}
            result = growth_events.find_one(query, projection=projection, sort=sort)
            if result:
                return result["height_px"]
            else:
                return 1
        except Exception as e:
            print(e)
            return 1

    def plot_growth_percentage(self, user_id, plant_name, start_date=None, end_date=None):
        growth_events = self.growth[str(user_id[:-1])]

        # Set default values for start and end dates
        if start_date is None:
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.date.today().strftime("%Y-%m-%d")

        # Query growth events within the date range
        query = {"plant_name": plant_name, "time": {"$gte": start_date, "$lte": end_date}}
        projection = {"time": 1, "height_px": 1, "_id": 0}
        results = growth_events.find(query, projection=projection).sort("time")

        # Convert height_px to growth_percentage
        oldest_height_px = self.get_oldest_height_px(user_id, plant_name)
        growth_data = []
        for result in results:
            height_px = result["height_px"]
            growth_percentage = (height_px - oldest_height_px) / oldest_height_px * 100
            time = result["time"]
            growth_data.append((time, growth_percentage))

        # Plot the data and encode the image as a base64 string
        fig, ax = plt.subplots()
        x = [datetime.datetime.strptime(str(data[0]), "%Y-%m-%d %H:%M:%S") for data in growth_data]
        y = [data[1] for data in growth_data]
        ax.plot(x, y)
        ax.set_xlabel("Time")
        ax.set_ylabel("Growth Percentage")
        ax.set_title("Plant Growth Over Time")

        # Encode the image as a base64 string
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()

        # Build the HTML img tag and return it
        img_html = f'data:image/png;base64,{img_str}'
        print(img_html)
        return img_html

