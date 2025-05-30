import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple

class HandDetector:
    """
    Kelas untuk mendeteksi tangan dan menghitung jari yang diangkat menggunakan MediaPipe.
    
    Attributes:
        JEMPOL (List[int]): Indeks landmark untuk jempol.
        TELUNJUK (List[int]): Indeks landmark untuk telunjuk.
        JARI_TENGAH (List[int]): Indeks landmark untuk jari tengah.
        JARI_MANIS (List[int]): Indeks landmark untuk jari manis.
        JARI_KELINGKING (List[int]): Indeks landmark untuk kelingking.
        hands (mp.solutions.hands.Hands): Objek MediaPipe untuk deteksi tangan.
        mp_drawing (mp.solutions.drawing_utils): Utilitas untuk menggambar landmark.
        mp_drawing_styles (mp.solutions.drawing_styles): Gaya visual untuk landmark.
    """
    
    JEMPOL = [1, 2, 3, 4]
    TELUNJUK = [5, 6, 7, 8]
    JARI_TENGAH = [9, 10, 11, 12]
    JARI_MANIS = [13, 14, 15, 16]
    JARI_KELINGKING = [17, 18, 19, 20]

    def __init__(self):
        """Inisialisasi detektor tangan dengan pengaturan MediaPipe."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def detect_finger_number(self, hand_landmarks, handedness: str) -> int:
        """
        Menghitung jumlah jari yang diangkat pada satu tangan.
        
        Args:
            hand_landmarks: Landmark tangan dari MediaPipe.
            handedness (str): Sisi tangan ('Left' atau 'Right').
            
        Returns:
            int: Jumlah jari yang diangkat.
        """
        fingers = []
        
        # Mendeteksi jempol
        thumb_tip = hand_landmarks.landmark[self.JEMPOL[-1]]
        thumb_ip = hand_landmarks.landmark[self.JEMPOL[2]]
        fingers.append(thumb_tip.x < thumb_ip.x if handedness == 'Right' else thumb_tip.x > thumb_ip.x)
        
        # Mendeteksi jari lainnya
        for finger in [self.TELUNJUK, self.JARI_TENGAH, self.JARI_MANIS, self.JARI_KELINGKING]:
            tip = hand_landmarks.landmark[finger[-1]]
            pip = hand_landmarks.landmark[finger[-2]]
            dip = hand_landmarks.landmark[finger[-3]]
            fingers.append(tip.y < pip.y and tip.y < dip.y)
        
        return sum(fingers)

    def combine_hand_numbers(self, left_count: int, right_count: int) -> int:
        """
        Menggabungkan jumlah jari dari kedua tangan untuk menghasilkan angka 0-10.
        
        Args:
            left_count (int): Jumlah jari tangan kiri.
            right_count (int): Jumlah jari tangan kanan.
            
        Returns:
            int: Total jari yang diangkat (maksimum 10).
        """
        if left_count == 0:
            return right_count
        if right_count == 0:
            return left_count
        if left_count == 5:
            return min(10, 5 + right_count)
        return min(10, left_count + right_count)

    def process_hands(self, frame: np.ndarray, rgb_frame: np.ndarray) -> Tuple[int, int, int]:
        """
        Memproses landmark tangan dan mengembalikan jumlah jari yang diangkat.
        
        Args:
            frame (np.ndarray): Bingkai gambar untuk menggambar landmark.
            rgb_frame (np.ndarray): Bingkai dalam format RGB untuk pemrosesan.
            
        Returns:
            Tuple[int, int, int]: Jumlah jari kiri, kanan, dan total.
        """
        left_count, right_count = 0, 0
        total_fingers = 0
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness = results.multi_handedness[idx].classification[0].label
                count = self.detect_finger_number(hand_landmarks, handedness)
                
                # Menggambar landmark tangan dengan gaya berwarna
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Memperbarui jumlah jari
                if handedness == 'Left':
                    left_count = count
                else:
                    right_count = count
                
                # Menampilkan jumlah jari per tangan
                cv2.putText(frame, f"{handedness}: {count}", 
                           (10, 50 + idx * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                           (255, 255, 255), 2)
            
            total_fingers = self.combine_hand_numbers(left_count, right_count)
        
        return left_count, right_count, total_fingers

    def check_button_interaction(self, hand_landmarks, button_pos: Tuple[int, int], 
                              button_size: Tuple[int, int], width: int, height: int) -> bool:
        """
        Memeriksa apakah tangan berinteraksi dengan tombol.
        
        Args:
            hand_landmarks: Landmark tangan dari MediaPipe.
            button_pos (Tuple[int, int]): Posisi tombol (x, y).
            button_size (Tuple[int, int]): Ukuran tombol (lebar, tinggi).
            width (int): Lebar bingkai.
            height (int): Tinggi bingkai.
            
        Returns:
            bool: True jika tangan berada di area tombol, False jika tidak.
        """
        if hand_landmarks:
            index_finger = hand_landmarks.landmark[8]
            x, y = int(index_finger.x * width), int(index_finger.y * height)
            button_x, button_y = button_pos
            button_w, button_h = button_size
            return button_x < x < button_x + button_w and button_y < y < button_y + button_h
        return False

    def close(self):
        """Menutup sumber daya MediaPipe untuk tangan."""
        self.hands.close()