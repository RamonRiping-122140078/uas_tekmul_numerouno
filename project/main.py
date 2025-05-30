import cv2
import os
import game_state
import hand_detector
import face_detector
import audio_manager
import ui_renderer

def main():
    """
    Fungsi utama untuk menjalankan permainan matematika interaktif.
    
    Menginisialisasi aset, webcam, dan mengelola alur permainan.
    """
    # Memuat aset dari folder
    asset_dir = os.path.join(os.getcwd(), 'project', 'asset')
    logo_path = os.path.join(asset_dir, 'logo.png')
    button_path = os.path.join(asset_dir, 'buttonstart.png')
    tryagain_path = os.path.join(asset_dir, 'buttontryagain.png')
    bgcard_path = os.path.join(asset_dir, 'backgroundcard.png')
    bgm_path = os.path.join(asset_dir, 'sound_matematika.wav')
    win_sound_path = os.path.join(asset_dir, 'sound_kematian.wav')
    lose_sound_path = os.path.join(asset_dir, 'sound_kematian_kalah.wav')
    
    # Memuat gambar
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    button = cv2.imread(button_path, cv2.IMREAD_UNCHANGED)
    tryagain = cv2.imread(tryagain_path, cv2.IMREAD_UNCHANGED)
    bgcard = cv2.imread(bgcard_path, cv2.IMREAD_UNCHANGED)
    
    # Memeriksa keberhasilan memuat gambar
    if any(img is None for img in [logo, button, tryagain, bgcard]):
        print("Error: Gagal memuat file gambar!")
        print(f"Logo path: {logo_path}")
        print(f"Button path: {button_path}")
        print(f"Try Again path: {tryagain_path}")
        print(f"Background Card path: {bgcard_path}")
        return
    
    # Mengubah ukuran gambar
    logo = cv2.resize(logo, (200, 200))
    button = cv2.resize(button, (200, 60))
    tryagain = cv2.resize(tryagain, (250, 180))
    bgcard = cv2.resize(bgcard, (300, 150))
    
    # Inisialisasi komponen permainan
    game_state_instance = game_state.GameState()
    hand_detector_instance = hand_detector.HandDetector()
    face_detector_instance = face_detector.FaceDetector()
    audio_manager_instance = audio_manager.AudioManager(bgm_path, win_sound_path, lose_sound_path)
    ui_renderer_instance = ui_renderer.UIRenderer(logo, button, tryagain, bgcard)
    
    # Inisialisasi webcam
    cap = cv2.VideoCapture(0)
    is_game_started = False
    answer_display_time = 0
    answer_feedback = ""
    sound_delay = 30  # ~1 detik pada 30fps
    
    try:
        # Memulai loop utama permainan
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Gagal mengambil frame dari webcam")
                break
            
            # Membalik frame secara horizontal
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Menangani menu utama
            if not is_game_started:
                button_x, button_y = ui_renderer_instance.draw_main_menu(frame, width, height)
                results = hand_detector_instance.hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Menggambar landmark tangan dengan garis putih di menu
                        hand_detector_instance.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            hand_detector_instance.mp_hands.HAND_CONNECTIONS,
                            hand_detector_instance.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                            hand_detector_instance.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2)
                        )
                        # Memeriksa interaksi dengan start_button
                        if hand_detector_instance.check_button_interaction(hand_landmarks, (button_x, button_y), 
                                                               (200, 60), width, height):
                            is_game_started = True
                            audio_manager_instance.play_background_music()
            
            else:
                # Memproses tangan dan wajah
                left_count, right_count, total_fingers = hand_detector_instance.process_hands(frame, rgb_frame)
                face_pos = face_detector_instance.get_face_position(rgb_frame, width, height)
                
                # Menangani layar akhir permainan
                if game_state_instance.problems_count >= game_state_instance.total_problems:
                    if not game_state_instance.game_over_played:
                        audio_manager_instance.play_game_over_sound(game_state_instance.score)
                        game_state_instance.game_over_played = True
                    
                    # Menggambar layar akhir
                    tryagain_x, tryagain_y = ui_renderer_instance.draw_game_over(frame, game_state_instance, width, height)
                    results = hand_detector_instance.hands.process(rgb_frame)
                    
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            hand_detector_instance.mp_drawing.draw_landmarks(
                                frame,
                                hand_landmarks,
                                hand_detector_instance.mp_hands.HAND_CONNECTIONS,
                                hand_detector_instance.mp_drawing_styles.get_default_hand_landmarks_style(),
                                hand_detector_instance.mp_drawing_styles.get_default_hand_connections_style()
                            )
                            # Memeriksa interaksi dengan tryagain_button
                            if hand_detector_instance.check_button_interaction(hand_landmarks, (tryagain_x, tryagain_y), 
                                                                   (250, 180), width, height):
                                # Mengatur ulang permainan
                                game_state_instance = game_state.GameState()
                                is_game_started = True
                                answer_display_time = 0
                                answer_feedback = ""
                                audio_manager_instance.stop_all_sounds()
                                audio_manager_instance.play_background_music()
                                sound_delay = 30
                                continue
                
                else:
                    # Memperbarui jawaban
                    if total_fingers is not None:
                        game_state_instance.current_answer_given = total_fingers
                    
                    # Membuat soal baru jika diperlukan
                    if game_state_instance.current_problem is None:
                        game_state_instance.new_problem()
                        answer_display_time = 0
                        answer_feedback = ""
                    
                    # Memperbarui status permainan
                    if game_state_instance.current_problem:
                        if not game_state_instance.update_timer():
                            if not game_state_instance.show_feedback:
                                # Memeriksa jawaban
                                final_answer = game_state_instance.current_answer_given if game_state_instance.current_answer_given is not None else 0
                                correct = game_state_instance.check_answer(final_answer)
                                game_state_instance.answer_history.append(correct)
                                answer_feedback = f"Benar! +20" if correct else f"Salah! +0"
                                audio_manager_instance.speak("Your answer is right!" if correct else 
                                    f"Your answer is wrong! The right answer is {int(game_state_instance.current_answer)}")
                                game_state_instance.show_feedback = True
                                answer_display_time = game_state_instance.feedback_delay
                            elif sound_delay > 0:
                                sound_delay -= 1
                            elif answer_display_time > 0:
                                answer_display_time -= 1
                            else:
                                # Pindah ke soal berikutnya
                                game_state_instance.problems_count += 1
                                game_state_instance.current_problem = None
                                game_state_instance.show_feedback = False
                                sound_delay = 30
                            
                    # Menggambar UI permainan
                    ui_renderer_instance.draw_game_ui(
                        frame, game_state_instance, width, height, face_pos, total_fingers,
                        answer_feedback, answer_display_time
                    )
            
            # Menampilkan frame
            cv2.imshow('Kamera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # Membersihkan sumber daya
        cap.release()
        hand_detector_instance.close()
        face_detector_instance.close()
        audio_manager_instance.quit()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()