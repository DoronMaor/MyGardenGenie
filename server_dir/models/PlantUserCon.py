class PlantUserCon:
    """
    Class representing a plant or user connection.
    """

    def __init__(self, c_type: str, full_id: str, sock, stream_ip):
        """
        Initializes a PlantUserCon instance.

        Args:
            c_type (str): The type of connection ("plant" or "user").
            full_id (str): The full ID of the connection.
            sock: The socket object associated with the connection.
            stream_ip: The streaming IP address associated with the connection.
        """
        self.plant = None
        self.users = ["A", "B"]
        self.id_num = full_id[:-1]
        if stream_ip:
            self.stream_ip = stream_ip

        if c_type == "plant":
            self.set_plant(sock)
        elif c_type == "user":
            self.set_user(sock, full_id[-1])

    def set_plant(self, sock):
        """
        Sets the socket object for the plant connection.

        Args:
            sock: The socket object to set.
        """
        self.plant = sock

    def set_user(self, sock, letter):
        """
        Sets the socket object for the specified user connection.

        Args:
            sock: The socket object to set.
            letter (str): The letter representing the user ('A' or 'B').
        """
        self.users[0 if letter == 'A' else 1] = sock
        print("users", self.users)

    def auto_set(self, c_type, sock, full_id, stream_ip):
        """
        Automatically sets the connection based on the given parameters.

        Args:
            c_type (str): The type of connection ("plant" or "user").
            sock: The socket object to set.
            full_id (str): The full ID of the connection.
            stream_ip: The streaming IP address associated with the connection.
        """
        if stream_ip:
            self.stream_ip = stream_ip
        if c_type == "plant":
            self.set_plant(sock)
        elif c_type == "user":
            self.set_user(sock, full_id[-1])

    def get_id(self):
        """
        Returns the ID number of the connection.

        Returns:
            str: The ID number.
        """
        return self.id_num

    def get_stream_ip(self):
        """
        Returns the streaming IP address associated with the connection.

        Returns:
            The streaming IP address.
        """
        return self.stream_ip

    def get_user_sock(self, letter):
        """
        Returns the socket object for the specified user connection.

        Args:
            letter (str): The letter representing the user ('A' or 'B').

        Returns:
            The socket object for the specified user connection.
        """
        print("users get", self.users)
        return self.users[0 if letter == 'A' else 1]

    def get_both_users_sock(self):
        """
        Returns the socket objects for both user connections.

        Returns:
            list: A list containing the socket objects for both user connections.
        """
        return self.users

    def get_plant_sock(self):
        """
        Returns the socket object for the plant connection.

        Returns:
            The socket object for the plant connection.
        """
        return self.plant
