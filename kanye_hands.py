# kanye_hands.py
# Hand gesture sampler - Play audio samples with hand gestures
#
# Requirements:
#   pip install opencv-python mediapipe numpy sounddevice soundfile

import os
import time
from collections import defaultdict

import cv2
import mediapipe as mp
import numpy as np
import sounddevice as sd
import soundfile as sf

# =========================
# ------- SETTINGS --------
# =========================
CAMERA_INDEX = 0
FRAME_W, FRAME_H = 640, 480

# Box sizes
BOX_SIZE_FINGER = 20
BOX_SIZE_THUMB  = 25

# Cooldown
COOLDOWN_SEC = 0.2
FULL_SONG_COOLDOWN = 2.0

# MediaPipe
MIN_DET_CONF = 0.5
MIN_TRK_CONF = 0.5
MODEL_COMPLEXITY = 0

DRAW_SKELETON = False

# Audio files
AUDIO_DIR = "audio"
SOUND_FILES = {
    ("Right", "INDEX"):  "work_it.wav",
    ("Right", "MIDDLE"): "make_it.wav",
    ("Right", "RING"):   "do_it.wav",
    ("Right", "PINKY"):  "makes_us.wav",
    ("Left",  "INDEX"):  "harder.wav",
    ("Left",  "MIDDLE"): "better.wav",
    ("Left",  "RING"):   "faster.wav",
    ("Left",  "PINKY"):  "stronger.wav",
}

FULL_SONG_FILE = "kanye_stronger.wav"

LABEL_TEXT = {
    "Right": {"INDEX": "Work It", "MIDDLE": "Make It", "RING": "Do It", "PINKY": "Makes Us"},
    "Left":  {"INDEX": "Harder",  "MIDDLE": "Better",  "RING": "Faster","PINKY": "Stronger"},
}

WINDOW_TITLE = "Kanye Hands (ESC: Quit | +/-: Size | S: Skeleton)"

# =========================
# ------ UTILITIES --------
# =========================
def load_sound_clip(path: str):
    try:
        data, sr = sf.read(path, dtype="float32", always_2d=True)
        return data, sr
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def play_clip(clip):
    if clip is None:
        return
    data, sr = clip
    try:
        sd.play(data, sr, blocking=False)
    except:
        pass

def stop_all_audio():
    try:
        sd.stop()
    except:
        pass

def tip_to_px(lm_point):
    return int(lm_point.x * FRAME_W), int(lm_point.y * FRAME_H)

def draw_circle(img, center, radius, color, thickness=2):
    cv2.circle(img, (int(center[0]), int(center[1])), radius, color, thickness)

def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def handed_label(mp_handedness):
    label = mp_handedness.classification[0].label
    return "Right" if "Right" in label else "Left"

