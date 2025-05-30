import cv2
import numpy as np
from typing import Optional, Tuple, List
import game_state

class UIRenderer:
    """
    Kelas untuk merender elemen antarmuka pengguna seperti tombol, teks, dan indikator kemajuan.
    
    Attributes:
        logo (np.ndarray): Gambar logo.
        start_button (np.ndarray): Gambar tombol mulai.
        tryagain_button (np.ndarray): Gambar tombol coba lagi.
        bgcard (np.ndarray): Gambar latar belakang untuk soal.
        font (int): Jenis font untuk teks.
    """
    
    def __init__(self, logo: np.ndarray, start_button: np.ndarray, tryagain_button: np.ndarray, bgcard: np.ndarray):
        """Inisialisasi perender UI dengan gambar aset."""
        self.logo = logo
        self.start_button = start_button
        self.tryagain_button = tryagain_button
        self.bgcard = bgcard
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    @staticmethod
    def overlay_image(background: np.ndarray, overlay: np.ndarray, position: Tuple[int, int]) -> np.ndarray:
        """
        Menumpuk gambar di atas latar belakang dengan blending alpha.
        
        Args:
            background (np.ndarray): Gambar latar belakang.
            overlay (np.ndarray): Gambar yang akan ditumpuk.
            position (Tuple[int, int]): Posisi tumpukan (y, x).
            
        Returns:
            np.ndarray: Latar belakang dengan gambar yang ditumpuk.
        """
        h, w = overlay.shape[:2]
        y, x = position
        
        if overlay.shape[2] == 4:  # Menangani kanal alpha
            overlay_rgb = overlay[:,:,:3]
            alpha = overlay[:,:,3] / 255.0
            alpha_3d = np.stack([alpha, alpha, alpha], axis=2)
            roi = background[y:y+h, x:x+w]
            result = (overlay_rgb * alpha_3d + roi * (1 - alpha_3d)).astype(np.uint8)
            background[y:y+h, x:x+w] = result
        else:
            background[y:y+h, x:x+w] = overlay
        return background

    def draw_main_menu(self, frame: np.ndarray, width: int, height: int) -> Tuple[int, int]:
        """
        Menggambar menu utama dengan logo dan start_button.
        
        Args:
            frame (np.ndarray): Bingkai untuk menggambar.
            width (int): Lebar bingkai.
            height (int): Tinggi bingkai.
            
        Returns:
            Tuple[int, int]: Posisi start_button (x, y).
        """
        # Menempatkan logo di tengah atas
        logo_x = (width - self.logo.shape[1]) // 2
        logo_y = 50
        button_x = (width - self.start_button.shape[1]) // 2
        button_y = logo_y + self.logo.shape[0] + 20
        
        frame = self.overlay_image(frame, self.logo, (logo_y, logo_x))
        frame = self.overlay_image(frame, self.start_button, (button_y, button_x))
        return button_x, button_y

    def draw_game_ui(self, frame: np.ndarray, game_state: game_state.GameState, width: int, height: int, 
                    face_pos: Optional[Tuple[int, int, int, int]], total_fingers: int, 
                    answer_feedback: str, answer_display_time: int):
        """
        Menggambar antarmuka permainan, termasuk kartu soal, timer, score, dan answer_feedback.
        
        Args:
            frame (np.ndarray): Bingkai untuk menggambar.
            game_state (GameState): Status permainan saat ini.
            width (int): Lebar bingkai.
            height (int): Tinggi bingkai.
            face_pos (Optional[Tuple[int, int, int, int]]): Posisi wajah (x, y, lebar, tinggi).
            total_fingers (int): Jumlah jari yang diangkat.
            answer_feedback (str): Teks umpan balik (misalnya, "Benar! +20").
            answer_display_time (int): Sisa waktu tampilan umpan balik.
        """
        # Menggambar bgcard di atas wajah
        if face_pos:
            face_x, face_y, face_w, face_h = face_pos
            bgcard_x = face_x - (self.bgcard.shape[1] - face_w) // 2
            bgcard_y = max(0, face_y - self.bgcard.shape[0] - 20)
            bgcard_x = max(0, min(bgcard_x, width - self.bgcard.shape[1]))
            bgcard_y = max(0, min(bgcard_y, height - self.bgcard.shape[0]))
            frame = self.overlay_image(frame, self.bgcard, (bgcard_y, bgcard_x))
            
            # Menggambar soal matematika
            if game_state.current_problem:
                text = game_state.current_problem
                text_width, text_height = cv2.getTextSize(text, self.font, 1.0, 2)[0]
                text_x = bgcard_x + (self.bgcard.shape[1] - text_width) // 2
                text_y = bgcard_y + (self.bgcard.shape[0] + text_height) // 2
                cv2.putText(frame, text, (text_x, text_y), self.font, 1.0, (255, 255, 255), 3)
                cv2.putText(frame, text, (text_x, text_y), self.font, 1.0, (0, 0, 0), 2)

        # Menggambar timer dan score
        timer_text = f"Waktu: {int(game_state.timer)}s"
        cv2.putText(frame, timer_text, (width - 150, 30), self.font, 0.7, 
                   (0, 0, 255) if game_state.timer < 2 else (255, 255, 255), 2)
        score_text = f"Score: {game_state.score}"
        cv2.putText(frame, score_text, (width - 150, 60), self.font, 0.7, (255, 255, 255), 2)

        # Menggambar jawaban saat ini
        if total_fingers is not None:
            cv2.putText(frame, f"Jawaban: {total_fingers}", (10, 110), self.font, 1, (255, 255, 255), 2)

        # Menggambar indikator kemajuan soal
        self.draw_question_progress(frame, game_state.total_problems, game_state.problems_count, 
                                  game_state.answer_history, width)

        # Menggambar answer_feedback terakhir
        if answer_display_time > 0 and answer_feedback:
            feedback_color = (0, 255, 0) if "Benar" in answer_feedback else (0, 0, 255)
            feedback_pos = (width // 2 - 60, height // 2)
            cv2.putText(frame, answer_feedback, feedback_pos, self.font, 1, (0, 0, 0), 3)
            cv2.putText(frame, answer_feedback, feedback_pos, self.font, 1, feedback_color, 2)

    @staticmethod
    def draw_question_progress(frame: np.ndarray, total_questions: int, current_question: int, 
                             answers: List[bool], width: int):
        """
        Menggambar indikator kemajuan soal berupa lingkaran dan garis penghubung.
        
        Args:
            frame (np.ndarray): Bingkai untuk menggambar.
            total_questions (int): Jumlah total soal.
            current_question (int): Nomor soal saat ini.
            answers (List[bool]): Daftar answer_history (benar/salah).
            width (int): Lebar bingkai.
        """
        CIRCLE_RADIUS = 8
        LINE_LENGTH = 30
        SPACING = 45
        Y_POSITION = 30
        
        total_width = SPACING * (total_questions - 1)
        start_x = (width - total_width) // 2
        
        # Menggambar garis penghubung
        for i in range(total_questions - 1):
            x1 = start_x + (i * SPACING) + CIRCLE_RADIUS
            x2 = x1 + LINE_LENGTH
            line_color = (150, 150, 150) if i >= len(answers) else (0, 255, 0) if answers[i] else (0, 0, 255)
            cv2.line(frame, (x1, Y_POSITION), (x2, Y_POSITION), line_color, 2)
        
        # Menggambar lingkaran untuk setiap soal
        for i in range(total_questions):
            center_x = start_x + (i * SPACING)
            center = (center_x, Y_POSITION)
            if i == current_question:
                cv2.circle(frame, center, CIRCLE_RADIUS + 2, (0, 255, 255), -1)
                cv2.circle(frame, center, CIRCLE_RADIUS + 2, (255, 255, 255), 2)
            elif i < len(answers):
                color = (0, 255, 0) if answers[i] else (0, 0, 255)
                cv2.circle(frame, center, CIRCLE_RADIUS, color, -1)
            else:
                cv2.circle(frame, center, CIRCLE_RADIUS, (150, 150, 150), 2)

    def draw_game_over(self, frame: np.ndarray, game_state: game_state.GameState, width: int, height: int) -> Tuple[int, int]:
        """
        Menggambar layar akhir permainan dengan score akhir dan tryagain_button.
        
        Args:
            frame (np.ndarray): Bingkai untuk menggambar.
            game_state (GameState): Status permainan.
            width (int): Lebar bingkai.
            height (int): Tinggi bingkai.
            
        Returns:
            Tuple[int, int]: Posisi tryagain_button (x, y).
        """
        # Membuat lapisan overlay untuk menggelapkan latar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
        frame[:] = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Mengatur posisi teks
        y_start = height // 4
        y_spacing = 50  # Jarak antar teks untuk pemisahan yang lebih baik
        messages = [
            ("Permainan Selesai!", 2.0, (0, 255, 0)),
            (f"Score Akhir: {game_state.score}/100", 1.8, (0, 255, 0))
        ]
        
        # Menggambar teks pesan
        for i, (msg, scale, color) in enumerate(messages):
            text_size = cv2.getTextSize(msg, self.font, scale, 3)[0]
            text_x = (width - text_size[0]) // 2
            text_y = y_start + i * y_spacing
            cv2.putText(frame, msg, (text_x, text_y), self.font, scale, (0, 0, 0), 4)
            cv2.putText(frame, msg, (text_x, text_y), self.font, scale, color, 2)
        
        # Menggambar tryagain_button
        tryagain_x = (width - self.tryagain_button.shape[1]) // 2
        tryagain_y = y_start + (len(messages) * y_spacing) + 20
        frame = self.overlay_image(frame, self.tryagain_button, (tryagain_y, tryagain_x))
        
        # Menggambar teks keluar
        quit_text = "Tekan 'Q' untuk keluar"
        text_size = cv2.getTextSize(quit_text, self.font, 1.0, 2)[0]
        text_x = (width - text_size[0]) // 2
        text_y = tryagain_y + self.tryagain_button.shape[0] + 20
        text_y = min(text_y, height - text_size[1] - 10)
        cv2.putText(frame, quit_text, (text_x, text_y), self.font, 1.0, (0, 0, 0), 3)
        cv2.putText(frame, quit_text, (text_x, text_y), self.font, 1.0, (255, 255, 255), 2)
        
        return tryagain_x, tryagain_y