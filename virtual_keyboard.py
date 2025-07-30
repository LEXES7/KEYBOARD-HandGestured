import cv2
import numpy as np
import math

class VirtualKeyboard:
    def __init__(self):
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['SPACE', 'CLEAR', 'BACKSPACE']
        ]
        self.text = ""
        self.key_size = 120  
        self.key_margin = 10 
        self.pressed_key = None
        self.hover_key = None
        self.hover_start_time = 0
        self.hover_duration = 0.8  
        self.last_press_time = 0
        self.press_cooldown = 0.3  
        
    def calculate_distance(self, point1, point2):
        """Calculate distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def check_pinch(self, hand_positions):
        """Check if thumb and index finger are pinching"""
        thumb_tip = None
        index_tip = None
        
        for pos in hand_positions:
            if pos[0] == 4:  # Thumb tip
                thumb_tip = (pos[1], pos[2])
            elif pos[0] == 8:  # Index finger tip
                index_tip = (pos[1], pos[2])
        
        if thumb_tip and index_tip:
            distance = self.calculate_distance(thumb_tip, index_tip)
            return distance < 50, index_tip  
        return False, None
    
    def draw_keyboard(self, image):
        h, w, _ = image.shape
        
        # Calculate responsive positions
        start_x = w // 20  
        start_y = int(h * 0.55)  
        # Scale key size based on screen width
        self.key_size = max(80, w // 12)  
        
        for row_idx, row in enumerate(self.keys):
            y = start_y + row_idx * (self.key_size + self.key_margin)
            
            if row_idx == 3:  
                self.draw_special_row(image, row, y, w)
            else:
                row_width = len(row) * (self.key_size + self.key_margin)
                x_offset = (w - row_width) // 2
                
                for col_idx, key in enumerate(row):
                    x = x_offset + col_idx * (self.key_size + self.key_margin)
                    
                    if self.pressed_key == key:
                        color = (0, 255, 0)  # Green for pressed
                    elif self.hover_key == key:
                        # Progress color from yellow to red based on hover time
                        import time
                        if hasattr(self, 'hover_start_time') and self.hover_start_time > 0:
                            elapsed = time.time() - self.hover_start_time
                            progress = min(elapsed / self.hover_duration, 1.0)
                            # Yellow to red gradient
                            color = (0, int(255 * (1 - progress)), int(255 * progress))
                        else:
                            color = (0, 255, 255)  # Yellow for hover
                    else:
                        color = (60, 60, 60)  # Darker gray for better contrast
                    
                    # Draw key with rounded corners effect
                    cv2.rectangle(image, (x, y), (x + self.key_size, y + self.key_size), color, -1)
                    cv2.rectangle(image, (x, y), (x + self.key_size, y + self.key_size), (255, 255, 255), 3)
                    
                    # Draw key text with better positioning
                    text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
                    text_x = x + (self.key_size - text_size[0]) // 2
                    text_y = y + (self.key_size + text_size[1]) // 2
                    
                    text_color = (0, 0, 0) if color != (60, 60, 60) else (255, 255, 255)
                    cv2.putText(image, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, text_color, 3)
        
        # Draw text area - larger and more prominent
        text_area_height = int(h * 0.15)
        text_area_y = int(h * 0.05)
        cv2.rectangle(image, (start_x, text_area_y), (w - start_x, text_area_y + text_area_height), (240, 240, 240), -1)
        cv2.rectangle(image, (start_x, text_area_y), (w - start_x, text_area_y + text_area_height), (0, 0, 0), 3)
        
        # Handle long text with scrolling
        display_text = self.text
        max_chars = w // 20  # Responsive character limit
        if len(display_text) > max_chars:
            display_text = "..." + display_text[-(max_chars-3):]
        
        # Better text positioning
        text_y = text_area_y + text_area_height // 2 + 10
        cv2.putText(image, display_text, (start_x + 20, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        
        # Show character count
        char_count_text = f"Characters: {len(self.text)}"
        cv2.putText(image, char_count_text, (w - 300, text_area_y + text_area_height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        # Instructions at top
        instruction_text = "Pinch thumb + index finger to type | Hover to select"
        cv2.putText(image, instruction_text, (start_x, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Show hover progress bar
        if self.hover_key and hasattr(self, 'hover_start_time') and self.hover_start_time > 0:
            import time
            elapsed = time.time() - self.hover_start_time
            progress = min(elapsed / self.hover_duration, 1.0)
            
            # Progress bar
            bar_width = w - 2 * start_x
            progress_width = int(bar_width * progress)
            bar_y = text_area_y + text_area_height + 20
            
            cv2.rectangle(image, (start_x, bar_y), (start_x + progress_width, bar_y + 20), (0, 255, 0), -1)
            cv2.rectangle(image, (start_x, bar_y), (start_x + bar_width, bar_y + 20), (255, 255, 255), 2)
            
            # Hover text
            hover_text = f"Hovering on: {self.hover_key} ({progress*100:.0f}%)"
            cv2.putText(image, hover_text, (start_x, bar_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return image
    
    def draw_special_row(self, image, row, y, screen_width):
        key_widths = {'SPACE': self.key_size * 4, 'CLEAR': self.key_size * 2, 'BACKSPACE': self.key_size * 2}
        
        # Center the special row
        total_width = sum(key_widths[key] for key in row) + self.key_margin * (len(row) - 1)
        start_x = (screen_width - total_width) // 2
        x = start_x
        
        for key in row:
            width = key_widths.get(key, self.key_size)
            
            # Different colors for different states
            if self.pressed_key == key:
                color = (0, 255, 0)  # Green for pressed
            elif self.hover_key == key:
                import time
                if hasattr(self, 'hover_start_time') and self.hover_start_time > 0:
                    elapsed = time.time() - self.hover_start_time
                    progress = min(elapsed / self.hover_duration, 1.0)
                    color = (0, int(255 * (1 - progress)), int(255 * progress))
                else:
                    color = (0, 255, 255)  # Yellow for hover
            else:
                color = (60, 60, 60)  # Darker gray
            
            cv2.rectangle(image, (x, y), (x + width, y + self.key_size), color, -1)
            cv2.rectangle(image, (x, y), (x + width, y + self.key_size), (255, 255, 255), 3)
            
            # Better text positioning for special keys
            text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            text_x = x + (width - text_size[0]) // 2
            text_y = y + (self.key_size + text_size[1]) // 2
            
            text_color = (0, 0, 0) if color != (60, 60, 60) else (255, 255, 255)
            cv2.putText(image, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, text_color, 2)
            
            x += width + self.key_margin
    
    def check_hover_and_pinch(self, hand_positions, image_shape):
        """Main method to check for typing using pinch + hover"""
        import time
        current_time = time.time()
        
        # Check for pinch
        is_pinching, index_pos = self.check_pinch(hand_positions)
        
        if not index_pos:
            self.hover_key = None
            self.hover_start_time = 0
            return None
        
        # Check which key the index finger is over
        current_hover = self.check_key_hover(index_pos, image_shape)
        
        # Handle hover logic
        if current_hover:
            if current_hover == self.hover_key:
                # Still hovering on same key
                if self.hover_start_time == 0:
                    self.hover_start_time = current_time
                elif current_time - self.hover_start_time >= self.hover_duration:
                    # Hover time reached - type if pinching
                    if is_pinching and current_time - self.last_press_time > self.press_cooldown:
                        self.last_press_time = current_time
                        self.hover_start_time = 0  # Reset hover
                        self.pressed_key = current_hover
                        return self.process_key_press(current_hover)
            else:
                # Started hovering on new key
                self.hover_key = current_hover
                self.hover_start_time = current_time
        else:
            # Not hovering on any key
            self.hover_key = None
            self.hover_start_time = 0
        
        self.pressed_key = None
        return None
    
    def check_key_hover(self, finger_pos, image_shape):
        """Check which key the finger is hovering over"""
        h, w, _ = image_shape
        start_y = int(h * 0.55)
        
        for row_idx, row in enumerate(self.keys):
            y = start_y + row_idx * (self.key_size + self.key_margin)
            
            if row_idx == 3:  # Special row
                return self.check_special_row_hover(finger_pos, row, y, w)
            else:
                # Center the row
                row_width = len(row) * (self.key_size + self.key_margin)
                x_offset = (w - row_width) // 2
                
                for col_idx, key in enumerate(row):
                    x = x_offset + col_idx * (self.key_size + self.key_margin)
                    
                    if x < finger_pos[0] < x + self.key_size and y < finger_pos[1] < y + self.key_size:
                        return key
        
        return None
    
    def check_special_row_hover(self, finger_pos, row, y, screen_width):
        key_widths = {'SPACE': self.key_size * 4, 'CLEAR': self.key_size * 2, 'BACKSPACE': self.key_size * 2}
        
        total_width = sum(key_widths[key] for key in row) + self.key_margin * (len(row) - 1)
        start_x = (screen_width - total_width) // 2
        x = start_x
        
        for key in row:
            width = key_widths.get(key, self.key_size)
            
            if x < finger_pos[0] < x + width and y < finger_pos[1] < y + self.key_size:
                return key
            
            x += width + self.key_margin
        
        return None
    
    def process_key_press(self, key):
        """Process the actual key press"""
        if key == 'SPACE':
            self.text += ' '
            return ' '
        elif key == 'CLEAR':
            self.text = ""
            return None
        elif key == 'BACKSPACE':
            if self.text:
                self.text = self.text[:-1]
            return None
        else:
            self.text += key
            return key