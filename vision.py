import cv2
import numpy as np
# import serial  # uncomment when Arduino is connected

# ============================================================
# CONFIGURATION
# ============================================================
CAMERA_INDEX = 0

# Raw camera resolution (before rotation)
RAW_WIDTH = 640
RAW_HEIGHT = 480

# After 90° rotation, width and height swap
FRAME_WIDTH = RAW_HEIGHT   # 480
FRAME_HEIGHT = RAW_WIDTH   # 640

# Which way to rotate: pick ONE based on how your camera is mounted
# Try COUNTERCLOCKWISE first. If the image is upside-down, switch.
ROTATION = cv2.ROTATE_90_COUNTERCLOCKWISE
# ROTATION = cv2.ROTATE_90_CLOCKWISE

# Y-pixel thresholds on the ROTATED frame (calibrate in Step 8)
# These are now out of 640 (the new height) instead of 480
CLOSE_THRESHOLD_Y = 420     # ~6 feet — start tracking
VIBRATION_THRESHOLD_Y = 500  # ~4 feet — trigger vibration motor

# Minimum contour area to count as a real obstacle (filters noise)
MIN_OBSTACLE_AREA = 3000

# ============================================================
# SETUP
# ============================================================
cap = cv2.VideoCapture(CAMERA_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, RAW_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RAW_HEIGHT)

if not cap.isOpened():
    print("ERROR: Cannot open camera")
    exit()

# Background subtractor — learns what the "normal" scene looks like.
# Since the camera is FIXED in place, this works very well.
# Anything new that enters the scene gets detected as foreground.
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500,        # frames to learn background
    varThreshold=50,    # sensitivity (lower = more sensitive)
    detectShadows=True  # detect shadows separately
)

# Morphology kernel for cleaning up the detection mask
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

# Arduino serial connection (uncomment when hardware is ready)
# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# import time; time.sleep(2)  # wait for Arduino to reset


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_zone(cx):
    """Which third of the ROTATED frame is this x-coordinate in?"""
    if cx < FRAME_WIDTH // 3:
        return "LEFT"
    elif cx < 2 * FRAME_WIDTH // 3:
        return "CENTER"
    else:
        return "RIGHT"


# def process_frame(frame):
#     """
#     Takes a raw camera frame, rotates it, detects obstacles.
#     Returns (obstacles, debug_frame, mask).
#     obstacles = list of (bottom_y, zone, cx)
#     """
#     # STEP 1: Rotate the frame so vertical mount becomes portrait
#     rotated = cv2.rotate(frame, ROTATION)

#     # STEP 2: Blur to reduce camera noise
#     blurred = cv2.GaussianBlur(rotated, (11, 11), 0)

#     # STEP 3: Background subtraction
#     fg_mask = bg_subtractor.apply(blurred)

#     # STEP 4: Clean up the mask
#     fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
#     fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)

#     # STEP 5: Remove shadow pixels (MOG2 marks shadows as ~127)
#     _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

#     # STEP 6: Find contours of detected objects
#     contours, _ = cv2.findContours(
#         fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#     )

#     obstacles = []
#     debug_frame = rotated.copy()

#     # Draw zone divider lines (vertical)
#     third = FRAME_WIDTH // 3
#     cv2.line(debug_frame, (third, 0), (third, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.line(debug_frame, (third * 2, 0), (third * 2, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.putText(debug_frame, "LEFT", (10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "CENTER", (third + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "RIGHT", (third * 2 + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#     # Draw threshold lines (horizontal)
#     cv2.line(debug_frame, (0, CLOSE_THRESHOLD_Y),
#              (FRAME_WIDTH, CLOSE_THRESHOLD_Y), (0, 255, 255), 1)
#     cv2.putText(debug_frame, "~6ft", (5, CLOSE_THRESHOLD_Y - 5),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
#     cv2.line(debug_frame, (0, VIBRATION_THRESHOLD_Y),
#              (FRAME_WIDTH, VIBRATION_THRESHOLD_Y), (0, 0, 255), 1)
#     cv2.putText(debug_frame, "~4ft VIBRATE", (5, VIBRATION_THRESHOLD_Y - 5),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

#     for cnt in contours:
#         area = cv2.contourArea(cnt)
#         if area < MIN_OBSTACLE_AREA:
#             continue

