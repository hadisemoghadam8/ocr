
import cv2
import numpy as np


class ImageAnalyzer:
    """
    Extract image metrics to guide preprocessing pipeline selection.
    """

    @staticmethod
    def analyze(image: np.ndarray) -> dict:
        """
        Compute key characteristics of the input image.

        Args:
            image: Input image in BGR format.

        Returns:
            Dictionary with brightness, contrast, edge density, noise, blur, sharpness, and UI score.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        brightness = np.mean(gray)
        contrast = gray.std()

        # Edge density as a proxy for text/content complexity
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        noise = ImageAnalyzer._estimate_noise(gray)
        blur_score = ImageAnalyzer._detect_blur(gray)
        sharpness = ImageAnalyzer._calculate_sharpness(gray)
        ui_score = ImageAnalyzer._detect_ui_elements(gray)

        return {
            "brightness": float(brightness),
            "contrast": float(contrast),
            "edge_density": float(edge_density),
            "noise": float(noise),
            "blur_score": float(blur_score),
            "sharpness": float(sharpness),
            "ui_score": float(ui_score)
        }

    @staticmethod
    def _estimate_noise(gray: np.ndarray) -> float:
        """
        Estimate noise level by measuring std deviation in the image center.
        """
        h, w = gray.shape
        
        if h < 10 or w < 10:
            return 0.0
            
        # Sample a central region to avoid border artifacts
        center_h = h // 2
        center_w = w // 2
        sample_size = min(50, h // 4, w // 4)
        
        roi = gray[
            center_h - sample_size:center_h + sample_size,
            center_w - sample_size:center_w + sample_size
        ]
        
        if roi.size == 0:
            return 0.0
            
        return float(np.std(roi))

    @staticmethod
    def _detect_blur(gray: np.ndarray) -> float:
        """
        Detect blur using Laplacian variance (higher = sharper).
        """
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(laplacian.var())

    @staticmethod
    def _calculate_sharpness(gray: np.ndarray) -> float:
        """
        Calculate sharpness based on Sobel gradient magnitude.
        """
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        return float(np.mean(gradient_magnitude))

    @staticmethod
    def _detect_ui_elements(gray: np.ndarray) -> float:
        """
        Estimate likelihood of UI/screenshot content based on rectangular shape density.
        
        Returns:
            Score between 0 and 1 (higher = more likely a UI screenshot).
        """
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return 0.0
        
        rectangles = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Skip tiny contours
            if area < 100:
                continue
                
            # Check for 4-corner shapes (rectangles)
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            
            if len(approx) == 4:
                rectangles += 1
        
        # Normalize: 20+ rectangles = strong UI signal
        return float(min(rectangles / 20.0, 1.0))


# Legacy support for older imports
def analyze_image(image: np.ndarray) -> dict:
    """
    Legacy wrapper for ImageAnalyzer.analyze().
    """
    return ImageAnalyzer.analyze(image)