import cv2
from hand_detector import HandDetector
from virtual_keyboard import VirtualKeyboard
import time

def main():
    print("Initializing camera...")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Trying camera 1...")
        cap = cv2.VideoCapture(1)
        
    if not cap.isOpened():
        print("No camera available!")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    print("Camera opened successfully!")
    
    detector = HandDetector(detection_confidence=0.8, tracking_confidence=0.8, max_hands=1)
    keyboard = VirtualKeyboard()
    
    frame_count = 0
    fps_start_time = time.time()
    fps = 0
    
    print("Virtual Keyboard started!")
    print("Instructions:")
    print("1. Hover your index finger over a key")
    print("2. Pinch thumb and index finger together to type")
    print("3. Keys are larger and more responsive now!")
    print("4. Press 'q' to quit")
    
    while True:
        ret, img = cap.read()
        
        if not ret or img is None:
            continue
        
        frame_count += 1
        
        # Calculate FPS
        if frame_count % 30 == 0:
            fps_end_time = time.time()
            fps = 30 / (fps_end_time - fps_start_time)
            fps_start_time = fps_end_time
        
        try:
            img = cv2.flip(img, 1)  # Mirror effect
            
            # Detect hands with optimized settings
            img = detector.find_hands(img, draw=True)
            hand_positions = detector.get_hand_positions(img)
            finger_positions = detector.get_finger_positions(img)
            
            img = keyboard.draw_keyboard(img)
            
            if finger_positions:
                if 'thumb_tip' in finger_positions:
                    thumb_pos = finger_positions['thumb_tip']
                    cv2.circle(img, thumb_pos, 15, (255, 0, 0), cv2.FILLED)
                    cv2.circle(img, thumb_pos, 20, (255, 255, 255), 2)
                
                if 'index_tip' in finger_positions:
                    index_pos = finger_positions['index_tip']
                    cv2.circle(img, index_pos, 15, (0, 255, 0), cv2.FILLED)
                    cv2.circle(img, index_pos, 20, (255, 255, 255), 2)
                
                # Draw connection line when close
                if 'thumb_tip' in finger_positions and 'index_tip' in finger_positions:
                    thumb_pos = finger_positions['thumb_tip']
                    index_pos = finger_positions['index_tip']
                    distance = ((thumb_pos[0] - index_pos[0])**2 + (thumb_pos[1] - index_pos[1])**2)**0.5
                    
                    if distance < 100:  # Show connection when fingers are close
                        color = (0, 255, 0) if distance < 50 else (0, 255, 255)
                        cv2.line(img, thumb_pos, index_pos, color, 3)
                        # Show distance
                        mid_point = ((thumb_pos[0] + index_pos[0])//2, (thumb_pos[1] + index_pos[1])//2)
                        cv2.putText(img, f"{int(distance)}", mid_point, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Check for typing
            if hand_positions:
                typed_key = keyboard.check_hover_and_pinch(hand_positions, img.shape)
                if typed_key:
                    print(f"Typed: {typed_key}")
            
            # Show FPS and performance info
            cv2.putText(img, f"FPS: {fps:.1f}", (10, img.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.putText(img, f"Frame: {frame_count}", (10, img.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show window in fullscreen for better visibility
            cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_NORMAL)
            cv2.imshow("Virtual Keyboard", img)
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            continue
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('f'):  # Toggle fullscreen
            cv2.setWindowProperty("Virtual Keyboard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        elif key == ord('w'):  # Windowed mode
            cv2.setWindowProperty("Virtual Keyboard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    
    cap.release()
    cv2.destroyAllWindows()
    print("Virtual Keyboard closed.")

if __name__ == "__main__":
    main()