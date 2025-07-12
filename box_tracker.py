import cv2
import numpy as np
from collections import deque


class BoxTracker:
    """Modern box tracking system for clean, futuristic object detection visualization."""
    
    def __init__(self, settings=None):
        self.trail_length = 30
        self.tracks = {}
        self.next_id = 1
        self.smoothing_alpha = 0.8
        
        self.settings = settings or {}
        self.show_trails = self.settings.get('showTrails', True)
        self.color_mode = self.settings.get('colorMode', 'auto')
        self.shader_effects = self.settings.get('shaderEffects', True)
        self.show_coordinates = self.settings.get('showCoordinates', True)
        
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=False
        )
        
        self.min_area = 200
        self.max_tracking_distance = 100
        self.stationary_threshold = 3.0
        self.max_missing_frames = 20
        
    def detect_moving_objects(self, frame):
        """Detect moving objects and return their bounding boxes."""
        fg_mask = self.bg_subtractor.apply(frame)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            
            cx = x + w // 2
            cy = y + h // 2
            
            detections.append({
                'center': (cx, cy),
                'bbox': (x, y, w, h),
                'area': area
            })
        
        return detections
    
    def update_tracks(self, detections, frame_idx):
        """Update tracks with new detections."""
        matched_tracks = set()
        
        for detection in detections:
            center = detection['center']
            best_match = None
            min_distance = float('inf')
            
            for track_id, track in self.tracks.items():
                if track_id in matched_tracks:
                    continue
                    
                if track['missing_frames'] > 0:
                    continue
                    
                last_center = track['centers'][-1]
                distance = np.sqrt((center[0] - last_center[0])**2 + (center[1] - last_center[1])**2)
                
                if distance < min_distance and distance < self.max_tracking_distance:
                    min_distance = distance
                    best_match = track_id
            
            if best_match:
                matched_tracks.add(best_match)
                track = self.tracks[best_match]
                
                last_center = track['centers'][-1]
                smooth_x = int(self.smoothing_alpha * center[0] + (1 - self.smoothing_alpha) * last_center[0])
                smooth_y = int(self.smoothing_alpha * center[1] + (1 - self.smoothing_alpha) * last_center[1])
                
                track['centers'].append((smooth_x, smooth_y))
                track['bboxes'].append(detection['bbox'])
                track['frame_idx'] = frame_idx
                track['missing_frames'] = 0
                
                if len(track['centers']) >= 2:
                    p1 = track['centers'][-2]
                    p2 = track['centers'][-1]
                    velocity = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                    track['velocity'] = velocity
                
            else:
                track_id = f"T{self.next_id:03d}"
                self.next_id += 1
                
                self.tracks[track_id] = {
                    'centers': deque([center], maxlen=self.trail_length),
                    'bboxes': deque([detection['bbox']], maxlen=self.trail_length),
                    'frame_idx': frame_idx,
                    'missing_frames': 0,
                    'velocity': 0.0,
                    'color': self._generate_color(track_id)
                }
        
        for track_id, track in list(self.tracks.items()):
            if track_id not in matched_tracks:
                track['missing_frames'] += 1
                
                if track['missing_frames'] > self.max_missing_frames:
                    del self.tracks[track_id]
    
    def _generate_color(self, track_id):
        """Generate a consistent color for a track ID."""
        return (255, 255, 255)
    
    def _get_negative_color(self, frame, x, y, w=20, h=20):
        """Get negative color with subtle contrast enhancement."""
        if self.color_mode == 'white':
            return (255, 255, 255)
        elif self.color_mode == 'black':
            return (0, 0, 0)
        elif self.color_mode == 'blue':
            return (255, 180, 80)
        elif self.color_mode == 'green':
            return (0, 255, 0)
        elif self.color_mode == 'cyan':
            return (255, 255, 0)
        elif self.color_mode == 'purple':
            return (255, 0, 255)
        elif self.color_mode == 'orange':
            return (0, 165, 255)
        
        height, width = frame.shape[:2]
        
        x1 = max(0, x - w//2)
        y1 = max(0, y - h//2)
        x2 = min(width, x + w//2)
        y2 = min(height, y + h//2)
        
        sample_points = [
            (x1, y1), (x2, y1), (x1, y2), (x2, y2),
            (x, y1), (x, y2), (x1, y), (x2, y),
            (x, y)
        ]
        
        total_b, total_g, total_r = 0, 0, 0
        valid_samples = 0
        
        for sx, sy in sample_points:
            if 0 <= sx < width and 0 <= sy < height:
                b, g, r = frame[sy, sx]
                total_b += int(b)
                total_g += int(g)
                total_r += int(r)
                valid_samples += 1
        
        if valid_samples == 0:
            return (200, 200, 200)
        
        avg_b = total_b // valid_samples
        avg_g = total_g // valid_samples
        avg_r = total_r // valid_samples
        
        neg_b = 255 - avg_b
        neg_g = 255 - avg_g
        neg_r = 255 - avg_r
        
        contrast = abs(neg_b - avg_b) + abs(neg_g - avg_g) + abs(neg_r - avg_r)
        
        if contrast > 120:
            enhanced_b = min(255, int(neg_b * 1.05))
            enhanced_g = int(neg_g * 0.95)
            enhanced_r = int(neg_r * 0.9)
            
            return (enhanced_b, enhanced_g, enhanced_r)
        
        else:
            brightness = (avg_b + avg_g + avg_r) / 3
            
            if brightness < 128:
                return (220, 215, 210)
            else:
                return (60, 55, 50)
    
    def draw_tracks(self, frame):
        """Draw tracking visualization on frame."""
        result = frame.copy()
        
        shader_layer = np.zeros_like(frame) if self.shader_effects else None
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.35
        text_thickness = 1
        line_thickness = 2 if self.shader_effects else 1
        
        for track_id, track in self.tracks.items():
            if track['missing_frames'] > 0:
                continue
                
            centers = list(track['centers'])
            bboxes = list(track['bboxes'])
            
            if len(centers) == 0:
                continue
            
            current_center = centers[-1]
            
            if len(bboxes) > 0:
                x, y, w, h = bboxes[-1]
                box_color = self._get_negative_color(result, x + w//2, y + h//2, w, h)
                
                if self.shader_effects:
                    cv2.rectangle(shader_layer, (x-2, y-2), (x + w + 2, y + h + 2), box_color, 3, cv2.LINE_AA)
                    corner_size = min(w, h) // 6
                    corner_thickness = 3
                    cv2.line(shader_layer, (x, y), (x + corner_size, y), box_color, corner_thickness, cv2.LINE_AA)
                    cv2.line(shader_layer, (x, y), (x, y + corner_size), box_color, corner_thickness, cv2.LINE_AA)
                    cv2.line(shader_layer, (x + w, y), (x + w - corner_size, y), box_color, corner_thickness, cv2.LINE_AA)
                    cv2.line(shader_layer, (x + w, y), (x + w, y + corner_size), box_color, corner_thickness, cv2.LINE_AA)
                    cv2.line(shader_layer, (x, y + h), (x + corner_size, y + h), box_color, corner_thickness, cv2.LINE_AA)
                    cv2.line(shader_layer, (x, y + h), (x, y + h - corner_size), box_color, corner_thickness, cv2.LINE_AA)
                    cv2.line(shader_layer, (x + w, y + h), (x + w - corner_size, y + h), box_color, corner_thickness, cv2.LINE_AA)
                    cv2.line(shader_layer, (x + w, y + h), (x + w, y + h - corner_size), box_color, corner_thickness, cv2.LINE_AA)
                
                cv2.rectangle(result, (x, y), (x + w, y + h), box_color, line_thickness, cv2.LINE_AA)
            
            if self.show_trails and len(centers) > 1:
                for i in range(1, len(centers)):
                    trail_center = centers[i]
                    trail_color = self._get_negative_color(result, trail_center[0], trail_center[1])
                    
                    alpha = (i / len(centers)) * 0.6 + 0.3
                    faded_color = tuple(int(c * alpha) for c in trail_color)
                    
                    cv2.line(result, centers[i-1], centers[i], faded_color, line_thickness, cv2.LINE_AA)
            
            crosshair_color = self._get_negative_color(result, current_center[0], current_center[1])
            crosshair_size = 8 if self.shader_effects else 6
            
            if self.shader_effects:
                cv2.drawMarker(shader_layer, current_center, crosshair_color, cv2.MARKER_CROSS, crosshair_size + 2, 3, cv2.LINE_AA)
            
            cv2.drawMarker(result, current_center, crosshair_color, cv2.MARKER_CROSS, crosshair_size, line_thickness, cv2.LINE_AA)
            
            if self.show_coordinates:
                coord_text = f"({current_center[0]},{current_center[1]})"
                text_size = cv2.getTextSize(coord_text, font, font_scale, text_thickness)[0]
                
                text_x = current_center[0] + 8
                text_y = current_center[1] - 8
                
                if text_x + text_size[0] > frame.shape[1]:
                    text_x = current_center[0] - text_size[0] - 8
                if text_y - text_size[1] < 0:
                    text_y = current_center[1] + text_size[1] + 8
                
                text_color = self._get_negative_color(result, text_x + text_size[0]//2, text_y - text_size[1]//2)
                
                cv2.putText(result, coord_text, (text_x, text_y), 
                           font, font_scale, text_color, text_thickness, cv2.LINE_AA)
                
                id_text = track_id[-3:]
                id_color = self._get_negative_color(result, text_x + text_size[0]//2, text_y + 15)
                cv2.putText(result, id_text, (text_x, text_y + 15), 
                           font, font_scale * 0.7, id_color, text_thickness, cv2.LINE_AA)
        
        if self.shader_effects and shader_layer is not None:
            glow_layer = cv2.GaussianBlur(shader_layer, (15, 15), 0)
            
            result = cv2.addWeighted(result, 1.0, glow_layer, 0.4, 0)
            
            result = cv2.add(result, shader_layer)
        
        return result
    
    def process_frame(self, frame, frame_idx):
        """Process a single frame and return visualization."""
        detections = self.detect_moving_objects(frame)
        self.update_tracks(detections, frame_idx)
        return self.draw_tracks(frame) 