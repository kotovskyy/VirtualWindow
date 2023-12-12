import json
import cv2
import threading


class FaceTracker():
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'
        )
        self.last_valid_rect = (0, 0, 0, 0)
        self.last_valid_center = (0, 0)
        self.cap = cv2.VideoCapture(0)
        self.n_prev = 6
        self.prev_rectangles = [(0, 0, 0, 0) for _ in range(self.n_prev)]
    
    def update_rect(self, rect):
        with self.lock:
            self.last_valid_rect = rect
    
    def get_data(self):
        with self.lock:
            x = self.last_valid_rect[0]
            y = self.last_valid_rect[1]
            size = self.last_valid_rect[2]
        data = {
        "x" : x,
        "y" : y,
        "size" : size
        }
        data_json = json.dumps(data)
        return data_json
    
    def rectangleMA(self, prev_rects):
        x_array, y_array, w_array, h_array = ([], [], [], [])
        for (x, y, w, h) in prev_rects:
            x_array.append(x)
            y_array.append(y)
            w_array.append(w)
            h_array.append(h)
        x = int(sum(x_array)/len(x_array))
        y = int(sum(y_array)/len(y_array))
        w = int(sum(w_array)/len(w_array))
        h = int(sum(h_array)/len(h_array))
        return (x, y, w, h)
    

    def startTracking(self):
        while True:
            # Read a frame from the webcam
            ret, frame = self.cap.read()
            if not ret:
                break

            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=7)

            if len(faces) > 0:
                # Draw rectangles around detected faces
                for (x, y, w, h) in faces:
                    # center of the detected rectangle
                    # center = (x+w//2, y+h//2)
                    self.prev_rectangles.pop(0)
                    self.prev_rectangles.append((x, y, w, h))
                    smoother_rect = self.rectangleMA(self.prev_rectangles)
                    x, y, w, h = smoother_rect

                    # prev_centers.pop(0)
                    # prev_centers.append(center)
                    # smooth the central point position using moving average filter
                    smoother_center = (x+w//2, y+h//2)
                    # prev_centers[-1] = smoother_center

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.circle(frame, smoother_center, 1, (0, 0, 255), 2)

                    # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    # cv2.circle(frame, smoother_center, 1, (0, 255, 0), 2)

                    # save last valid position of the central point
                    self.last_valid_center = smoother_center
                    self.update_rect(smoother_rect)
            else:
                # rectangle stays on the screen in the last valid position
                x, y, w, h = self.last_valid_rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                cv2.circle(frame, self.last_valid_center, 1, (0, 0, 255), 2)


            # Display the frame with face tracking
            cv2.imshow('Face Tracking', frame)

            # Break the loop when the 'Esc' key is pressed
            if cv2.waitKey(1) & 0xFF == 27:
                break

            print(self.last_valid_rect)

        self.cap.release()
        cv2.destroyAllWindows()
