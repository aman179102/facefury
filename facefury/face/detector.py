"""Face detection using OpenCV Haar Cascade classifier."""

import cv2
import numpy as np
from typing import Tuple, Optional, List


class FaceDetector:
    """Detects faces in images using OpenCV."""
    
    def __init__(self):
        """Initialize face detector with Haar cascade classifier."""
        # Use OpenCV's built-in Haar cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            raise RuntimeError("Failed to load Haar cascade classifier")
    
    def detect_face(self, image_path: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the primary face in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (x, y, width, height) or None if no face found
        """
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return None
        
        # Return the largest face (most likely the main subject)
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        return tuple(largest_face)
    
    def detect_all_faces(self, image_path: str) -> List[Tuple[int, int, int, int]]:
        """
        Detect all faces in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of (x, y, width, height) tuples
        """
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return [tuple(face) for face in faces]
    
    def has_face(self, image_path: str) -> bool:
        """Check if image contains at least one face."""
        return self.detect_face(image_path) is not None
