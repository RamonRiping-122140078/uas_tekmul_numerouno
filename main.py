# 🧮 Interactive Maths
# Game Matematika Sederhana dengan Hand Number Detection

# Import library yang dibutuhkan
import cv2
import mediapipe as mp
import numpy as np
import os
import random
import pygame
import pyttsx3
import threading
import asyncio
import platform

# Fungsi untuk generate soal matematika
def generate_math_problem():
    operators = ['+', '-', '*', '/']
    operator = random.choice(operators)
    
    if operator == '+':
        # Penjumlahan (hasil 0-10)
        result = random.randint(0, 10)
        num2 = random.randint(0, result)
        num1 = result - num2
    elif operator == '-':
        # Pengurangan (hasil 0-10)
        num1 = random.randint(0, 10)
        num2 = random.randint(0, num1)
    elif operator == '*':
        # Perkalian (hasil 0-10)
        result = random.randint(0, 10)
        factors = [i for i in range(1, 11) if result % i == 0]
        num1 = random.choice(factors)
        num2 = result // num1
    else:
        # Pembagian (hasil 0-10, tanpa sisa)
        num2 = random.randint(1, 10)
        num1 = random.randint(0, 10) * num2
    
    problem = f"{num1} {operator} {num2}"
    answer = eval(problem)
    return problem, float(answer)

# State untuk game
class GameState:
    def __init__(self):
        self.current_problem = None
        self.current_answer = None
        self.problems_count = 0
        self.correct_answers = 0
        self.total_problems = 5
        self.score = 0
        self.time_per_question = 7
        self.timer = 0
        self.last_time = 0
        self.current_answer_given = None
        self.feedback_delay = 60
        self.show_feedback = False
        self.game_over_delay = 120
        self.show_thank_you = False
        self.final_score_delay = 90
        self.answers_history = []
        
    def new_problem(self):
        if self.problems_count < self.total_problems:
            self.current_problem, self.current_answer = generate_math_problem()
            self.timer = self.time_per_question
            self.last_time = cv2.getTickCount()
            return True
        return False
    
    def update_timer(self):
        if self.timer > 0:
            current_time = cv2.getTickCount()
            elapsed = (current_time - self.last_time) / cv2.getTickFrequency()
            self.timer = max(0, self.time_per_question - elapsed)
            return self.timer > 0
        return False
    
    def check_answer(self, user_answer):
        if self.timer > 0:
            if abs(user_answer - self.current_answer) < 0.01:
                self.score += 20
                return True
        return False

# Daftar Indeks Landmark Tangan
JEMPOL = [1, 2, 3, 4]
TELUNJUK = [5, 6, 7, 8]
JARI_TENGAH = [9, 10, 11, 12]
JARI_MANIS = [13, 14, 15, 16]
JARI_KELINGKING = [17, 18, 19, 20]

# Fungsi untuk mendeteksi angka dari posisi jari
def detect_finger_number(hand_landmarks, handedness):
    fingers = []
    
    thumb_tip = hand_landmarks.landmark[JEMPOL[-1]]
    thumb_base = hand_landmarks.landmark[JEMPOL[0]]
    thumb_ip = hand_landmarks.landmark[JEMPOL[2]]
    
    if handedness == 'Right':
        fingers.append(thumb_tip.x < thumb_ip.x)
    else:
        fingers.append(thumb_tip.x > thumb_ip.x)
    
    finger_lists = [TELUNJUK, JARI_TENGAH, JARI_MANIS, JARI_KELINGKING]
    for finger in finger_lists:
        tip = hand_landmarks.landmark[finger[-1]]
        pip = hand_landmarks.landmark[finger[-2]]
        dip = hand_landmarks.landmark[finger[-3]]
        fingers.append(tip.y < pip.y and tip.y < dip.y)
    
    return sum(fingers)

def combine_hand_numbers(left_count, right_count):
    if left_count == 0:
        return right_count
    if right_count == 0:
        return left_count
    if left_count == 5:
        return 5 + right_count
    return min(10, left_count + right_count)

# Inisialisasi MediaPipe Hands dan Face Detection
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)
face_detection = mp_face.FaceDetection(min_detection_confidence=0.5)

# Fungsi untuk mengecek apakah tangan berinteraksi dengan tombol
def check_button_interaction(hand_landmarks, button_pos, button_size, width, height):
    if hand_landmarks:
        index_finger = hand_landmarks.landmark[8]
        x, y = int(index_finger.x * width), int(index_finger.y * height)
        button_x, button_y = button_pos
        button_w, button_h = button_size
        if (button_x < x < button_x + button_w and 
            button_y < y < button_y + button_h):
            return True
    return False

