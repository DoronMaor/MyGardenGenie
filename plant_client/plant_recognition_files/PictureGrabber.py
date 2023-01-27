import cv2


class PictureGrabber:
    def __init__(self):
        self.cap = None

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 1024)

    def take_a_picture(self):
        self.setup_camera()
        while True:
            ret, photo = self.cap.read()

            if photo is not None:
                cv2.imwrite('temp' + '.jpg', photo)
                break


def stop_streaming(self):
    cv2.destroyAllWindows()
    self.cap.release()


p = PictureGrabber()
p.take_a_picture()