#         x, y, w, h = cv2.boundingRect(cnt)
#         bottom_y = y + h
#         cx = x + w // 2

#         if bottom_y > CLOSE_THRESHOLD_Y:
#             zone = get_zone(cx)
#             obstacles.append((bottom_y, zone, cx))

#             if bottom_y > VIBRATION_THRESHOLD_Y:
#                 color = (0, 0, 255)
#                 label = f"{zone} CLOSE!"
#             else:
#                 color = (0, 255, 255)
#                 label = f"{zone}"

#             cv2.rectangle(debug_frame, (x, y), (x + w, y + h), color, 2)
#             cv2.putText(debug_frame, label, (x, y - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#     return obstacles, debug_frame, fg_mask
def process_frame(frame):
    """
    Detects obstacles using:
    1. Dynamic floor sampling (adapts to any room)
    2. Edge detection (catches walls even if same color as floor)
    """
    rotated = cv2.rotate(frame, ROTATION)
    blurred = cv2.GaussianBlur(rotated, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # ── DYNAMIC FLOOR SAMPLING ──
    # Sample a strip at the very bottom center of the frame.
    # This is ALWAYS floor because the walker is right there.
    h, w = rotated.shape[:2]
    sample_strip = hsv[h - 40 : h - 5, w // 4 : 3 * w // 4]

    # Calculate the mean and standard deviation of the floor color
    h_mean = np.mean(sample_strip[:, :, 0])
    s_mean = np.mean(sample_strip[:, :, 1])
    v_mean = np.mean(sample_strip[:, :, 2])
    h_std = np.std(sample_strip[:, :, 0])
    s_std = np.std(sample_strip[:, :, 1])
    v_std = np.std(sample_strip[:, :, 2])

    # Build a range that covers the floor's color with some tolerance
    # The multiplier controls how strict the match is (2.0 = lenient, 1.0 = strict)
    tolerance = 2.0
    floor_lower = np.array([
        max(0, h_mean - h_std * tolerance - 10),
        max(0, s_mean - s_std * tolerance - 15),
        max(0, v_mean - v_std * tolerance - 25)
    ], dtype=np.uint8)
    floor_upper = np.array([
        min(180, h_mean + h_std * tolerance + 10),
        min(255, s_mean + s_std * tolerance + 15),
        min(255, v_mean + v_std * tolerance + 25)
    ], dtype=np.uint8)

    # Mask: floor pixels = white
    floor_mask = cv2.inRange(hsv, floor_lower, floor_upper)

    # ── EDGE DETECTION (catches same-color walls) ──
    # Edges mark where surfaces change angle — floor-to-wall transitions
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # Thicken edges so they act as barriers
    edge_dilated = cv2.dilate(edges, kernel, iterations=2)

    # ── COMBINE BOTH METHODS ──
    # Start with "not floor" mask
    obstacle_mask = cv2.bitwise_not(floor_mask)

    # Add edges as additional obstacles
    # This catches walls that are floor-colored because the edge
    # between floor and wall still shows up
    obstacle_mask = cv2.bitwise_or(obstacle_mask, edge_dilated)

    # Ignore the top quarter (ceiling, far away, irrelevant)
    obstacle_mask[0 : FRAME_HEIGHT // 4, :] = 0

    # Clean up
    obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # ── FIND CONTOURS ──
    contours, _ = cv2.findContours(
        obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    obstacles = []
    debug_frame = rotated.copy()

    # Draw the floor sample region so you can see what it's using
    cv2.rectangle(debug_frame, (w // 4, h - 40), (3 * w // 4, h - 5), (0, 255, 0), 1)
    cv2.putText(debug_frame, "floor sample", (w // 4 + 5, h - 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    # Draw zone dividers
    third = FRAME_WIDTH // 3
    cv2.line(debug_frame, (third, 0), (third, FRAME_HEIGHT), (255, 255, 0), 1)
    cv2.line(debug_frame, (third * 2, 0), (third * 2, FRAME_HEIGHT), (255, 255, 0), 1)
    cv2.putText(debug_frame, "LEFT", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    cv2.putText(debug_frame, "CENTER", (third + 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    cv2.putText(debug_frame, "RIGHT", (third * 2 + 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    # Draw threshold lines
    cv2.line(debug_frame, (0, CLOSE_THRESHOLD_Y),
             (FRAME_WIDTH, CLOSE_THRESHOLD_Y), (0, 255, 255), 1)
    cv2.putText(debug_frame, "~6ft", (5, CLOSE_THRESHOLD_Y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    cv2.line(debug_frame, (0, VIBRATION_THRESHOLD_Y),
             (FRAME_WIDTH, VIBRATION_THRESHOLD_Y), (0, 0, 255), 1)
    cv2.putText(debug_frame, "~4ft VIBRATE", (5, VIBRATION_THRESHOLD_Y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_OBSTACLE_AREA:
            continue

        x, y, w_box, h_box = cv2.boundingRect(cnt)
        bottom_y = y + h_box
        cx = x + w_box // 2

        if bottom_y > CLOSE_THRESHOLD_Y:
            zone = get_zone(cx)
            obstacles.append((bottom_y, zone, cx))

            if bottom_y > VIBRATION_THRESHOLD_Y:
                color = (0, 0, 255)
                label = f"{zone} CLOSE!"
            else:
                color = (0, 255, 255)
                label = f"{zone}"

            cv2.rectangle(debug_frame, (x, y), (x + w_box, y + h_box), color, 2)
            cv2.putText(debug_frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return obstacles, debug_frame, obstacle_mask


def decide_action(obstacles):
    """
    Given detected obstacles, decide nudge direction and vibration.
    Returns (nudge_direction, should_vibrate)
    """
    if not obstacles:
        return None, False

    should_vibrate = any(by > VIBRATION_THRESHOLD_Y for by, _, _ in obstacles)

    closest = max(obstacles, key=lambda o: o[0])
    _, zone, _ = closest

    if zone == "RIGHT":
        nudge = "LEFT"
    elif zone == "LEFT":
        nudge = "RIGHT"
    elif zone == "CENTER":
        left_obstacles = [o for o in obstacles if o[1] == "LEFT"]
        right_obstacles = [o for o in obstacles if o[1] == "RIGHT"]
        if len(left_obstacles) <= len(right_obstacles):
            nudge = "LEFT"
        else:
            nudge = "RIGHT"
    else:
        nudge = None

    return nudge, should_vibrate


def send_command(nudge, vibrate):
    """Send commands to Arduino. Replace prints with serial writes."""
    if vibrate:
        print(">>> VIBRATION MOTOR: ON (obstacle within ~4 feet)")
        # ser.write(b'V')

    if nudge == "LEFT":
        print(">>> NUDGE LEFT")
        # ser.write(b'L')
    elif nudge == "RIGHT":
        print(">>> NUDGE RIGHT")
        # ser.write(b'R')
    else:
        if not vibrate:
            print(">>> ALL CLEAR")
            # ser.write(b'S')


# ============================================================
# MOUSE CALLBACK FOR CALIBRATION
# ============================================================
def mouse_callback(event, x, y, flags, param):
    """Click anywhere on the debug window to print pixel coordinates."""
    if event == cv2.EVENT_LBUTTONDOWN:
        zone = get_zone(x)
        print(f"Clicked: x={x}, y={y} | Zone: {zone}"
              f" | {'VIBRATE RANGE' if y > VIBRATION_THRESHOLD_Y else 'CLOSE' if y > CLOSE_THRESHOLD_Y else 'far'}")


# ============================================================
# MAIN LOOP
# ============================================================
print("Smart Walker Vision System (Vertical Camera)")
print(f"Rotated frame size: {FRAME_WIDTH}x{FRAME_HEIGHT}")
print("Press 'q' to quit")
print("Press 'c' to capture a calibration snapshot")
print("Click on the debug window to check pixel coordinates")
print("-" * 50)

cv2.namedWindow("Walker Vision - Debug")
cv2.setMouseCallback("Walker Vision - Debug", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Lost camera feed")
        break

    obstacles, debug_frame, mask = process_frame(frame)
    nudge, vibrate = decide_action(obstacles)
    send_command(nudge, vibrate)

    cv2.imshow("Walker Vision - Debug", debug_frame)
    cv2.imshow("Detection Mask", mask)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        cv2.imwrite("calibration_snapshot.png", debug_frame)
        print("Saved calibration_snapshot.png")

cap.release()
cv2.destroyAllWindows()