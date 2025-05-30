import mediapipe as mp
import numpy as np
from typing import Optional, Tuple

class FaceDetector:
    """
    Kelas untuk mendeteksi wajah menggunakan MediaPipe untuk penempatan elemen UI.
    
    Attributes:
        face_detection (mp.solutions.face_detection.FaceDetection): Objek MediaPipe untuk deteksi wajah.
    """
    
    def __init__(self):
        """Inisialisasi detektor wajah dengan pengaturan MediaPipe."""
        self.mp_face = mp.solutions.face_detection
        self.face_detection = self.mp_face.FaceDetection(min_detection_confidence=0.5)

    def get_face_position(self, rgb_frame: np.ndarray, width: int, height: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Mendeteksi wajah dan mengembalikan kotak pembatasnya dalam piksel.
        
        Args:
            rgb_frame (np.ndarray): Bingkai dalam format RGB.
            width (int): Lebar bingkai.
            height (int): Tinggi bingkai.
            
        Returns:
            Optional[Tuple[int, int, int, int]]: Kotak pembatas wajah (x, y, lebar, tinggi), None jika tidak terdeteksi.
        """
        results = self.face_detection.process(rgb_frame)
        if results.detections:
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            return (
                int(bbox.xmin * width),
                int(bbox.ymin * height),
                int(bbox.width * width),
                int(bbox.height * height)
            )
        return None

    def close(self):
        """Menutup sumber daya MediaPipe untuk deteksi wajah."""
        self.face_detection.close()