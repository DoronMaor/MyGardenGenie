import cv2, socket, pickle
import threading


class VideoStreamReceiver:
    def __init__(self, ip: str, port: int):
        self.receiving = True
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.current_thread = None

    def rec_video(self):
        try:
            self.s.bind((self.ip, self.port))
        except:
            self.ip += 1
            self.s.bind((self.ip, self.port))
        print("Receiving!")
        while self.receiving:
            x = self.s.recvfrom(1000000)
            self.clientip = x[1][0]
            data = x[0]
            data = pickle.loads(data)
            data = cv2.imdecode(data, cv2.IMREAD_COLOR)
            cv2.imshow('Rec', data)
            print(data)
            cv2.waitKey(20)

    def start_receiving(self):
        self.current_thread = threading.Thread(target=self.rec_video)
        self.current_thread.start()
        self.receiving = True

    def stop_receiving(self):
        self.receiving = False
        self.current_thread.join()
        self.current_thread = None
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cv2.destroyAllWindows()
