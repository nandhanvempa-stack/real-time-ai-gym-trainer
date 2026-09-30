import cv2
import mediapipe as mp
import numpy as np
import math

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    """Return angle ABC in degrees."""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denominator == 0:
        return 0.0

    cosine = np.dot(ba, bc) / denominator
    cosine = np.clip(cosine, -1.0, 1.0)
    return math.degrees(math.acos(cosine))


def point(landmarks, landmark, width, height):
    p = landmarks[landmark.value]
    return [p.x * width, p.y * height]


def process_curl(landmarks, width, height, side):
    if side == "RIGHT":
        shoulder = point(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, width, height)
        elbow = point(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW, width, height)
        wrist = point(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)
    else:
        shoulder = point(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER, width, height)
        elbow = point(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW, width, height)
        wrist = point(landmarks, mp_pose.PoseLandmark.LEFT_WRIST, width, height)

    angle = calculate_angle(shoulder, elbow, wrist)
    return angle


def process_squat(landmarks, width, height, side):
    if side == "RIGHT":
        hip = point(landmarks, mp_pose.PoseLandmark.RIGHT_HIP, width, height)
        knee = point(landmarks, mp_pose.PoseLandmark.RIGHT_KNEE, width, height)
        ankle = point(landmarks, mp_pose.PoseLandmark.RIGHT_ANKLE, width, height)
    else:
        hip = point(landmarks, mp_pose.PoseLandmark.LEFT_HIP, width, height)
        knee = point(landmarks, mp_pose.PoseLandmark.LEFT_KNEE, width, height)
        ankle = point(landmarks, mp_pose.PoseLandmark.LEFT_ANKLE, width, height)

    angle = calculate_angle(hip, knee, ankle)
    return angle


def process_pushup(landmarks, width, height, side):
    if side == "RIGHT":
        shoulder = point(landmarks, mp_pose.PoseLandmark.RIGHT_SHOULDER, width, height)
        elbow = point(landmarks, mp_pose.PoseLandmark.RIGHT_ELBOW, width, height)
        wrist = point(landmarks, mp_pose.PoseLandmark.RIGHT_WRIST, width, height)
        hip = point(landmarks, mp_pose.PoseLandmark.RIGHT_HIP, width, height)
    else:
        shoulder = point(landmarks, mp_pose.PoseLandmark.LEFT_SHOULDER, width, height)
        elbow = point(landmarks, mp_pose.PoseLandmark.LEFT_ELBOW, width, height)
        wrist = point(landmarks, mp_pose.PoseLandmark.LEFT_WRIST, width, height)
        hip = point(landmarks, mp_pose.PoseLandmark.LEFT_HIP, width, height)

    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    body_angle = calculate_angle(shoulder, hip, [hip[0], hip[1] + 100])
    return elbow_angle, body_angle


def draw_text(frame, text, position, scale=0.7):
    cv2.putText(
        frame, text, position, cv2.FONT_HERSHEY_SIMPLEX,
        scale, (255, 255, 255), 2, cv2.LINE_AA
    )


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    exercise = "CURL"
    side = "RIGHT"
    reps = 0
    stage = "DOWN"
    feedback = "Ready"
    last_angle = 0

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            feedback = "Move into position"

            if result.pose_landmarks:
                landmarks = result.pose_landmarks.landmark

                if exercise == "CURL":
                    angle = process_curl(landmarks, width, height, side)
                    last_angle = angle

                    if angle > 155:
                        stage = "DOWN"
                        feedback = "Good - extend your arm"
                    elif angle < 50:
                        if stage == "DOWN":
                            reps += 1
                        stage = "UP"
                        feedback = "Good curl"
                    else:
                        feedback = "Complete the movement"

                elif exercise == "SQUAT":
                    angle = process_squat(landmarks, width, height, side)
                    last_angle = angle

                    if angle > 160:
                        stage = "UP"
                        feedback = "Stand straight"
                    elif angle < 100:
                        if stage == "UP":
                            reps += 1
                        stage = "DOWN"
                        feedback = "Good squat"
                    else:
                        feedback = "Go lower"

                elif exercise == "PUSHUP":
                    angle, body_angle = process_pushup(
                        landmarks, width, height, side
                    )
                    last_angle = angle

                    if angle > 155:
                        stage = "UP"
                        feedback = "Good - push up"
                    elif angle < 90:
                        if stage == "UP":
                            reps += 1
                        stage = "DOWN"
                        feedback = "Good - go down"
                    else:
                        feedback = "Complete the push-up"

                    # Simple posture warning.
                    if body_angle > 25:
                        feedback = "Keep your body straight"

                mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            # Information panel
            cv2.rectangle(frame, (10, 10), (360, 175), (0, 0, 0), -1)

            draw_text(frame, f"Exercise: {exercise}", (25, 40))
            draw_text(frame, f"Reps: {reps}", (25, 75))
            draw_text(frame, f"Stage: {stage}", (25, 110))
            draw_text(frame, f"Angle: {int(last_angle)}", (25, 145))
            draw_text(frame, feedback, (25, 205), 0.65)

            draw_text(
                frame,
                "1=Curl  2=Squat  3=Push-up  R=Reset  Q=Quit",
                (15, height - 20),
                0.55
            )

            cv2.imshow("Real-Time AI Gym Trainer", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("1"):
                exercise = "CURL"
                reps = 0
                stage = "DOWN"
            elif key == ord("2"):
                exercise = "SQUAT"
                reps = 0
                stage = "UP"
            elif key == ord("3"):
                exercise = "PUSHUP"
                reps = 0
                stage = "UP"
            elif key == ord("r"):
                reps = 0
                stage = "DOWN" if exercise == "CURL" else "UP"

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