# Fungsi untuk menempatkan gambar ke dalam frame
def overlay_image(background, overlay, position):
    h, w = overlay.shape[:2]
    y, x = position
    if overlay.shape[2] == 4:
        overlay_rgb = overlay[:,:,:3]
        alpha = overlay[:,:,3] / 255.0
        alpha_3d = np.stack([alpha, alpha, alpha], axis=2)
        roi = background[y:y+h, x:x+w]
        result = (overlay_rgb * alpha_3d + roi * (1 - alpha_3d))
        background[y:y+h, x:x+w] = result
    else:
        background[y:y+h, x:x+w] = overlay
    return background

def draw_question_progress(frame, total_questions, current_question, answers, width):
    CIRCLE_RADIUS = 8
    LINE_LENGTH = 30
    SPACING = 45
    Y_POSITION = 30
    total_width = (SPACING * (total_questions - 1))
    start_x = (width - total_width) // 2
    
    for i in range(total_questions - 1):
        x1 = start_x + (i * SPACING) + CIRCLE_RADIUS
        x2 = x1 + LINE_LENGTH
        line_color = (150, 150, 150)
        if i < len(answers):
            line_color = (0, 255, 0) if answers[i] else (0, 0, 255)
        cv2.line(frame, (x1, Y_POSITION), (x2, Y_POSITION), line_color, 2)
    
    for i in range(total_questions):
        center_x = start_x + (i * SPACING)
        center = (center_x, Y_POSITION)
        if i == current_question:
            cv2.circle(frame, center, CIRCLE_RADIUS + 2, (0, 255, 255), -1)
            cv2.circle(frame, center, CIRCLE_RADIUS + 2, (255, 255, 255), 2)
        else:
            if i < len(answers):
                color = (0, 255, 0) if answers[i] else (0, 0, 255)
                cv2.circle(frame, center, CIRCLE_RADIUS, color, -1)
            else:
                cv2.circle(frame, center, CIRCLE_RADIUS, (150, 150, 150), 2)

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

def play_speak(text):
    threading.Thread(target=speak, args=(text,)).start()

