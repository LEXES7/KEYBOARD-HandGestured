import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, static_mode=False, max_hands=1, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_mode,
            max_num_hands=max_hands,  
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, image, draw=True):
        h, w, _ = image.shape
        if w > 1280:  
            scale = 1280 / w
            new_w, new_h = int(w * scale), int(h * scale)
            image = cv2.resize(image, (new_w, new_h))
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False  
        self.results = self.hands.process(image_rgb)
        image_rgb.flags.writeable = True

        if draw and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                )

        return image

    def get_hand_positions(self, image):
        hand_positions = []
        if self.results and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                for id, landmark in enumerate(hand_landmarks.landmark):
                    h, w, _ = image.shape
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    hand_positions.append((id, cx, cy))
        return hand_positions
    
    def get_finger_positions(self, image):
        """Get specific finger tip positions"""
        finger_positions = {}
        if self.results and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                h, w, _ = image.shape
                
                landmarks = {
                    'thumb_tip': 4,
                    'index_tip': 8,
                    'middle_tip': 12,
                    'ring_tip': 16,
                    'pinky_tip': 20
                }
                
                for finger, landmark_id in landmarks.items():
                    landmark = hand_landmarks.landmark[landmark_id]
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    finger_positions[finger] = (cx, cy)
        
        return finger_positions