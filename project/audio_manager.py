import os
import pygame
import pyttsx3
import threading

class AudioManager:
    """
    Kelas untuk mengelola pemutaran suara, termasuk musik latar dan efek suara.
    
    Attributes:
        bgm_path (str): Lokasi file musik latar.
        win_sound (pygame.mixer.Sound): Efek suara untuk kemenangan.
        lose_sound (pygame.mixer.Sound): Efek suara untuk kekalahan.
    """
    
    def __init__(self, bgm_path: str, win_sound_path: str, lose_sound_path: str):
        """Inisialisasi pengelola suara dengan file audio."""
        pygame.mixer.init()
        self.bgm_path = bgm_path
        self.win_sound = pygame.mixer.Sound(win_sound_path) if os.path.exists(win_sound_path) else None
        self.lose_sound = pygame.mixer.Sound(lose_sound_path) if os.path.exists(lose_sound_path) else None
        if self.win_sound:
            self.win_sound.set_volume(0.5)
        if self.lose_sound:
            self.lose_sound.set_volume(0.5)

    def play_background_music(self):
        """Memutar musik latar secara berulang."""
        try:
            pygame.mixer.music.load(self.bgm_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error memutar musik latar: {e}")

    def stop_background_music(self):
        """Menghentikan musik latar."""
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"Error menghentikan musik latar: {e}")

    def play_game_over_sound(self, score: int):
        """
        Memutar suara akhir berdasarkan score.
        
        Args:
            score (int): Skor akhir pemain.
        """
        try:
            self.stop_background_music()
            if score >= 60 and self.win_sound:
                self.win_sound.play()
            elif self.lose_sound:
                self.lose_sound.play()
        except pygame.error as e:
            print(f"Error memutar suara akhir: {e}")

    def stop_all_sounds(self):
        """Menghentikan semua suara yang sedang diputar."""
        if self.win_sound:
            self.win_sound.stop()
        if self.lose_sound:
            self.lose_sound.stop()
        self.stop_background_music()

    @staticmethod
    def speak(text: str):
        """
        Memutar teks sebagai suara menggunakan text-to-speech di thread terpisah.
        
        Args:
            text (str): Teks yang akan diucapkan.
        """
        def _speak():
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
        
        threading.Thread(target=_speak).start()

    def quit(self):
        """Membersihkan sumber daya pygame mixer."""
        pygame.mixer.quit()