from models.PlantUserCon import PlantUserCon


class PlantUserList:
    def __init__(self):
        self.dict = {}

    def add_con(self, data: tuple, sock):
        id_num = data[-1]
        try:
            self.dict[id_num[:-1]].auto_set(c_type=data[1], full_id=id_num, sock=sock)
        except:
            self.dict[id_num[:-1]] = PlantUserCon(c_type=data[1], full_id=id_num, sock=sock)

    def add_con_web(self, c_type, id_num, sock):
        try:
            c_type, stream_ip = c_type
            if c_type == 'user':
                stream_ip = None
        except:
            c_type, stream_ip = c_type, None
        try:
            self.dict[id_num[:-1]].auto_set(c_type=c_type, full_id=id_num, sock=sock, stream_ip=stream_ip)
        except:
            self.dict[id_num[:-1]] = PlantUserCon(c_type=c_type, full_id=id_num, sock=sock, stream_ip=stream_ip)

    def get_sock(self, c_type, full_id_num):
        for i in self.dict:
            pc = self.dict[i]
            if pc is not None:
                if pc.get_id() == full_id_num[:-1]:
                    if c_type == "plant":
                        return pc.get_plant_sock()
                    elif c_type == "user":
                        return pc.get_user_sock(full_id_num[-1])
                    elif c_type == "both_users":
                        return pc.get_both_users_sock()
                    return -1
        return -1

    def get_id_by_sock(self, sck):
        for i in self.dict:
            pc = self.dict[i]
            usock = pc.get_user_sock()
            psock1 = pc.get_plant_sock('A')
            psock2 = pc.get_plant_sock('B')

            if usock == sck or psock1 == sck or psock2 == sck:
                return i
        return -1

    def get_stream_ip_by_sock(self, sck):
        for i in self.dict:
            pc = self.dict[i]
            psock = pc.get_plant_sock()
            usock1 = pc.get_user_sock('A')
            usock2 = pc.get_user_sock('B')

            if psock == sck or usock1 == sck or usock2 == sck:
                return pc.get_stream_ip()

        return "127.0.0.1"
