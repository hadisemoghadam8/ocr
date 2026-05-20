# C:\Users\ASUS\ocr_project\preprocess\analyzer.py

import cv2
import numpy as np


class ImageAnalyzer:
    """
    Analyzes image characteristics for pipeline routing
    """

    @staticmethod
    def analyze(image: np.ndarray) -> dict:
        """
        Analyze image and return characteristics
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary containing image metrics
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Brightness
        brightness = np.mean(gray)

        # Contrast
        contrast = gray.std()

        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size

        # Noise estimation
        noise = ImageAnalyzer._estimate_noise(gray)

        # Blur detection
        blur_score = ImageAnalyzer._detect_blur(gray)

        # Sharpness
        sharpness = ImageAnalyzer._calculate_sharpness(gray)

        # UI detection
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
        """Estimate image noise level"""
        h, w = gray.shape
        
        if h < 10 or w < 10:
            return 0.0
            
        # Sample center region
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
        """Detect blur using Laplacian variance"""
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        return float(variance)

    @staticmethod
    def _calculate_sharpness(gray: np.ndarray) -> float:
        """Calculate image sharpness"""
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        sharpness = np.mean(gradient_magnitude)
        
        return float(sharpness)

    @staticmethod
    def _detect_ui_elements(gray: np.ndarray) -> float:
        """
        Detect UI elements (buttons, rectangles, etc.)
        Returns score 0-1 indicating likelihood of UI screenshot
        """
        # Detect rectangles
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        if len(contours) == 0:
            return 0.0
        
        # Count rectangular shapes
        rectangles = 0
        total_area = gray.shape[0] * gray.shape[1]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Skip very small contours
            if area < 100:
                continue
                
            # Approximate contour
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            
            # Check if it's rectangular (4 corners)
            if len(approx) == 4:
                rectangles += 1
        
        # Normalize score
        ui_score = min(rectangles / 20.0, 1.0)
        
        return float(ui_score)


# Backward compatibility: keep old function name
def analyze_image(image: np.ndarray) -> dict:
    """
    Legacy function - redirects to ImageAnalyzer.analyze()
    """
    return ImageAnalyzer.analyze(image)
