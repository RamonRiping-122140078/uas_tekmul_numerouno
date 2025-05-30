import cv2
from typing import Optional, List
import math_problem_generator

class GameState:
    """
    Kelas untuk mengelola status permainan, seperti score, timer, dan kemajuan soal.
    
    Attributes:
        current_problem (Optional[str]): Soal matematika saat ini.
        current_answer (Optional[float]): Jawaban benar untuk soal saat ini.
        problems_count (int): Jumlah soal yang telah dikerjakan.
        correct_answers (int): Jumlah jawaban yang benar.
        total_problems (int): Total soal dalam satu permainan.
        score (int): Skor pemain (20 poin per jawaban benar).
        time_per_question (int): Waktu maksimum per soal (detik).
        timer (float): Waktu tersisa untuk soal saat ini.
        last_time (int): Waktu terakhir diukur (tick).
        current_answer_given (Optional[int]): Jawaban yang diberikan pemain.
        feedback_delay (int): Durasi tampilan umpan balik (frame).
        show_feedback (bool): Status apakah umpan balik ditampilkan.
        game_over_played (bool): Status apakah suara akhir sudah dimainkan.
        answer_history (List[bool]): Daftar status jawaban (benar/salah).
    """
    
    def __init__(self, total_problems: int = 5, time_per_question: int = 7):
        """Inisialisasi status permainan dengan nilai awal."""
        self.current_problem: Optional[str] = None
        self.current_answer: Optional[float] = None
        self.problems_count: int = 0
        self.correct_answers: int = 0
        self.total_problems: int = total_problems
        self.score: int = 0
        self.time_per_question: int = time_per_question
        self.timer: float = 0
        self.last_time: int = 0
        self.current_answer_given: Optional[int] = None
        self.feedback_delay: int = 45  # ~1.5 detik pada 30fps
        self.show_feedback: bool = False
        self.game_over_played: bool = False
        self.answer_history: List[bool] = []

    def new_problem(self) -> bool:
        """
        Membuat soal matematika baru jika permainan belum selesai.
        
        Returns:
            bool: True jika soal baru dibuat, False jika permainan selesai.
        """
        if self.problems_count < self.total_problems:
            # Membuat soal baru dan mengatur ulang timer
            self.current_problem, self.current_answer = math_problem_generator.MathProblemGenerator.generate_math_problem()
            self.timer = self.time_per_question
            self.last_time = cv2.getTickCount()
            self.current_answer_given = None
            return True
        return False

    def update_timer(self) -> bool:
        """
        Memperbarui timer dan memeriksa apakah waktu masih tersedia.
        
        Returns:
            bool: True jika waktu masih ada, False jika habis.
        """
        if self.timer > 0:
            # Menghitung waktu yang telah berlalu
            current_time = cv2.getTickCount()
            elapsed = (current_time - self.last_time) / cv2.getTickFrequency()
            self.timer = max(0, self.time_per_question - elapsed)
            return self.timer > 0
        return False

    def check_answer(self, user_answer: int) -> bool:
        """
        Memeriksa apakah jawaban pemain benar dan memperbarui score.
        
        Args:
            user_answer (int): Jawaban yang diberikan pemain.
            
        Returns:
            bool: True jika jawaban benar, False jika salah.
        """
        if self.current_answer is not None:
            # Membandingkan jawaban dengan toleransi untuk hasil float
            if abs(user_answer - self.current_answer) < 0.01:
                self.score += 20
                self.correct_answers += 1
                return True
        return False