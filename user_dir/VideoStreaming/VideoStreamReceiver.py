import cv2, socket, pickle


class VideoStreamReceiver:
    def __init__(self, ip: str, port: int):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.s.bind((self.ip, self.port))
        self.receiving = True

    def start_receiving(self):
        self.receiving = True
        print("Receiving!")
        while self.receiving:
            x = self.s.recvfrom(1000000)
            self.clientip = x[1][0]
            data = x[0]
            data = pickle.loads(data)
            data = cv2.imdecode(data, cv2.IMREAD_COLOR)
            cv2.imshow('server', data)


    def stop_receiving(self):
        self.receiving = False
        cv2.destroyAllWindows()

