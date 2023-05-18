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
        """
        Initializes a connection to the MongoDB server and sets up the necessary collections.
        """
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")

        self.db = self.client["Logs"]
        self.events = self.db["events"]
        self.growth = self.db["growth"]
        self.alerts = self.db["alerts"]
        self.conditions_tester_users = self.db["conditions_tester_users"]

    def insert_event(self, event):
        """
        Inserts a log event into the "events" collection.

        Args:
            event (dict): The log event to be inserted.

        Returns:
            bool: True if the event was inserted successfully, False otherwise.
        """
        self.events.insert_one(event)

    def find_events(self, query):
        """
        Finds log events in the "events" collection that match the given query.

        Args:
            query (dict): The MongoDB query for finding log events.

        Returns:
            pymongo.Cursor: A cursor pointing to the result of the find operation.
        """
        return self.events.find(query)

    def add_action_args(self, user_id, time: str, level: str, action: str, encoded_images: list):
        """
        Adds action arguments to a log event for a specific user.

        Args:
            user_id (str): The ID of the user.
            time (str): The timestamp of the log event in the format "%Y-%m-%d %H:%M:%S".
            level (str): The level of the log event.
            action (str): The action performed by the user.
            encoded_images (list): A list of encoded images related to the log event.

        Returns:
            bool: True if the action arguments were added successfully, False otherwise.
        """
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
        """
        Retrieves log events for a specific user within a given date range.

        Args:
            user_id (str): The ID of the user.
            start_date (str): The start date of the date range in the format "%Y-%m-%d".
            end_date (str): The end date of the date range in the format "%Y-%m-%d".
            plant_name (str, optional): The name of the plant. Defaults to None.

        Returns:
            list: A list of log events matching the query.
        """
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
            query["$or"] = [
                {"action.1": plant_name},
                {"action.1.0": plant_name}
            ]

        # execute the query and get all matching log events
        logs = user_events.find(query)

        return list(logs)

    ###

    def insert_growth_event(self, event):
        """
        Inserts a growth event into the "growth" collection.

        Args:
            event (dict): The growth event to be inserted.

        Returns:
            bool: True if the event was inserted successfully, False otherwise.
        """
        self.growth.insert_one(event)

    def add_growth_args(self, user_id, plant_name: str, time: str, light_level, moisture_level, height_px):
        """
        Adds growth arguments to a growth event for a specific user and plant.

        Args:
            user_id (str): The ID of the user.
            plant_name (str): The name of the plant.
            time (str): The timestamp of the growth event in the format "%Y-%m-%d %H:%M:%S".
            light_level: The light level for the growth event.
            moisture_level: The moisture level for the growth event.
            height_px: The height in pixels for the growth event.

        Returns:
            bool: True if the growth arguments were added successfully, False otherwise.
        """
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
        """
           Retrieves the oldest height in pixels for a given user ID and plant name.

           Args:
               user_id (str): User ID.
               plant_name (str): Plant name.

           Returns:
               int: Oldest height in pixels if available, 1 otherwise.
        """
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

    def plot_growth_percentage(self, user_id, plant_name, logs, start_date=None, end_date=None):
        """
        Generates a plot of growth percentage over time for a specific user ID and plant name,
        along with intervention data.

        Args:
            user_id (str): User ID.
            plant_name (str): Plant name.
            logs (list): List of intervention logs.
            start_date (str, optional): Start date for the data range. Defaults to None.
            end_date (str, optional): End date for the data range. Defaults to None.

        Returns:
            str: HTML img tag representing the plot as a base64-encoded image.
        """
        growth_events = self.growth[str(user_id[:-1])]

        # Set default values for start and end dates
        if start_date is None:
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.date.today().strftime("%Y-%m-%d")

        input_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        start_output_str = input_date.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')

        input_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_output_str = input_date.strftime('%Y-%m-%dT%H:%M:%S.%f+10:00')

        # Query growth events within the date range
        query = {"plant_name": plant_name,
                 "time": {"$gte": datetime.datetime.strptime(start_output_str, '%Y-%m-%dT%H:%M:%S.%f+00:00'),
                          "$lte": datetime.datetime.strptime(end_output_str, '%Y-%m-%dT%H:%M:%S.%f+10:00')}}
        projection = {"time": 1, "height_px": 1, "_id": 0}
        results = growth_events.find(query, projection=projection).sort("time")

        # Get the oldest height in pixels
        oldest_height_px = self.get_oldest_height_px(user_id, plant_name)

        # Prepare growth data
        growth_data_points = []
        for result in results:
            height_px = result["height_px"]
            growth_percentage = (height_px - oldest_height_px) / oldest_height_px * 100
            time = result["time"]
            growth_data_points.append((time, growth_percentage))

        if not growth_data_points:
            return None

        # Prepare intervention data
        intervention_points = []
        colors = []
        labels = []

        last_time = growth_data_points[-1][0]

        for intervention in logs:
            intervention_time = datetime.datetime.strptime(intervention["time"], "%Y-%m-%d %H:%M:%S")
            if intervention_time > last_time:
                continue

            action = intervention["action"]
            if action.startswith("Watered"):
                color = "blue"
            elif action.startswith("Turned LED"):
                color = "green"
            else:
                color = "red"  # Default color for other interventions

            # Find the growth data point closest to the intervention time
            closest_point = min(growth_data_points, key=lambda x: abs(x[0] - intervention_time))
            intervention_points.append((intervention_time, closest_point[1]))
            colors.append(color)
            labels.append(action)

        # Plot the data
        fig, ax = plt.subplots(figsize=(10, 6))
        x_growth = [data[0] for data in growth_data_points]
        y_growth = [data[1] for data in growth_data_points]
        ax.plot(x_growth, y_growth, label="Growth", color="orange")

        for i in range(len(intervention_points)):
            ax.scatter(intervention_points[i][0], intervention_points[i][1],
                       c=colors[i], s=100)

        # Create a single legend for all intervention actions
        legend_labels = ["LED", "Watered"]
        legend_handles = [plt.Line2D([], [], marker='o', color='w', markerfacecolor=color, markersize=8)
                          for color in set(colors)]
        ax.legend(legend_handles, legend_labels)

        # Add labels to the intervention dots
        for i in range(len(intervention_points)):
            ax.annotate(labels[i], (intervention_points[i][0], intervention_points[i][1]),
                        xytext=(10, 10), textcoords='offset points', color="black", fontsize=10)

        # Set axes labels and title
        ax.set_xlabel("Time")
        ax.set_ylabel("Growth Percentage")
        ax.set_title("Plant Growth Over Time")
        ax.legend()

        # Encode the image as a base64 string
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()

        # Build the HTML img tag and return it
        img_html = f'data:image/png;base64,{img_str}'
        return img_html

    def moisture_light_plot(self, user_id, plant_name, start_date=None, end_date=None):
        """
        Generates a plot of moisture and light levels over time for a specific user ID and plant name.

        Args:
            user_id (str): User ID.
            plant_name (str): Plant name.
            start_date (str, optional): Start date for the data range. Defaults to None.
            end_date (str, optional): End date for the data range. Defaults to None.

        Returns:
            str: HTML img tag representing the plot as a base64-encoded image.
        """
        growth_events = self.growth[str(user_id[:-1])]

        # Set default values for start and end dates
        if start_date is None:
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.date.today().strftime("%Y-%m-%d")

        input_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        start_output_str = input_date.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')

        input_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_output_str = input_date.strftime('%Y-%m-%dT%H:%M:%S.%f+10:00')

        # Query growth events within the date range
        query = {"plant_name": plant_name,
                 "time": {"$gte": datetime.datetime.strptime(start_output_str, '%Y-%m-%dT%H:%M:%S.%f+00:00'),
                          "$lte": datetime.datetime.strptime(end_output_str, '%Y-%m-%dT%H:%M:%S.%f+10:00')}}
        projection = {"time": 1, "light_level": 1, "moisture_level": 1, "_id": 0}
        results = growth_events.find(query, projection=projection).sort("time")

        # Get the data for moisture and light levels
        moisture_data = []
        light_data = []
        for result in results:
            time = datetime.datetime.strptime(str(result["time"]), "%Y-%m-%d %H:%M:%S")
            moisture_data.append((time, result["moisture_level"]))
            light_data.append((time, result["light_level"]))

        if not light_data:
            return None

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
        """
        Adds a tester user with the specified details.

        Args:
            full_id (str): Full user ID.
            plant_type (str): Plant type.
            new_light_level: New light level.
            new_moisture_level: New moisture level.
        """
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
        """
        Retrieves tester data for a specific plant type.

        Args:
            plant_type (str): Plant type.

        Returns:
            list: List of tuples containing average light level, average moisture level,
            and average growth percentage for each tester user.
        """
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
        """
        Adds an alert for a specific user.

        Args:
            user_id (str): User ID.
            title (str): Alert title.
            details (str): Alert details.

        Returns:
            bool: True if the alert was successfully added, False otherwise.
        """
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
        """
        Retrieves all alerts for a specific user.

        Args:
            user_id (str): User ID.

        Returns:
            list: List of dictionaries representing alerts.
        """
        try:
            alerts = self.alerts[str(user_id[:-1])]
            user_alerts = list(alerts.find({"user_id": user_id}))
            return user_alerts
        except Exception as e:
            print(e)
            return []

    def get_and_delete_alerts(self, user_id):
        """
        Retrieves and deletes all alerts for a specific user.

        Args:
            user_id (str): User ID.

        Returns:
            list: List of dictionaries representing alerts.
        """
        try:
            alerts = self.alerts[str(user_id[:-1])]
            user_alerts = list(alerts.find({"user_id": user_id}))
            alerts.delete_many({"user_id": user_id})
            return user_alerts
        except Exception as e:
            print(e)
            return []

    def delete_alert(self, user_id, title, details):
        """
        Deletes a specific alert for a user.

        Args:
            user_id (str): User ID.
            title (str): Alert title.
            details (str): Alert details.

        Returns:
            bool: True if the alert. Use max_tokens to increase the limit if necessary.
        """
        try:
            alerts = self.alerts[str(user_id[:-1])]

            result = alerts.delete_one({"user_id": user_id, "title": title, "details": details})
            return result.deleted_count == 1
        except Exception as e:
            print(e)
            return False

    def add_fake_growth_data(self, user_id, plant_name, start_date, end_date):
        n = 100
        light_levels = [random.randint(500, 1000) for _ in range(n)]
        moisture_levels = [random.randint(30, 80) for _ in range(n)]
        height_px = [random.randint(200, 600) for _ in range(n)]

        current_time = start_date.replace(minute=0, second=0, microsecond=0)
        delta = datetime.timedelta(hours=1)
        date_format = "%Y-%m-%d %H:%M:%S"

        for i in range(n):
            current_time_str = current_time.strftime(date_format)
            self.add_growth_args(user_id, plant_name, current_time_str, light_levels[i], moisture_levels[i],
                                 height_px[i])
            current_time += delta
            time.sleep(0.1)

    def add_fake_action_data(self, user_id, start_date, end_date):
        plant_names = ["A", "B"]
        levels = ["Automatic", "Manual"]
        delta = datetime.timedelta(hours=1)
        date_format = "%Y-%m-%d %H:%M:%S"

        current_time = start_date
        while current_time <= end_date:
            action = random.choice([
                ("add_water", random.choice(plant_names)),
                ("led_ring", [random.choice(plant_names), random.choice([True, False])])
            ])
            level = random.choice(levels)
            current_time_str = current_time.strftime(date_format)
            self.add_action_args(user_id, current_time_str, level, action, None)
            current_time += delta

if __name__ == '__main__':
    p = LogDatabase()

    start_date = datetime.datetime(2023, 5, 15, 9, 0, 0)
    end_date = datetime.datetime(2023, 5, 18, 0, 0, 0)

    p.add_fake_growth_data("f4824b9d981240a8bbcff6bc810acd9A", "mol", start_date, end_date)
    p.add_fake_action_data("f4824b9d981240a8bbcff6bc810acd9A", start_date, end_date)