# =========================
# --------- MAIN ----------
# =========================
def main():
    global BOX_SIZE_FINGER, BOX_SIZE_THUMB, DRAW_SKELETON

    print("Loading audio files...")
    sounds = {}
    for key, fname in SOUND_FILES.items():
        full = os.path.join(AUDIO_DIR, fname)
        if os.path.exists(full):
            clip = load_sound_clip(full)
            if clip is not None:
                sounds[key] = clip

    # Load full song
    full_song_path = os.path.join(AUDIO_DIR, FULL_SONG_FILE)
    full_song = None
    if os.path.exists(full_song_path):
        full_song = load_sound_clip(full_song_path)
        if full_song:
            print(f"✓ Full song loaded: {FULL_SONG_FILE}")

    state = defaultdict(lambda: 0)
    last  = defaultdict(lambda: 0.0)
    thumbs_touching_state = 0
    last_full_song_time = 0.0

    mp_hands = mp.solutions.hands
    mp_draw  = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("ERROR: Could not open camera!")
        return

    print("\n" + "="*60)
    print("🎹 KANYE HANDS - Controls:")
    print("="*60)
    print("  Touch fingers to thumb       = Play samples")
    print("  Touch BOTH THUMBS together   = FULL SONG!")
    print("  Press '+/-'                  = Adjust box size")
    print("  Press 'S'                    = Toggle skeleton")
    print("  Press ESC                    = Quit")
    print("="*60 + "\n")
    
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=MIN_DET_CONF,
        min_tracking_confidence=MIN_TRK_CONF,
        model_complexity=MODEL_COMPLEXITY
    ) as hands:

        fps_time = time.time()
        fps_counter = 0
        fps_display = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            fps_counter += 1
            if time.time() - fps_time > 1.0:
                fps_display = fps_counter
                fps_counter = 0
                fps_time = time.time()

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            res = hands.process(rgb)
            rgb.flags.writeable = True
            now = time.time()

            # Title
            cv2.putText(frame, f"POV: Kanye 2007 | FPS: {fps_display}",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Instructions
            cv2.putText(frame, "Touch thumbs together = FULL SONG",
                        (10, FRAME_H - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 0), 1)

            thumb_positions = {}

            if res.multi_hand_landmarks and res.multi_handedness:
                for lmset, handed in zip(res.multi_hand_landmarks, res.multi_handedness):
                    hand_label = handed_label(handed)
                    lm = lmset.landmark
                    thumb_xy = tip_to_px(lm[4])
                    thumb_positions[hand_label] = thumb_xy

                thumbs_colliding = False
                if "Left" in thumb_positions and "Right" in thumb_positions:
                    dist = distance(thumb_positions["Left"], thumb_positions["Right"])
                    thumb_trigger_dist = BOX_SIZE_THUMB * 2.5
                    thumbs_colliding = dist < thumb_trigger_dist

                    if thumbs_colliding:
                        cv2.line(frame, thumb_positions["Left"], thumb_positions["Right"], 
                                (0, 255, 255), 3)

                    if thumbs_colliding and thumbs_touching_state == 0:
                        if (now - last_full_song_time) > FULL_SONG_COOLDOWN:
                            if full_song:
                                stop_all_audio()
                                play_clip(full_song)
                                print("🎵 FULL SONG PLAYING!")
                                last_full_song_time = now
                        thumbs_touching_state = 1
                    elif not thumbs_colliding and thumbs_touching_state == 1:
                        thumbs_touching_state = 0

                for lmset, handed in zip(res.multi_hand_landmarks, res.multi_handedness):
                    hand_label = handed_label(handed)
                    lm = lmset.landmark

                    thumb_xy = tip_to_px(lm[4])
                    thumb_color = (0, 255, 255) if thumbs_colliding else (0, 0, 255)
                    draw_circle(frame, thumb_xy, BOX_SIZE_THUMB, thumb_color, 3 if thumbs_colliding else 2)

                    finger_data = [
                        (8,  "INDEX",  0),
                        (12, "MIDDLE", 0),
                        (16, "RING",   0),
                        (20, "PINKY",  0),
                    ]

                    for tip_id, fname, offset in finger_data:
                        key = (hand_label, fname)
                        fx, fy = tip_to_px(lm[tip_id])
                        fy += offset
                        finger_xy = (fx, fy)
                        
                        dist = distance(thumb_xy, finger_xy)
                        trigger_dist = BOX_SIZE_THUMB + BOX_SIZE_FINGER
                        colliding = dist < trigger_dist

                        color = (0, 255, 0) if colliding else (180, 180, 180)
                        draw_circle(frame, finger_xy, BOX_SIZE_FINGER, color, 2)

                        txt = LABEL_TEXT[hand_label][fname]
                        label_y = int(fy - BOX_SIZE_FINGER - 8)
                        label_x = int(fx - 15)
                        
                        cv2.putText(frame, txt, (label_x, label_y),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

                        if colliding and state[key] == 0:
                            if (now - last[key]) > COOLDOWN_SEC and key in sounds:
                                if not thumbs_colliding:
                                    play_clip(sounds[key])
                                    last[key] = now
                            state[key] = 1
                        elif not colliding and state[key] == 1:
                            state[key] = 0

                    if DRAW_SKELETON:
                        mp_draw.draw_landmarks(
                            frame, lmset, mp_hands.HAND_CONNECTIONS,
                            mp_draw.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                            mp_draw.DrawingSpec(color=(255, 255, 255), thickness=1)
                        )

            cv2.imshow(WINDOW_TITLE, frame)

            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # ESC
                break
            elif k in (ord('+'), ord('=')):
                BOX_SIZE_FINGER = min(50, BOX_SIZE_FINGER + 2)
                BOX_SIZE_THUMB  = min(60, BOX_SIZE_THUMB  + 2)
            elif k == ord('-'):
                BOX_SIZE_FINGER = max(10, BOX_SIZE_FINGER - 2)
                BOX_SIZE_THUMB  = max(15, BOX_SIZE_THUMB  - 2)
            elif k == ord('s') or k == ord('S'):
                DRAW_SKELETON = not DRAW_SKELETON

    cap.release()
    cv2.destroyAllWindows()
    stop_all_audio()
    
    print("\n👋 Bye!")

if __name__ == "__main__":
    main()
