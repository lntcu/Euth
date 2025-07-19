import cv2
import mediapipe as mp
import time
from collections import deque
import hashlib

class Euth:

    """
    A facial gesture-based authentication system using eye blinks and nose movements.

    This class uses MediaPipe FaceMesh to track facial landmarks and interprets eye blinks
    and nose shakes as password inputs. The authentication succeeds when a predefined gesture
    sequence matches the target password.

    Parameters
    ----------
    blink_threshold : float, optional
        EAR (eye aspect ratio) threshold below which a blink is detected. Default is 0.23.
    blink_cooldown : float, optional
        Minimum time (in seconds) between detected blinks. Default is 0.3.
    auto_cooldown : float, optional
        Interval (in seconds) after which a 'neutral' input is automatically added. Default is 0.6.
    shake_buffer : int, optional
        Number of nose positions to store for shake detection. Default is 10.
    shake_threshold : int, optional
        Pixel distance difference in nose movement to detect a shake. Default is 30.
    shake_cooldown : float, optional
        Minimum time between allowed shake resets. Default is 0.5.
    """

    def __init__(self, blink_threshold=0.23, blink_cooldown=0.3, auto_cooldown=0.6,
                 shake_buffer=10, shake_threshold=30, shake_cooldown=0.5):
        self.BLINK_THRESHOLD = blink_threshold
        self.BLINK_COOLDOWN = blink_cooldown
        self.AUTO_COOLDOWN = auto_cooldown
        self.SHAKE_BUFFER = shake_buffer
        self.SHAKE_THRESHOLD = shake_threshold
        self.CLEAR_COOLDOWN = shake_cooldown

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1)
        self.mp_drawing = mp.solutions.drawing_utils

    def eye_aspect_ratio(self, landmarks, left_indices, right_indices, image_w, image_h):

        """
        Calculate the average eye aspect ratio (EAR) for both eyes.

        EAR is used to determine eye closure (i.e., blinks).

        Parameters
        ----------
        landmarks : List[mediapipe.framework.formats.landmark_pb2.NormalizedLandmark]
            List of facial landmarks from MediaPipe.
        left_indices : List[int]
            Landmark indices for the left eye.
        right_indices : List[int]
            Landmark indices for the right eye.
        image_w : int
            Width of the image.
        image_h : int
            Height of the image.

        Returns
        -------
        float
            Average EAR of both eyes.
        """

        def get_coord(index):
            return int(landmarks[index].x * image_w), int(landmarks[index].y * image_h)

        def distance(p1, p2):
            return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

        left_eye = [get_coord(i) for i in left_indices]
        right_eye = [get_coord(i) for i in right_indices]

        left_ear = (distance(left_eye[1], left_eye[5]) + distance(left_eye[2], left_eye[4])) / \
                   (2.0 * distance(left_eye[0], left_eye[3]))
        right_ear = (distance(right_eye[1], right_eye[5]) + distance(right_eye[2], right_eye[4])) / \
                    (2.0 * distance(right_eye[0], right_eye[3]))

        return (left_ear + right_ear) / 2.0

    def auth(self, password = "", verbose = 2):

        """
        Starts the authentication loop using eye blinks and nose shakes.

        The function reads frames from the webcam and uses facial gestures
        to enter characters. A blink adds 'B', a timeout adds 'N', and a
        horizontal nose shake clears the current attempt. The process ends
        when the input sequence matches the provided password.

        Parameters
        ----------
        password : str, optional
            The SHA-256 hash (hex digest) of the gesture password to match.
            Use 'B' for blink and 'N' for neutral (timeout-based). Default is "".
        verbose : int, optional
            Verbosity level:
            - 0 = silent
            - 1 = shows asterisk (*) for each input and clear messages
            - 2 = prints success messages

        Returns
        -------
        bool
            True if authentication was successful, False otherwise.
        """

        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        NOSE_TIP = 1

        last_blink_time = time.time()
        last_check_time = time.time()
        last_clear_time = time.time()
        nose_positions = deque(maxlen=self.SHAKE_BUFFER)

        cap = cv2.VideoCapture(0)
        time.sleep(0.5)

        attempt = ""

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                image = cv2.flip(frame, 1)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_image)

                image_h, image_w = image.shape[:2]

                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    landmarks = face_landmarks.landmark

                    ear = self.eye_aspect_ratio(landmarks, LEFT_EYE, RIGHT_EYE, image_w, image_h)

                    nose = landmarks[NOSE_TIP]
                    nose_x = int(nose.x * image_w)
                    nose_positions.append(nose_x)

                    current_time = time.time()

                    if (ear < self.BLINK_THRESHOLD and
                            (current_time - last_blink_time) > self.BLINK_COOLDOWN and
                            (current_time - last_clear_time) > self.CLEAR_COOLDOWN):
                        attempt += "B"
                        if verbose >= 1: print("*", end="", flush=True)
                        last_blink_time = current_time
                        last_check_time = current_time

                    elif (current_time - last_check_time >= self.AUTO_COOLDOWN and
                          (current_time - last_clear_time) > self.CLEAR_COOLDOWN):
                        attempt += "N"
                        if verbose >= 1: print("*", end="", flush=True)
                        last_check_time = current_time

                    if len(nose_positions) >= self.SHAKE_BUFFER:
                        movement = max(nose_positions) - min(nose_positions)
                        if movement > self.SHAKE_THRESHOLD and current_time - last_clear_time >= self.CLEAR_COOLDOWN:
                            attempt = ""
                            if verbose >= 1: print(" Cleared")
                            last_clear_time = current_time

                    self.mp_drawing.draw_landmarks(
                        image, face_landmarks, self.mp_face_mesh.FACEMESH_TESSELATION,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                        self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1)
                    )

                hash = hashlib.sha256(attempt.encode()).hexdigest()
                if hash == password:
                    if verbose >= 2: print(" Authenticated")
                    return True

        finally:
            cap.release()
