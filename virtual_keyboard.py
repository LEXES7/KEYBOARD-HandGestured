import cv2
import numpy as np
import math

class VirtualKeyboard:
    def __init__(self):
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['SPACE', 'CLEAR', 'BACK']
        ]
        self.text = ""
        self.base_key_size = 80
        self.key_margin = 8
        self.pressed_key = None
        self.hover_key = None
        self.hover_start_time = 0
        self.hover_duration = 0.8
        self.last_press_time = 0
        self.press_cooldown = 0.3
        
    def calculate_distance(self, point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def check_pinch(self, hand_positions):
        thumb_tip = None
        index_tip = None
        
        for pos in hand_positions:
            if pos[0] == 4:
                thumb_tip = (pos[1], pos[2])
            elif pos[0] == 8:
                index_tip = (pos[1], pos[2])
        
        if thumb_tip and index_tip:
            distance = self.calculate_distance(thumb_tip, index_tip)
            return distance < 50, index_tip
        return False, None
    
    def draw_keyboard(self, image):
        h, w, _ = image.shape
        
        margin = 20
        available_width = w - 2 * margin
        available_height = int(h * 0.4)
        
        max_row_keys = 10
        self.key_size = min(
            (available_width - (max_row_keys - 1) * self.key_margin) // max_row_keys,
            available_height // 5,
            100
        )
        self.key_size = max(self.key_size, 50)
        
        start_y = h - available_height - margin
        
        for row_idx, row in enumerate(self.keys):
            y = start_y + row_idx * (self.key_size + self.key_margin)
            
            if row_idx == 3:
                self.draw_special_row(image, row, y, w, margin, available_width)
            else:
                row_width = len(row) * self.key_size + (len(row) - 1) * self.key_margin
                start_x = margin + (available_width - row_width) // 2
                
                for col_idx, key in enumerate(row):
                    x = start_x + col_idx * (self.key_size + self.key_margin)
                    
                    if self.pressed_key == key:
                        key_color = (0, 180, 120)
                        border_color = (0, 200, 150)
                        text_color = (255, 255, 255)
                    elif self.hover_key == key:
                        import time
                        if hasattr(self, 'hover_start_time') and self.hover_start_time > 0:
                            elapsed = time.time() - self.hover_start_time
                            progress = min(elapsed / self.hover_duration, 1.0)
                            blue_val = int(255 - progress * 100)
                            green_val = int(200 + progress * 55)
                            key_color = (0, green_val, blue_val)
                            border_color = (0, 220, 255)
                        else:
                            key_color = (0, 200, 255)
                            border_color = (0, 220, 255)
                        text_color = (255, 255, 255)
                    else:
                        key_color = (245, 245, 245)
                        border_color = (180, 180, 180)
                        text_color = (70, 70, 70)
                    
                    cv2.rectangle(image, (x, y), (x + self.key_size, y + self.key_size), key_color, -1)
                    cv2.rectangle(image, (x, y), (x + self.key_size, y + self.key_size), border_color, 2)
                    
                    font_scale = min(1.2, self.key_size / 60)
                    text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
                    text_x = x + (self.key_size - text_size[0]) // 2
                    text_y = y + (self.key_size + text_size[1]) // 2
                    
                    cv2.putText(image, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                               font_scale, text_color, 2)
        
        self.draw_text_area(image, w, h, margin)
        
        if self.hover_key and hasattr(self, 'hover_start_time') and self.hover_start_time > 0:
            self.draw_progress_bar(image, w, h, margin, start_y)
        
        return image
    
    def draw_text_area(self, image, w, h, margin):
        text_area_height = int(h * 0.12)
        text_area_y = margin
        
        cv2.rectangle(image, (margin, text_area_y), (w - margin, text_area_y + text_area_height), 
                     (255, 255, 255), -1)
        cv2.rectangle(image, (margin, text_area_y), (w - margin, text_area_y + text_area_height), 
                     (100, 150, 200), 3)
        
        display_text = self.text
        max_chars = (w - 2 * margin - 40) // 12
        if len(display_text) > max_chars:
            display_text = "..." + display_text[-(max_chars-3):]
        
        text_y = text_area_y + text_area_height // 2 + 8
        cv2.putText(image, display_text, (margin + 20, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                   1.0, (60, 60, 60), 2)
        
        char_text = f"{len(self.text)} chars"
        char_size = cv2.getTextSize(char_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        cv2.putText(image, char_text, (w - margin - char_size[0] - 10, text_area_y + text_area_height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 120), 1)
        
        instruction = "Pinch to Type  |  Hover to Select  |  Press Q to Quit"
        cv2.putText(image, instruction, (margin, text_area_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)
    
    def draw_progress_bar(self, image, w, h, margin, keyboard_y):
        import time
        elapsed = time.time() - self.hover_start_time
        progress = min(elapsed / self.hover_duration, 1.0)
        
        bar_y = keyboard_y - 40
        bar_width = w - 2 * margin
        progress_width = int(bar_width * progress)
        
        cv2.rectangle(image, (margin, bar_y), (margin + bar_width, bar_y + 15), (240, 240, 240), -1)
        
        if progress_width > 0:
            green_val = int(180 + progress * 75)
            cv2.rectangle(image, (margin, bar_y), (margin + progress_width, bar_y + 15), 
                         (0, green_val, 255), -1)
        
        cv2.rectangle(image, (margin, bar_y), (margin + bar_width, bar_y + 15), (150, 150, 150), 1)
        
        progress_text = f"Typing: {self.hover_key} ({progress*100:.0f}%)"
        cv2.putText(image, progress_text, (margin, bar_y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 2)
    
    def draw_special_row(self, image, row, y, screen_width, margin, available_width):
        total_margin = self.key_margin * (len(row) - 1)
        available_for_keys = available_width - total_margin
        
        space_width = int(available_for_keys * 0.5)
        other_width = int(available_for_keys * 0.25)
        
        key_widths = {
            'SPACE': space_width,
            'CLEAR': other_width,
            'BACK': other_width
        }
        
        total_width = sum(key_widths[key] for key in row) + total_margin
        start_x = margin + (available_width - total_width) // 2
        x = start_x
        
        for key in row:
            width = key_widths[key]
            
            if self.pressed_key == key:
                if key == 'SPACE':
                    key_color = (0, 180, 120)
                elif key == 'CLEAR':
                    key_color = (255, 120, 80)
                else:
                    key_color = (255, 160, 0)
                border_color = (0, 200, 150)
                text_color = (255, 255, 255)
            elif self.hover_key == key:
                import time
                if hasattr(self, 'hover_start_time') and self.hover_start_time > 0:
                    elapsed = time.time() - self.hover_start_time
                    progress = min(elapsed / self.hover_duration, 1.0)
                    blue_val = int(255 - progress * 100)
                    green_val = int(200 + progress * 55)
                    key_color = (0, green_val, blue_val)
                    border_color = (0, 220, 255)
                else:
                    key_color = (0, 200, 255)
                    border_color = (0, 220, 255)
                text_color = (255, 255, 255)
            else:
                if key == 'SPACE':
                    key_color = (230, 245, 255)
                    border_color = (100, 150, 200)
                elif key == 'CLEAR':
                    key_color = (255, 240, 235)
                    border_color = (255, 150, 100)
                else:
                    key_color = (255, 250, 230)
                    border_color = (255, 180, 50)
                text_color = (80, 80, 80)
            
            cv2.rectangle(image, (x, y), (x + width, y + self.key_size), key_color, -1)
            cv2.rectangle(image, (x, y), (x + width, y + self.key_size), border_color, 2)
            
            font_scale = min(0.9, width / 80)
            text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
            text_x = x + (width - text_size[0]) // 2
            text_y = y + (self.key_size + text_size[1]) // 2
            
            cv2.putText(image, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, text_color, 2)
            
            x += width + self.key_margin
    
    def check_hover_and_pinch(self, hand_positions, image_shape):
        import time
        current_time = time.time()
        
        is_pinching, index_pos = self.check_pinch(hand_positions)
        
        if not index_pos:
            self.hover_key = None
            self.hover_start_time = 0
            return None
        
        current_hover = self.check_key_hover(index_pos, image_shape)
        
        if current_hover:
            if current_hover == self.hover_key:
                if self.hover_start_time == 0:
                    self.hover_start_time = current_time
                elif current_time - self.hover_start_time >= self.hover_duration:
                    if is_pinching and current_time - self.last_press_time > self.press_cooldown:
                        self.last_press_time = current_time
                        self.hover_start_time = 0
                        self.pressed_key = current_hover
                        return self.process_key_press(current_hover)
            else:
                self.hover_key = current_hover
                self.hover_start_time = current_time
        else:
            self.hover_key = None
            self.hover_start_time = 0
        
        self.pressed_key = None
        return None
    
    def check_key_hover(self, finger_pos, image_shape):
        h, w, _ = image_shape
        margin = 20
        available_height = int(h * 0.4)
        start_y = h - available_height - margin
        
        for row_idx, row in enumerate(self.keys):
            y = start_y + row_idx * (self.key_size + self.key_margin)
            
            if row_idx == 3:
                return self.check_special_row_hover(finger_pos, row, y, w, margin)
            else:
                available_width = w - 2 * margin
                row_width = len(row) * self.key_size + (len(row) - 1) * self.key_margin
                start_x = margin + (available_width - row_width) // 2
                
                for col_idx, key in enumerate(row):
                    x = start_x + col_idx * (self.key_size + self.key_margin)
                    
                    if x < finger_pos[0] < x + self.key_size and y < finger_pos[1] < y + self.key_size:
                        return key
        
        return None
    
    def check_special_row_hover(self, finger_pos, row, y, screen_width, margin):
        available_width = screen_width - 2 * margin
        total_margin = self.key_margin * (len(row) - 1)
        available_for_keys = available_width - total_margin
        
        space_width = int(available_for_keys * 0.5)
        other_width = int(available_for_keys * 0.25)
        
        key_widths = {
            'SPACE': space_width,
            'CLEAR': other_width,
            'BACK': other_width
        }
        
        total_width = sum(key_widths[key] for key in row) + total_margin
        start_x = margin + (available_width - total_width) // 2
        x = start_x
        
        for key in row:
            width = key_widths[key]
            
            if x < finger_pos[0] < x + width and y < finger_pos[1] < y + self.key_size:
                return key
            
            x += width + self.key_margin
        
        return None
    
    def process_key_press(self, key):
        if key == 'SPACE':
            self.text += ' '
            return ' '
        elif key == 'CLEAR':
            self.text = ""
            return None
        elif key == 'BACK':
            if self.text:
                self.text = self.text[:-1]
            return None
        else:
            self.text += key
            return key