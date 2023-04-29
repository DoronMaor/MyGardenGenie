import base64
import os
import re
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
from bson.binary import Binary
import matplotlib.pyplot as plt
import datetime
import pymongo
import random
import time


class LogDatabase:
    def __init__(self):
        # Connect to the MongoDB server
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")

        # Get the "logs" database and the "events" collection
        self.db = self.client["Logs"]
        self.events = self.db["events"]
        self.growth = self.db["growth"]
        self.alerts = self.db["alerts"]
        self.conditions_tester_users = self.db["conditions_tester_users"]

    def insert_event(self, event):
        self.events.insert_one(event)

    def find_events(self, query):
        return self.events.find(query)

    def add_action_args(self, user_id, time: str, level: str, action: str, encoded_images: list):
        try:
            user_events = self.events[str(user_id[:-1])]
            log_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            specify_plant_headers = ["get_moisture", "led_ring", "add_water"]


            cevent = {
                "by": user_id,
                "time": log_time,
                "level": level,
                "action": action,
                "image": encoded_images if encoded_images is not None else None
            }

            user_events.insert_one(cevent)
            return True
        except Exception as e:
            print(e)
            return False

    def get_events_by_date(self, user_id, start_date, end_date, plant_name=None):
        plant_name = None if plant_name == "all" else plant_name

        user_events = self.events[str(user_id[:-1])]

        # convert start_date and end_date to datetime objects
        start_datetime = datetime.datetime.strptime(start_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        # build your MongoDB query based on the date range and user ID
        query = {
            "time": {"$gte": start_datetime, "$lte": end_datetime},
        }

        # add plant name to the query if provided
        if plant_name:
            query["action.1.0"] = plant_name

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

        input_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        start_output_str = input_date.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')

        input_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_output_str = input_date.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')

        # Query growth events within the date range
        query = {"plant_name": plant_name, "time": {"$gte": start_output_str, "$lte": end_output_str}}
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
        return img_html

    def moisture_light_plot(self, user_id, plant_name, start_date=None, end_date=None):
        growth_events = self.growth[str(user_id[:-1])]

        # Set default values for start and end dates
        if start_date is None:
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.date.today().strftime("%Y-%m-%d")

        # Query growth events within the date range
        query = {"plant_name": plant_name, "time": {"$gte": start_date, "$lte": end_date}}
        projection = {"time": 1, "light_level": 1, "moisture_level": 1, "_id": 0}
        results = growth_events.find(query, projection=projection).sort("time")

        # Get the data for moisture and light levels
        moisture_data = []
        light_data = []
        for result in results:
            time = datetime.datetime.strptime(str(result["time"]), "%Y-%m-%d %H:%M:%S")
            moisture_data.append((time, result["moisture_level"]))
            light_data.append((time, result["light_level"]))

        # Plot the data and encode the image as a base64 string
        # Set the figure size
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()

        ax1.plot([data[0] for data in moisture_data], [data[1] for data in moisture_data], 'b-')
        ax2.plot([data[0] for data in light_data], [data[1] for data in light_data], 'r-')
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Moisture Level", color='b')
        ax2.set_ylabel("Light Level", color='r')
        ax1.set_title("Moisture and Light Levels Over Time")

        # Encode the image as a base64 string
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()

        # Build the HTML img tag and return it
        img_html = f'data:image/png;base64,{img_str}'
        return img_html

    ###

    def add_tester_user(self, full_id: str, plant_type: str, new_light_level, new_moisture_level):
        main_id = full_id[:-1]

        user_data = {
            "main_id": main_id,
            "plant_type": plant_type,
            "new_light_level": new_light_level,
            "new_moisture_level": new_moisture_level,
            "starting_date": datetime.date.today().strftime("%Y-%m-%d"),
            "ending_date": (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
        }

        self.conditions_tester_users.insert_one(user_data)

    def get_tester_data_by_plant(self, plant_type: str):
        users = self.conditions_tester_users.find({"plant_type": plant_type})
        plant_data = []
        for user in users:
            user_id = user["main_id"] + "1"
            plant_name = user["plant_type"]
            oldest_height_px = self.get_oldest_height_px(user_id, plant_name)
            light_levels = []
            moisture_levels = []
            growth_percentages = []
            growth_events = self.growth[user["main_id"]]
            for event in growth_events.find({"plant_name": plant_name}):
                light_levels.append(event["light_level"])
                moisture_levels.append(event["moisture_level"])
                height_px = event["height_px"]
                growth_percentage = (height_px - oldest_height_px) / oldest_height_px * 100
                growth_percentages.append(growth_percentage)
            if growth_percentages:
                average_light = sum(light_levels) / len(light_levels)
                average_moisture = sum(moisture_levels) / len(moisture_levels)
                average_growth_percentage = sum(growth_percentages) / len(growth_percentages)
            else:
                average_light = 0
                average_moisture = 0
                average_growth_percentage = 0
            plant_data.append((average_light, average_moisture, average_growth_percentage))
        return plant_data

    ###

    def add_alert(self, user_id, title, details):
        try:
            alerts = self.alerts[str(user_id[:-1])]

            calert = {
                "user_id": user_id,
                "title": title,
                "details": details,
            }

            alerts.insert_one(calert)
            return True
        except Exception as e:
            print(e)
            return False

    def get_alerts(self, user_id):
        try:
            alerts = self.alerts[str(user_id[:-1])]
            user_alerts = list(alerts.find({"user_id": user_id}))
            return user_alerts
        except Exception as e:
            print(e)
            return []

    def get_and_delete_alerts(self, user_id):
        try:
            alerts = self.alerts[str(user_id[:-1])]
            user_alerts = list(alerts.find({"user_id": user_id}))
            alerts.delete_many({"user_id": user_id})
            return user_alerts
        except Exception as e:
            print(e)
            return []

    def delete_alert(self, user_id, title, details):
        try:
            alerts = self.alerts[str(user_id[:-1])]

            result = alerts.delete_one({"user_id": user_id, "title": title, "details": details})
            return result.deleted_count == 1
        except Exception as e:
            print(e)
            return False


    def add_fake_growth_data(self, user_id, plant_name):
        light_levels = [random.randint(500, 1000) for _ in range(10)]
        moisture_levels = [random.randint(30, 80) for _ in range(10)]
        height_px = [random.randint(200, 600) for _ in range(10)]

        current_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        for i in range(10):
            cevent_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            self.add_growth_args(user_id, plant_name, cevent_time, light_levels[i], moisture_levels[i],
                                      height_px[i])
            current_time += datetime.timedelta(hours=1)
            time.sleep(1)

if __name__ == '__main__':
    p = LogDatabase()
    p.add_fake_growth_data("877ef680d0fe4a1ebaaa445f61efb73A", "t")