import numpy as np


class PlantCareOptimizer:
    def __init__(self, base_light, base_moisture):
        """
        Initializes a new instance of the PlantCareOptimizer class.

        Parameters:
            base_light (float): The optimal light value for the plant type.
            base_moisture (float): The optimal moisture value for the plant type.
        """
        self.base_light = base_light
        self.base_moisture = base_moisture
        self.plant_stats = []

    def add_plant_stats(self, plant_stats):
        """
        Adds the stats for a plant to the optimizer.

        Parameters:
            plant_stats (tuple): A tuple containing the light value, moisture value, and growth percentage for the plant.
        """
        self.plant_stats.append(plant_stats)

    def calculate_optimal_stats(self):
        """
        Calculates the optimal light and moisture values for the plant type based on the stats for all plants added to the optimizer.

        Returns:
            tuple: A tuple containing the optimal light value and optimal moisture value.
        """
        num_plants = len(self.plant_stats)
        if num_plants == 0:
            return None

        # Create arrays for light, moisture, and growth percentage
        light_arr = np.zeros(num_plants)
        moisture_arr = np.zeros(num_plants)
        growth_arr = np.zeros(num_plants)

        for i in range(num_plants):
            light_arr[i] = self.plant_stats[i][0]
            moisture_arr[i] = self.plant_stats[i][1]
            growth_arr[i] = self.plant_stats[i][2]

        # Calculate mean and standard deviation for light and moisture
        light_mean = np.mean(light_arr)
        light_std = np.std(light_arr)
        moisture_mean = np.mean(moisture_arr)
        moisture_std = np.std(moisture_arr)

        # Calculate optimal light and moisture based on Bayes theorem
        light_optimal = (self.base_light * light_std ** 2 + light_mean * num_plants) / (light_std ** 2 + num_plants)
        moisture_optimal = (self.base_moisture * moisture_std ** 2 + moisture_mean * num_plants) / (
                moisture_std ** 2 + num_plants)

        return light_optimal, moisture_optimal

        # Bayes theorem is used to calculate the optimal values for light and moisture.
        # The formula for Bayes theorem is:
        # P(A|B) = P(B|A) * P(A) / P(B)
        #
        # In this case, A is the optimal value of the parameter (light or moisture),
        # and B is the observed values of the parameter for all plants of the same type.
        # We want to calculate P(A|B), which is the probability distribution of the optimal value
        # given the observed values.
        #
        # The numerator of the formula is:
        # P(B|A) * P(A)
        # This is the prior probability of observing the observed values given the optimal value
        # multiplied by the prior probability of the optimal value.
        #
        # The denominator of the formula is:
        # P(B)
        # This is the marginal probability of observing the observed values.
        #
        # We can simplify the formula by assuming that the observed values follow a normal distribution.
        # In this case, the prior probability of observing the observed values given the optimal value
        # is proportional to the likelihood function of a normal distribution with mean A and standard deviation sigma,
        # evaluated at the observed values. The prior probability of the optimal value is assumed to be a constant.
