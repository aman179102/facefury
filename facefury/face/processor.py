"""Face image processing using Pillow."""

from PIL import Image, ImageDraw, ImageFilter
import io
from typing import Optional, Tuple
from .detector import FaceDetector


class FaceProcessor:
    """Process face images for use as game sprites."""
    
    DEFAULT_SIZE = (128, 128)
    
    def __init__(self, size: Tuple[int, int] = DEFAULT_SIZE):
        """
        Initialize face processor.
        
        Args:
            size: Target size for output images (width, height)
        """
        self.size = size
        self.detector = FaceDetector()
    
    def process_image(self, image_path: str, circular_crop: bool = True) -> Optional[Image.Image]:
        """
        Process an image to extract and format the face.
        
        Args:
            image_path: Path to source image
            circular_crop: Whether to apply circular mask
            
        Returns:
            Processed PIL Image or None if no face detected
        """
        # Detect face
        face_rect = self.detector.detect_face(image_path)
        if face_rect is None:
            return None
        
        # Load image
        img = Image.open(image_path).convert("RGBA")
        
        # Extract face region with some padding
        x, y, w, h = face_rect
        padding = int(min(w, h) * 0.2)  # 20% padding
        
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img.width, x + w + padding)
        y2 = min(img.height, y + h + padding)
        
        # Crop face
        face_img = img.crop((x1, y1, x2, y2))
        
        # Resize to target size
        face_img = face_img.resize(self.size, Image.Resampling.LANCZOS)
        
        if circular_crop:
            face_img = self._apply_circular_mask(face_img)
        
        return face_img
    
    def _apply_circular_mask(self, img: Image.Image) -> Image.Image:
        """
        Apply circular mask to image.
        
        Args:
            img: Input PIL Image
            
        Returns:
            Circular masked image
        """
        # Create circular mask
        mask = Image.new("L", self.size, 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw circle
        draw.ellipse((0, 0, self.size[0], self.size[1]), fill=255)
        
        # Apply mask
        output = Image.new("RGBA", self.size, (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        # Add slight border
        border = Image.new("RGBA", self.size, (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border)
        border_draw.ellipse((0, 0, self.size[0]-1, self.size[1]-1), 
                           outline=(255, 255, 255, 200), width=3)
        
        output = Image.alpha_composite(output, border)
        
        return output
    
    def process_to_sprite(self, image_path: str, 
                         output_path: Optional[str] = None,
                         circular_crop: bool = True) -> Optional[str]:
        """
        Process image and save as sprite.
        
        Args:
            image_path: Path to source image
            output_path: Path to save output (optional)
            circular_crop: Whether to apply circular mask
            
        Returns:
            Path to saved sprite or None if failed
        """
        processed = self.process_image(image_path, circular_crop)
        if processed is None:
            return None
        
        if output_path:
            processed.save(output_path, "PNG")
            return output_path
        
        return None
    
    def create_animated_sprite(self, image_path: str, 
                               num_frames: int = 2) -> Optional[list]:
        """
        Create animated sprite frames from face.
        
        Args:
            image_path: Path to source image
            num_frames: Number of animation frames
            
        Returns:
            List of PIL Images for animation frames
        """
        base_img = self.process_image(image_path, circular_crop=True)
        if base_img is None:
            return None
        
        frames = []
        for i in range(num_frames):
            # Create slight variations for animation
            offset = (i - num_frames // 2) * 3
            frame = Image.new("RGBA", self.size, (0, 0, 0, 0))
            frame.paste(base_img, (offset, 0))
            frames.append(frame)
        
        return frames
    
    def resize_sprite(self, image: Image.Image, 
                     new_size: Tuple[int, int]) -> Image.Image:
        """Resize sprite to new dimensions."""
        return image.resize(new_size, Image.Resampling.LANCZOS)
