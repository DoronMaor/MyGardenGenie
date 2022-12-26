from models.PlantUserCon import PlantUserCon


class PlantUserList:
    def __init__(self):
        self.lst = [None]
        self.dict = {}
        # {idnum: PlantUserCon}
        # PlantUserCon = plant, user, id_num, psock, usock.
        #for i in range(0, 9999999):
        #    self.lst += [None]

    def add_con(self, data: tuple, sock):
        id_num = data[-1]
        try:
            #self.lst[id_num].auto_set(data[1], sock)
            self.dict[id_num].auto_set(data[1], sock)
        except:
            #self.lst[id_num] = PlantUserCon(data[1], data[-1], sock)
            self.dict[id_num] = PlantUserCon(data[1], data[-1], sock)

    def get_sock(self, c_type, id_num):
        for i in self.dict:
            pc = self.dict[i]
            if pc is not None:
                if pc.get_id() == id_num:
                    if c_type == "plant":
                        return pc.get_plant_sock()
                    elif c_type == "user":
                        return pc.get_user_sock()
                    return -1
        return -1

    def get_id_by_sock(self, sck):
        for i in self.dict:
            pc = self.dict[i]
            usock = pc.get_user_sock()
            psock = pc.get_plant_sock()

            if usock == sck or psock == sck:
                return i
        return -1