async def main():
    # Membaca gambar asset
    logo_path = os.path.join(os.getcwd(), 'asset', 'logo.png')
    button_path = os.path.join(os.getcwd(), 'asset', 'buttonstart.png')
    tryagain_path = os.path.join(os.getcwd(), 'asset', 'buttontryagain.png')
    bgcard_path = os.path.join(os.getcwd(), 'asset', 'backgroundcard.png')

    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    button = cv2.imread(button_path, cv2.IMREAD_UNCHANGED)
    tryagain = cv2.imread(tryagain_path, cv2.IMREAD_UNCHANGED)
    bgcard = cv2.imread(bgcard_path, cv2.IMREAD_UNCHANGED)

    if logo is None or button is None or bgcard is None or tryagain is None:
        print("Error: Tidak dapat membaca file gambar!")
        print(f"Logo path: {logo_path}")
        print(f"Button path: {button_path}")
        print(f"Try Again path: {tryagain_path}")
        print(f"Background Card path: {bgcard_path}")
        return

    START_BUTTON_SIZE = (200, 60)
    TRYAGAIN_BUTTON_SIZE = (250, 180)
    logo = cv2.resize(logo, (200, 200))
    button = cv2.resize(button, START_BUTTON_SIZE)
    tryagain = cv2.resize(tryagain, TRYAGAIN_BUTTON_SIZE)
    bgcard = cv2.resize(bgcard, (300, 150)) 
    sound_delay = 70

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Tidak dapat membuka webcam!")
        return

    # Initialize frame dimensions
    success, frame = cap.read()
    if not success:
        print("Gagal membaca frame dari webcam")
        cap.release()
        return
    frame = cv2.flip(frame, 1)
    height, width = frame.shape[:2]

    is_game_started = False
    game_state = GameState()
    answer_display_time = 0
    answer_feedback = ""

    pygame.mixer.init()
    bgm_path = os.path.join(os.getcwd(), 'asset', 'sound_matematika.wav')
    win_sound_path = os.path.join(os.getcwd(), 'asset', 'sound_kematian.wav')
    lose_sound_path = os.path.join(os.getcwd(), 'asset', 'sound_kematian_kalah.wav')
    
    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.5)
        win_sound = pygame.mixer.Sound(win_sound_path)
        lose_sound = pygame.mixer.Sound(lose_sound_path)
        win_sound.set_volume(0.5)
        lose_sound.set_volume(0.5)
    except pygame.error as e:
        print(f"Error loading audio: {e}")

    def play_background_music():
        try:
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error playing background music: {e}")

    def stop_background_music():
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"Error stopping background music: {e}")

    def play_game_over_sound(score):
        try:
            stop_background_music()
            if score >= 60:
                win_sound.play()
            else:
                lose_sound.play()
        except pygame.error as e:
            print(f"Error playing game over sound: {e}")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Gagal membaca frame dari webcam")
            break

        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2
        text = game_state.current_problem

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = hands.process(rgb_frame)
        face_results = face_detection.process(rgb_frame)

        if not is_game_started:
            logo_x = (width - 200) // 2
            logo_y = 50
            button_x = (width - 200) // 2
            button_y = logo_y + 200 + 20
            frame = overlay_image(frame, logo, (logo_y, logo_x))
            frame = overlay_image(frame, button, (button_y, button_x))

            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS)
                    if check_button_interaction(
                        hand_landmarks,
                        (button_x, button_y),
                        (200, 60),
                        width,
                        height
                    ):
                        is_game_started = True
                        play_background_music()

        else:
            if face_results.detections:
                for detection in face_results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    face_x = int(bbox.xmin * width)
                    face_y = int(bbox.ymin * height)
                    face_w = int(bbox.width * width)
                    face_h = int(bbox.height * height)
                    bgcard_x = face_x - (bgcard.shape[1] - face_w) // 2
                    bgcard_y = face_y - bgcard.shape[0] - 20
                    bgcard_x = max(0, min(bgcard_x, width - bgcard.shape[1]))
                    bgcard_y = max(0, min(bgcard_y, height - bgcard.shape[0]))
                    frame = overlay_image(frame, bgcard, (bgcard_y, bgcard_x))

                    if game_state.current_problem is None:
                        game_state.new_problem()
                        answer_display_time = 0
                        answer_feedback = ""

                    if game_state.current_problem:
                        draw_question_progress(
                            frame, 
                            game_state.total_problems,
                            game_state.problems_count,
                            game_state.answers_history,
                            width
                        )
                        if not game_state.update_timer():
                            if not game_state.show_feedback:
                                final_answer = total_fingers if 'total_fingers' in locals() else 0
                                correct = final_answer == int(game_state.current_answer)
                                if correct:
                                    game_state.score += 20
                                    answer_feedback = "Benar! +20"
                                    play_speak("Your answer is right!")
                                    game_state.answers_history.append(True)
                                else:
                                    answer_feedback = "Salah! +0"
                                    play_speak(f"Your answer is wrong! The right answer is {int(game_state.current_answer)}")
                                    game_state.answers_history.append(False)
                                game_state.show_feedback = True
                                answer_display_time = game_state.feedback_delay
                            elif sound_delay > 0 and not correct:
                                sound_delay -= 1 
                            elif answer_display_time > 0:
                                feedback_color = (0, 255, 0) if "Benar" in answer_feedback else (0, 0, 255)
                                feedback_pos = (width//2 - 60, height//2)
                                cv2.putText(frame, answer_feedback,
                                          feedback_pos, font, 1,
                                          (0, 0, 0), 3)
                                cv2.putText(frame, answer_feedback,
                                          feedback_pos, font, 1,
                                          feedback_color, 2)
                                answer_display_time -= 1
                            else:
                                game_state.problems_count += 1
                                game_state.current_problem = None
                                game_state.show_feedback = False
                                sound_delay = 70

                        timer_text = f"Waktu: {int(game_state.timer)}s"
                        cv2.putText(frame, timer_text,
                                  (width - 150, 30), font, 0.7,
                                  (0, 0, 255) if game_state.timer < 2 else (255, 255, 255), 2)
                        score_text = f"Score: {game_state.score}"
                        cv2.putText(frame, score_text,
                                  (width - 150, 60), font, 0.7,
                                  (255, 255, 255), 2)

                        (text_width, text_height), baseline = cv2.getTextSize(
                            text, font, font_scale, thickness)
                        text_x = bgcard_x + (bgcard.shape[1] - text_width) // 2
                        text_y = bgcard_y + (bgcard.shape[0] + text_height) // 2
                        cv2.putText(frame, text, (text_x, text_y), font,
                                  font_scale, (255, 255, 255), thickness + 1)
                        cv2.putText(frame, text, (text_x, text_y), font,
                                  font_scale, (0, 0, 0), thickness)

                        left_count = 0
                        right_count = 0
                        if hand_results.multi_hand_landmarks:
                            for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                                handedness = hand_results.multi_handedness[idx].classification[0].label
                                count = detect_finger_number(hand_landmarks, handedness)
                                mp_drawing.draw_landmarks(
                                    frame,
                                    hand_landmarks,
                                    mp_hands.HAND_CONNECTIONS,
                                    mp_drawing_styles.get_default_hand_landmarks_style(),
                                    mp_drawing_styles.get_default_hand_connections_style()
                                )
                                if handedness == 'Left':
                                    left_count = count
                                else:
                                    right_count = count
                                hand_pos_y = 50 + (idx * 30)
                                cv2.putText(frame, f"{handedness}: {count}", 
                                          (10, hand_pos_y), font, 0.7, 
                                          (255, 255, 255), 2)
                            total_fingers = combine_hand_numbers(left_count, right_count)
                            cv2.putText(frame, f"Jawaban: {total_fingers}", 
                                      (10, 110), font, 1, (255, 255, 255), 2)
                            game_state.current_answer_given = total_fingers
                        elif hasattr(game_state, 'current_answer_given'):
                            total_fingers = game_state.current_answer_given
                            cv2.putText(frame, f"Jawaban: {total_fingers}", 
                                      (10, 110), font, 1, (255, 255, 255), 2)
                        if answer_display_time > 0:
                            feedback_color = (0, 255, 0) if "Benar" in answer_feedback else (0, 0, 255)
                            feedback_pos = (width//2 - 60, height//2)
                            cv2.putText(frame, answer_feedback,
                                      feedback_pos, font, 1,
                                      (0, 0, 0), 3)
                            cv2.putText(frame, answer_feedback,
                                      feedback_pos, font, 1,
                                      feedback_color, 2)
                            answer_display_time -= 1

        if game_state.problems_count >= game_state.total_problems:
            if not hasattr(game_state, 'game_over_played'):
                play_game_over_sound(game_state.score)
                game_state.game_over_played = True

            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

            y_start = height // 4
            y_spacing = 40
            messages = [
                ("Permainan Selesai!", 2.0, (0, 255, 0)),
                (f"Score Akhir: {game_state.score}/100", 1.8, (0, 255, 0))
            ]

            for i, (msg, scale, color) in enumerate(messages):
                text_size = cv2.getTextSize(msg, font, scale, 3)[0]
                text_x = (width - text_size[0]) // 2
                text_y = y_start + i * y_spacing
                cv2.putText(frame, msg,
                          (text_x, text_y),
                          font, scale, (0, 0, 0), 4)
                cv2.putText(frame, msg,
                          (text_x, text_y),
                          font, scale, color, 2)

            tryagain_x = (width - TRYAGAIN_BUTTON_SIZE[0]) // 2
            tryagain_y = y_start + (len(messages) * y_spacing) + 40
            frame = overlay_image(frame, tryagain, (tryagain_y, tryagain_x))

            quit_text = "Tekan 'Q' untuk keluar"
            text_size = cv2.getTextSize(quit_text, font, 1.0, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = tryagain_y + TRYAGAIN_BUTTON_SIZE[1] + 40
            cv2.putText(frame, quit_text,
                      (text_x, text_y),
                      font, 1.0, (0, 0, 0), 3)
            cv2.putText(frame, quit_text,
                      (text_x, text_y),
                      font, 1.0, (255, 255, 255), 2)

            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                    if check_button_interaction(
                        hand_landmarks,
                        (tryagain_x, tryagain_y),
                        TRYAGAIN_BUTTON_SIZE,
                        width,
                        height
                    ):
                        game_state = GameState()
                        answer_display_time = 0
                        answer_feedback = ""
                        win_sound.stop()
                        lose_sound.stop()
                        pygame.mixer.music.load(bgm_path)
                        play_background_music()
                        continue

        cv2.imshow('Interactive Maths', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        await asyncio.sleep(1.0 / 60)  # Control frame rate

    stop_background_music()
    pygame.mixer.quit()
    hands.close()
    face_detection.close()
    cap.release()
    cv2.destroyAllWindows()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())