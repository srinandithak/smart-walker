# import cv2
# import numpy as np
# # import serial  # uncomment when Arduino is connected

# # ============================================================
# # CONFIGURATION
# # ============================================================
# CAMERA_INDEX = 0

# # Raw camera resolution (before rotation)
# RAW_WIDTH = 640
# RAW_HEIGHT = 480

# # After 90° rotation, width and height swap
# FRAME_WIDTH = RAW_HEIGHT   # 480
# FRAME_HEIGHT = RAW_WIDTH   # 640

# # Which way to rotate: pick ONE based on how your camera is mounted
# # Try COUNTERCLOCKWISE first. If the image is upside-down, switch.
# ROTATION = cv2.ROTATE_90_COUNTERCLOCKWISE
# # ROTATION = cv2.ROTATE_90_CLOCKWISE

# # Y-pixel thresholds on the ROTATED frame (calibrate in Step 8)
# # These are now out of 640 (the new height) instead of 480
# CLOSE_THRESHOLD_Y = 420     # ~6 feet — start tracking
# VIBRATION_THRESHOLD_Y = 500  # ~4 feet — trigger vibration motor

# # Minimum contour area to count as a real obstacle (filters noise)
# MIN_OBSTACLE_AREA = 3000

# # ============================================================
# # SETUP
# # ============================================================
# cap = cv2.VideoCapture(CAMERA_INDEX)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, RAW_WIDTH)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RAW_HEIGHT)

# if not cap.isOpened():
#     print("ERROR: Cannot open camera")
#     exit()

# # Background subtractor — learns what the "normal" scene looks like.
# # Since the camera is FIXED in place, this works very well.
# # Anything new that enters the scene gets detected as foreground.
# bg_subtractor = cv2.createBackgroundSubtractorMOG2(
#     history=500,        # frames to learn background
#     varThreshold=50,    # sensitivity (lower = more sensitive)
#     detectShadows=True  # detect shadows separately
# )

# # Morphology kernel for cleaning up the detection mask
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

# # Arduino serial connection (uncomment when hardware is ready)
# # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
# # import time; time.sleep(2)  # wait for Arduino to reset


# # ============================================================
# # HELPER FUNCTIONS
# # ============================================================
# def get_zone(cx):
#     """Which third of the ROTATED frame is this x-coordinate in?"""
#     if cx < FRAME_WIDTH // 3:
#         return "LEFT"
#     elif cx < 2 * FRAME_WIDTH // 3:
#         return "CENTER"
#     else:
#         return "RIGHT"


# # def process_frame(frame):
# #     """
# #     Takes a raw camera frame, rotates it, detects obstacles.
# #     Returns (obstacles, debug_frame, mask).
# #     obstacles = list of (bottom_y, zone, cx)
# #     """
# #     # STEP 1: Rotate the frame so vertical mount becomes portrait
# #     rotated = cv2.rotate(frame, ROTATION)

# #     # STEP 2: Blur to reduce camera noise
# #     blurred = cv2.GaussianBlur(rotated, (11, 11), 0)

# #     # STEP 3: Background subtraction
# #     fg_mask = bg_subtractor.apply(blurred)

# #     # STEP 4: Clean up the mask
# #     fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
# #     fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)

# #     # STEP 5: Remove shadow pixels (MOG2 marks shadows as ~127)
# #     _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

# #     # STEP 6: Find contours of detected objects
# #     contours, _ = cv2.findContours(
# #         fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
# #     )

# #     obstacles = []
# #     debug_frame = rotated.copy()

# #     # Draw zone divider lines (vertical)
# #     third = FRAME_WIDTH // 3
# #     cv2.line(debug_frame, (third, 0), (third, FRAME_HEIGHT), (255, 255, 0), 1)
# #     cv2.line(debug_frame, (third * 2, 0), (third * 2, FRAME_HEIGHT), (255, 255, 0), 1)
# #     cv2.putText(debug_frame, "LEFT", (10, 25),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
# #     cv2.putText(debug_frame, "CENTER", (third + 10, 25),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
# #     cv2.putText(debug_frame, "RIGHT", (third * 2 + 10, 25),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

# #     # Draw threshold lines (horizontal)
# #     cv2.line(debug_frame, (0, CLOSE_THRESHOLD_Y),
# #              (FRAME_WIDTH, CLOSE_THRESHOLD_Y), (0, 255, 255), 1)
# #     cv2.putText(debug_frame, "~6ft", (5, CLOSE_THRESHOLD_Y - 5),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
# #     cv2.line(debug_frame, (0, VIBRATION_THRESHOLD_Y),
# #              (FRAME_WIDTH, VIBRATION_THRESHOLD_Y), (0, 0, 255), 1)
# #     cv2.putText(debug_frame, "~4ft VIBRATE", (5, VIBRATION_THRESHOLD_Y - 5),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

# #     for cnt in contours:
# #         area = cv2.contourArea(cnt)
# #         if area < MIN_OBSTACLE_AREA:
# #             continue

# #         x, y, w, h = cv2.boundingRect(cnt)
# #         bottom_y = y + h
# #         cx = x + w // 2

# #         if bottom_y > CLOSE_THRESHOLD_Y:
# #             zone = get_zone(cx)
# #             obstacles.append((bottom_y, zone, cx))

# #             if bottom_y > VIBRATION_THRESHOLD_Y:
# #                 color = (0, 0, 255)
# #                 label = f"{zone} CLOSE!"
# #             else:
# #                 color = (0, 255, 255)
# #                 label = f"{zone}"

# #             cv2.rectangle(debug_frame, (x, y), (x + w, y + h), color, 2)
# #             cv2.putText(debug_frame, label, (x, y - 10),
# #                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# #     return obstacles, debug_frame, fg_mask
# def process_frame(frame):
#     """
#     Detects obstacles using:
#     1. Dynamic floor sampling (adapts to any room)
#     2. Edge detection (catches walls even if same color as floor)
#     """
#     rotated = cv2.rotate(frame, ROTATION)
#     blurred = cv2.GaussianBlur(rotated, (11, 11), 0)
#     hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

#     # ── DYNAMIC FLOOR SAMPLING ──
#     # Sample a strip at the very bottom center of the frame.
#     # This is ALWAYS floor because the walker is right there.
#     h, w = rotated.shape[:2]
#     sample_strip = hsv[h - 40 : h - 5, w // 4 : 3 * w // 4]

#     # Calculate the mean and standard deviation of the floor color
#     h_mean = np.mean(sample_strip[:, :, 0])
#     s_mean = np.mean(sample_strip[:, :, 1])
#     v_mean = np.mean(sample_strip[:, :, 2])
#     h_std = np.std(sample_strip[:, :, 0])
#     s_std = np.std(sample_strip[:, :, 1])
#     v_std = np.std(sample_strip[:, :, 2])

#     # Build a range that covers the floor's color with some tolerance
#     # The multiplier controls how strict the match is (2.0 = lenient, 1.0 = strict)
#     tolerance = 2.0
#     floor_lower = np.array([
#         max(0, h_mean - h_std * tolerance - 10),
#         max(0, s_mean - s_std * tolerance - 15),
#         max(0, v_mean - v_std * tolerance - 25)
#     ], dtype=np.uint8)
#     floor_upper = np.array([
#         min(180, h_mean + h_std * tolerance + 10),
#         min(255, s_mean + s_std * tolerance + 15),
#         min(255, v_mean + v_std * tolerance + 25)
#     ], dtype=np.uint8)

#     # Mask: floor pixels = white
#     floor_mask = cv2.inRange(hsv, floor_lower, floor_upper)

#     # ── EDGE DETECTION (catches same-color walls) ──
#     # Edges mark where surfaces change angle — floor-to-wall transitions
#     gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
#     edges = cv2.Canny(gray, 50, 150)

#     # Thicken edges so they act as barriers
#     edge_dilated = cv2.dilate(edges, kernel, iterations=2)

#     # ── COMBINE BOTH METHODS ──
#     # Start with "not floor" mask
#     obstacle_mask = cv2.bitwise_not(floor_mask)

#     # Add edges as additional obstacles
#     # This catches walls that are floor-colored because the edge
#     # between floor and wall still shows up
#     obstacle_mask = cv2.bitwise_or(obstacle_mask, edge_dilated)

#     # Ignore the top quarter (ceiling, far away, irrelevant)
#     obstacle_mask[0 : FRAME_HEIGHT // 4, :] = 0

#     # Clean up
#     obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
#     obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_OPEN, kernel, iterations=2)

#     # ── FIND CONTOURS ──
#     contours, _ = cv2.findContours(
#         obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#     )

#     obstacles = []
#     debug_frame = rotated.copy()

#     # Draw the floor sample region so you can see what it's using
#     cv2.rectangle(debug_frame, (w // 4, h - 40), (3 * w // 4, h - 5), (0, 255, 0), 1)
#     cv2.putText(debug_frame, "floor sample", (w // 4 + 5, h - 45),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

#     # Draw zone dividers
#     third = FRAME_WIDTH // 3
#     cv2.line(debug_frame, (third, 0), (third, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.line(debug_frame, (third * 2, 0), (third * 2, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.putText(debug_frame, "LEFT", (10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "CENTER", (third + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "RIGHT", (third * 2 + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#     # Draw threshold lines
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

#         x, y, w_box, h_box = cv2.boundingRect(cnt)
#         bottom_y = y + h_box
#         cx = x + w_box // 2

#         if bottom_y > CLOSE_THRESHOLD_Y:
#             zone = get_zone(cx)
#             obstacles.append((bottom_y, zone, cx))

#             if bottom_y > VIBRATION_THRESHOLD_Y:
#                 color = (0, 0, 255)
#                 label = f"{zone} CLOSE!"
#             else:
#                 color = (0, 255, 255)
#                 label = f"{zone}"

#             cv2.rectangle(debug_frame, (x, y), (x + w_box, y + h_box), color, 2)
#             cv2.putText(debug_frame, label, (x, y - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#     return obstacles, debug_frame, obstacle_mask


# def decide_action(obstacles):
#     """
#     Given detected obstacles, decide nudge direction and vibration.
#     Returns (nudge_direction, should_vibrate)
#     """
#     if not obstacles:
#         return None, False

#     should_vibrate = any(by > VIBRATION_THRESHOLD_Y for by, _, _ in obstacles)

#     closest = max(obstacles, key=lambda o: o[0])
#     _, zone, _ = closest

#     if zone == "RIGHT":
#         nudge = "LEFT"
#     elif zone == "LEFT":
#         nudge = "RIGHT"
#     elif zone == "CENTER":
#         left_obstacles = [o for o in obstacles if o[1] == "LEFT"]
#         right_obstacles = [o for o in obstacles if o[1] == "RIGHT"]
#         if len(left_obstacles) <= len(right_obstacles):
#             nudge = "LEFT"
#         else:
#             nudge = "RIGHT"
#     else:
#         nudge = None

#     return nudge, should_vibrate


# def send_command(nudge, vibrate):
#     """Send commands to Arduino. Replace prints with serial writes."""
#     if vibrate:
#         print(">>> VIBRATION MOTOR: ON (obstacle within ~4 feet)")
#         # ser.write(b'V')

#     if nudge == "LEFT":
#         print(">>> NUDGE LEFT")
#         # ser.write(b'L')
#     elif nudge == "RIGHT":
#         print(">>> NUDGE RIGHT")
#         # ser.write(b'R')
#     else:
#         if not vibrate:
#             print(">>> ALL CLEAR")
#             # ser.write(b'S')


# # ============================================================
# # MOUSE CALLBACK FOR CALIBRATION
# # ============================================================
# def mouse_callback(event, x, y, flags, param):
#     """Click anywhere on the debug window to print pixel coordinates."""
#     if event == cv2.EVENT_LBUTTONDOWN:
#         zone = get_zone(x)
#         print(f"Clicked: x={x}, y={y} | Zone: {zone}"
#               f" | {'VIBRATE RANGE' if y > VIBRATION_THRESHOLD_Y else 'CLOSE' if y > CLOSE_THRESHOLD_Y else 'far'}")


# # ============================================================
# # MAIN LOOP
# # ============================================================
# print("Smart Walker Vision System (Vertical Camera)")
# print(f"Rotated frame size: {FRAME_WIDTH}x{FRAME_HEIGHT}")
# print("Press 'q' to quit")
# print("Press 'c' to capture a calibration snapshot")
# print("Click on the debug window to check pixel coordinates")
# print("-" * 50)

# cv2.namedWindow("Walker Vision - Debug")
# cv2.setMouseCallback("Walker Vision - Debug", mouse_callback)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("ERROR: Lost camera feed")
#         break

#     obstacles, debug_frame, mask = process_frame(frame)
#     nudge, vibrate = decide_action(obstacles)
#     send_command(nudge, vibrate)

#     cv2.imshow("Walker Vision - Debug", debug_frame)
#     cv2.imshow("Detection Mask", mask)

#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('q'):
#         break
#     elif key == ord('c'):
#         cv2.imwrite("calibration_snapshot.png", debug_frame)
#         print("Saved calibration_snapshot.png")

# cap.release()
# cv2.destroyAllWindows()
# import cv2
# import numpy as np
# import time
# # import serial  # uncomment when Arduino is connected

# # ============================================================
# # CONFIGURATION
# # ============================================================

# import serial

# ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
# time.sleep(2)
# CAMERA_INDEX = 0

# # Set to True when running on Nvidia Jetson with USB camera
# USE_JETSON = False

# # Raw camera resolution (before rotation)
# RAW_WIDTH = 640
# RAW_HEIGHT = 480

# # After 90° rotation, width and height swap
# FRAME_WIDTH = RAW_HEIGHT   # 480
# FRAME_HEIGHT = RAW_WIDTH   # 640

# ROTATION = cv2.ROTATE_90_COUNTERCLOCKWISE
# # ROTATION = cv2.ROTATE_90_CLOCKWISE

# # Y-pixel thresholds on the ROTATED frame (calibrate these)
# CLOSE_THRESHOLD_Y = 420     # ~6 feet
# VIBRATION_THRESHOLD_Y = 500  # ~4 feet

# # Minimum contour area to count as obstacle
# MIN_OBSTACLE_AREA = 8000

# # Floor detection tolerance (lower = stricter, catches walls better)
# # Start at 25. If floor itself gets flagged as obstacle, increase.
# # If walls get missed, decrease.
# FLOOR_COLOR_TOLERANCE = 45

# # ============================================================
# # JETSON / CAMERA SETUP
# # ============================================================
# if USE_JETSON:
#     # USB camera on Jetson — GStreamer pipeline gives better performance
#     gst_pipeline = (
#         f"v4l2src device=/dev/video{CAMERA_INDEX} ! "
#         f"video/x-raw, width={RAW_WIDTH}, height={RAW_HEIGHT}, framerate=30/1 ! "
#         f"videoconvert ! video/x-raw, format=BGR ! appsink drop=1"
#     )
#     cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
# else:
#     cap = cv2.VideoCapture(CAMERA_INDEX)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, RAW_WIDTH)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RAW_HEIGHT)

# if not cap.isOpened():
#     print("ERROR: Cannot open camera")
#     if USE_JETSON:
#         print("On Jetson, check: ls /dev/video*")
#         print("Try setting CAMERA_INDEX to a different number")
#     exit()

# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

# # Arduino serial — on Jetson the port is usually /dev/ttyACM0 or /dev/ttyUSB0
# # ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
# # time.sleep(2)


# # ============================================================
# # HELPER FUNCTIONS
# # ============================================================
# def get_zone(cx):
#     if cx < FRAME_WIDTH // 3:
#         return "LEFT"
#     elif cx < 2 * FRAME_WIDTH // 3:
#         return "CENTER"
#     else:
#         return "RIGHT"


# def detect_floor_region(hsv_frame):
#     """
#     Grows the floor region UPWARD from the bottom of the frame.
    
#     Instead of saying "anything this color = floor" (which matches walls),
#     this starts from pixels we KNOW are floor (bottom of frame) and only
#     expands into neighboring pixels that look similar.
    
#     A wall 6 feet away won't be reached because the growth stops at
#     the floor-to-wall transition (edge, shadow, color change).
#     """
#     h, w = hsv_frame.shape[:2]

#     # Step 1: Sample the bottom strip to get floor color
#     sample = hsv_frame[h - 40 : h - 5, w // 4 : 3 * w // 4]
#     h_mean = int(np.mean(sample[:, :, 0]))
#     s_mean = int(np.mean(sample[:, :, 1]))
#     v_mean = int(np.mean(sample[:, :, 2]))

#     # Step 2: Create a seed mask — mark the bottom strip as "definitely floor"
#     seed_mask = np.zeros((h, w), dtype=np.uint8)
#     seed_mask[h - 40 : h - 5, :] = 255

#     # Step 3: Create a color-similarity mask
#     # Pixels that COULD be floor based on color alone
#     tol = FLOOR_COLOR_TOLERANCE
#     floor_lower = np.array([
#         max(0, h_mean - tol),
#         max(0, s_mean - tol * 2),
#         max(0, v_mean - tol * 2)
#     ], dtype=np.uint8)
#     floor_upper = np.array([
#         min(180, h_mean + tol),
#         min(255, s_mean + tol * 2),
#         min(255, v_mean + tol * 2)
#     ], dtype=np.uint8)
#     color_match = cv2.inRange(hsv_frame, floor_lower, floor_upper)

#     # Step 4: Flood fill — grow from seed through color-matched pixels only
#     # We iterate upward row by row. A pixel is floor ONLY if:
#     #   a) it matches the floor color, AND
#     #   b) the pixel below it (or near it) was already marked as floor
#     # This prevents the wall from being classified as floor even if
#     # it's the same color, because there's no connected path from
#     # the bottom of the frame to the wall through floor-colored pixels
#     # without crossing the transition edge.

#     floor_mask = seed_mask.copy()

#     # Dilate the seed upward repeatedly, but only into color-matched areas
#     grow_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
#     for _ in range(h // 3):  # enough iterations to reach the top if needed
#         expanded = cv2.dilate(floor_mask, grow_kernel, iterations=1)
#         # Only keep expanded pixels that match floor color
#         expanded = cv2.bitwise_and(expanded, color_match)
#         # If nothing new was added, stop early
#         if np.array_equal(expanded | floor_mask, floor_mask):
#             break
#         floor_mask = expanded | floor_mask

#     # Clean up small holes in the floor region
#     floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

#     return floor_mask


# def process_frame(frame):
#     """
#     Detects obstacles using:
#     1. Region-growing floor detection (grows up from bottom, stops at walls)
#     2. Edge detection (catches same-color walls where growth might leak)
#     """
#     rotated = cv2.rotate(frame, ROTATION)
#     blurred = cv2.GaussianBlur(rotated, (11, 11), 0)
#     hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
#     h, w = rotated.shape[:2]

#     # ── FLOOR DETECTION (region growing) ──
#     floor_mask = detect_floor_region(hsv)

#     # ── EDGE DETECTION (safety net for same-color walls) ──
#     gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
#     edges = cv2.Canny(gray, 100, 200)
#     edge_dilated = cv2.dilate(edges, kernel, iterations=1)

#     # ── COMBINE ──
#     obstacle_mask = cv2.bitwise_not(floor_mask)

#     # Only use edges where they are OUTSIDE the floor region.
#     # This prevents floor texture edges from being counted as obstacles.
#     edges_outside_floor = cv2.bitwise_and(edge_dilated, obstacle_mask)
#     obstacle_mask = cv2.bitwise_or(obstacle_mask, edges_outside_floor)

#     # Ignore top quarter (ceiling, irrelevant)
#     obstacle_mask[0 : FRAME_HEIGHT // 3, :] = 0

#     # Clean up
#     obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
#     obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_OPEN, kernel, iterations=2)

#     # ── FIND CONTOURS ──
#     contours, _ = cv2.findContours(
#         obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#     )

#     obstacles = []
#     debug_frame = rotated.copy()

#     # Draw floor sample region
#     cv2.rectangle(debug_frame, (w // 4, h - 40), (3 * w // 4, h - 5), (0, 255, 0), 1)
#     cv2.putText(debug_frame, "floor sample", (w // 4 + 5, h - 45),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

#     # Draw floor region overlay (green tint on detected floor)
#     floor_overlay = debug_frame.copy()
#     floor_overlay[floor_mask > 0] = (
#         floor_overlay[floor_mask > 0] * 0.7 + np.array([0, 80, 0]) * 0.3
#     ).astype(np.uint8)
#     debug_frame = floor_overlay

#     # Draw zone dividers
#     third = FRAME_WIDTH // 3
#     cv2.line(debug_frame, (third, 0), (third, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.line(debug_frame, (third * 2, 0), (third * 2, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.putText(debug_frame, "LEFT", (10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "CENTER", (third + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "RIGHT", (third * 2 + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#     # Draw threshold lines
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

#         x, y, w_box, h_box = cv2.boundingRect(cnt)
#         bottom_y = y + h_box
#         cx = x + w_box // 2

#         if bottom_y > CLOSE_THRESHOLD_Y:
#             zone = get_zone(cx)
#             obstacles.append((bottom_y, zone, cx))

#             if bottom_y > VIBRATION_THRESHOLD_Y:
#                 color = (0, 0, 255)
#                 label = f"{zone} CLOSE!"
#             else:
#                 color = (0, 255, 255)
#                 label = f"{zone}"

#             cv2.rectangle(debug_frame, (x, y), (x + w_box, y + h_box), color, 2)
#             cv2.putText(debug_frame, label, (x, y - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#     return obstacles, debug_frame, obstacle_mask


# def decide_action(obstacles):
#     if not obstacles:
#         return None, False

#     should_vibrate = any(by > VIBRATION_THRESHOLD_Y for by, _, _ in obstacles)

#     closest = max(obstacles, key=lambda o: o[0])
#     _, zone, _ = closest

#     if zone == "RIGHT":
#         nudge = "LEFT"
#     elif zone == "LEFT":
#         nudge = "RIGHT"
#     elif zone == "CENTER":
#         left_obstacles = [o for o in obstacles if o[1] == "LEFT"]
#         right_obstacles = [o for o in obstacles if o[1] == "RIGHT"]
#         nudge = "LEFT" if len(left_obstacles) <= len(right_obstacles) else "RIGHT"
#     else:
#         nudge = None

#     return nudge, should_vibrate


# # def send_command(nudge, vibrate):
# #     if vibrate:
# #         print(">>> VIBRATION MOTOR: ON")
# #         # ser.write(b'V')
# #     if nudge == "LEFT":
# #         print(">>> NUDGE LEFT")
# #         # ser.write(b'L')
# #     elif nudge == "RIGHT":
# #         print(">>> NUDGE RIGHT")
# #         # ser.write(b'R')
# #     else:
# #         if not vibrate:
# #             print(">>> ALL CLEAR")
# #             # ser.write(b'S')
# last_command = None

# def send_command(nudge, vibrate):
#     global last_command

#     command = ""

#     if nudge == "LEFT":
#         command += "L"
#     elif nudge == "RIGHT":
#         command += "R"

#     if vibrate:
#         command += "V"

#     if command == "":
#         command = "S"

#     if command != last_command:
#         print(f">>> Sending: {command}")
#         ser.write((command + "\n").encode())
#         last_command = command

# def mouse_callback(event, x, y, flags, param):
#     if event == cv2.EVENT_LBUTTONDOWN:
#         zone = get_zone(x)
#         print(f"Clicked: x={x}, y={y} | Zone: {zone}"
#               f" | {'VIBRATE' if y > VIBRATION_THRESHOLD_Y else 'CLOSE' if y > CLOSE_THRESHOLD_Y else 'far'}")


# # ============================================================
# # MAIN LOOP
# # ============================================================
# print("Smart Walker Vision System")
# print(f"Rotated frame: {FRAME_WIDTH}x{FRAME_HEIGHT}")
# print(f"Jetson mode: {USE_JETSON}")
# print("Press 'q' to quit | 'c' for snapshot | click for coordinates")
# print("-" * 50)

# cv2.namedWindow("Walker Vision - Debug")
# cv2.setMouseCallback("Walker Vision - Debug", mouse_callback)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("ERROR: Lost camera feed")
#         break

#     obstacles, debug_frame, mask = process_frame(frame)
#     nudge, vibrate = decide_action(obstacles)
#     send_command(nudge, vibrate)

#     cv2.imshow("Walker Vision - Debug", debug_frame)
#     cv2.imshow("Detection Mask", mask)
#     cv2.imshow("Floor Region", mask ^ 255)  # shows floor in white

#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('q'):
#         break
#     elif key == ord('c'):
#         cv2.imwrite("calibration_snapshot.png", debug_frame)
#         print("Saved calibration_snapshot.png")

# cap.release()
# cv2.destroyAllWindows()
# -*- coding: utf-8 -*-
# import cv2
# import numpy as np
# import time
# import serial

# # ============================================================
# # ARDUINO SERIAL SETUP
# # ============================================================
# ser = serial.Serial('COM5', 115200, timeout=1)
# time.sleep(2)

# # ============================================================
# # FSR SOCKET BROADCAST SERVER (port 5005)
# # plot_force.py on a nearby laptop connects here
# # ============================================================
# import socket
# import threading

# clients = []
# clients_lock = threading.Lock()

# def handle_client(conn):
#     with clients_lock:
#         clients.append(conn)
#     try:
#         while True:
#             if conn.recv(1) == b'':
#                 break
#     except:
#         pass
#     finally:
#         with clients_lock:
#             if conn in clients:
#                 clients.remove(conn)
#         conn.close()

# def start_server(port=5005):
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     server.bind(('0.0.0.0', port))
#     server.listen(5)
#     print(f"FSR broadcast server listening on port {port}")
#     while True:
#         conn, addr = server.accept()
#         print(f"plot_force client connected: {addr}")
#         threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

# threading.Thread(target=start_server, daemon=True).start()

# # Latest distance reading from Arduino serial (updated each loop)
# tof_dist_mm = None

# # Distance thresholds in millimeters
# VIBRATE_DISTANCE_MM = 1830    # 6 feet — warn user first
# CLOSE_DISTANCE_MM = 1220      # 4 feet — steer if user hasn't reacted

# # ============================================================
# # CONFIGURATION
# # ============================================================
# CAMERA_INDEX = 0

# # Set to True when running on Nvidia Jetson with USB camera
# USE_JETSON = False

# # Raw camera resolution (before rotation)
# RAW_WIDTH = 640
# RAW_HEIGHT = 480

# # After 90 degree rotation, width and height swap
# FRAME_WIDTH = RAW_HEIGHT   # 480
# FRAME_HEIGHT = RAW_WIDTH   # 640

# ROTATION = cv2.ROTATE_90_COUNTERCLOCKWISE
# # ROTATION = cv2.ROTATE_90_CLOCKWISE

# # Y-pixel thresholds on the ROTATED frame (calibrate these)
# CLOSE_THRESHOLD_Y = 420     # ~6 feet
# VIBRATION_THRESHOLD_Y = 500  # ~4 feet

# # Minimum contour area to count as obstacle
# MIN_OBSTACLE_AREA = 8000

# # Floor detection tolerance (lower = stricter, catches walls better)
# FLOOR_COLOR_TOLERANCE = 45

# # ============================================================
# # JETSON / CAMERA SETUP
# # ============================================================
# if USE_JETSON:
#     gst_pipeline = (
#         f"v4l2src device=/dev/video{CAMERA_INDEX} ! "
#         f"video/x-raw, width={RAW_WIDTH}, height={RAW_HEIGHT}, framerate=30/1 ! "
#         f"videoconvert ! video/x-raw, format=BGR ! appsink drop=1"
#     )
#     cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
# else:
#     cap = cv2.VideoCapture(CAMERA_INDEX)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, RAW_WIDTH)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RAW_HEIGHT)

# if not cap.isOpened():
#     print("ERROR: Cannot open camera")
#     if USE_JETSON:
#         print("On Jetson, check: ls /dev/video*")
#         print("Try setting CAMERA_INDEX to a different number")
#     exit()

# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))


# # ============================================================
# # HELPER FUNCTIONS
# # ============================================================
# def get_zone(cx):
#     if cx < FRAME_WIDTH // 3:
#         return "LEFT"
#     elif cx < 2 * FRAME_WIDTH // 3:
#         return "CENTER"
#     else:
#         return "RIGHT"


# def read_serial():
#     """Read all pending Arduino serial lines. Updates tof_dist_mm, broadcasts FSR data."""
#     global tof_dist_mm
#     while ser.in_waiting:
#         try:
#             line = ser.readline().decode(errors='ignore').strip()
#         except Exception:
#             break
#         if line.startswith("D:"):
#             try:
#                 val = int(line[2:])
#                 if 20 <= val <= 4000:
#                     tof_dist_mm = val
#             except ValueError:
#                 pass
#         elif "," in line:
#             try:
#                 left, right = line.split(",")
#                 int(left); int(right)
#                 msg = (line + "\n").encode()
#                 with clients_lock:
#                     for conn in list(clients):
#                         try:
#                             conn.sendall(msg)
#                         except:
#                             clients.remove(conn)
#             except:
#                 pass


# def detect_floor_region(hsv_frame):
#     """
#     Grows the floor region UPWARD from the bottom of the frame.
#     Starts from pixels we KNOW are floor (bottom of frame) and only
#     expands into neighboring pixels that look similar.
#     """
#     h, w = hsv_frame.shape[:2]

#     sample = hsv_frame[h - 40 : h - 5, w // 4 : 3 * w // 4]
#     h_mean = int(np.mean(sample[:, :, 0]))
#     s_mean = int(np.mean(sample[:, :, 1]))
#     v_mean = int(np.mean(sample[:, :, 2]))

#     seed_mask = np.zeros((h, w), dtype=np.uint8)
#     seed_mask[h - 40 : h - 5, :] = 255

#     tol = FLOOR_COLOR_TOLERANCE
#     floor_lower = np.array([
#         max(0, h_mean - tol),
#         max(0, s_mean - tol * 2),
#         max(0, v_mean - tol * 2)
#     ], dtype=np.uint8)
#     floor_upper = np.array([
#         min(180, h_mean + tol),
#         min(255, s_mean + tol * 2),
#         min(255, v_mean + tol * 2)
#     ], dtype=np.uint8)
#     color_match = cv2.inRange(hsv_frame, floor_lower, floor_upper)

#     floor_mask = seed_mask.copy()
#     grow_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
#     for _ in range(h // 3):
#         expanded = cv2.dilate(floor_mask, grow_kernel, iterations=1)
#         expanded = cv2.bitwise_and(expanded, color_match)
#         if np.array_equal(expanded | floor_mask, floor_mask):
#             break
#         floor_mask = expanded | floor_mask

#     floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
#     return floor_mask


# def process_frame(frame):
#     """
#     Detects obstacles using:
#     1. Region-growing floor detection (grows up from bottom, stops at walls)
#     2. Edge detection (catches same-color walls where growth might leak)
#     """
#     rotated = cv2.rotate(frame, ROTATION)
#     blurred = cv2.GaussianBlur(rotated, (11, 11), 0)
#     hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
#     h, w = rotated.shape[:2]

#     # -- FLOOR DETECTION (region growing) --
#     floor_mask = detect_floor_region(hsv)

#     # -- EDGE DETECTION (safety net for same-color walls) --
#     gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
#     edges = cv2.Canny(gray, 100, 200)
#     edge_dilated = cv2.dilate(edges, kernel, iterations=1)

#     # -- COMBINE --
#     obstacle_mask = cv2.bitwise_not(floor_mask)
#     edges_outside_floor = cv2.bitwise_and(edge_dilated, obstacle_mask)
#     obstacle_mask = cv2.bitwise_or(obstacle_mask, edges_outside_floor)

#     # Ignore top third (ceiling, irrelevant)
#     obstacle_mask[0 : FRAME_HEIGHT // 3, :] = 0

#     # Clean up
#     obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
#     obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_OPEN, kernel, iterations=2)

#     # -- FIND CONTOURS --
#     contours, _ = cv2.findContours(
#         obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#     )

#     obstacles = []
#     debug_frame = rotated.copy()

#     # Draw floor sample region
#     cv2.rectangle(debug_frame, (w // 4, h - 40), (3 * w // 4, h - 5), (0, 255, 0), 1)
#     cv2.putText(debug_frame, "floor sample", (w // 4 + 5, h - 45),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

#     # Draw floor region overlay (green tint on detected floor)
#     floor_overlay = debug_frame.copy()
#     floor_overlay[floor_mask > 0] = (
#         floor_overlay[floor_mask > 0] * 0.7 + np.array([0, 80, 0]) * 0.3
#     ).astype(np.uint8)
#     debug_frame = floor_overlay

#     # Draw zone dividers
#     third = FRAME_WIDTH // 3
#     cv2.line(debug_frame, (third, 0), (third, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.line(debug_frame, (third * 2, 0), (third * 2, FRAME_HEIGHT), (255, 255, 0), 1)
#     cv2.putText(debug_frame, "LEFT", (10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "CENTER", (third + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
#     cv2.putText(debug_frame, "RIGHT", (third * 2 + 10, 25),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

#     # Draw threshold lines
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

#         x, y, w_box, h_box = cv2.boundingRect(cnt)
#         bottom_y = y + h_box
#         cx = x + w_box // 2

#         if bottom_y > CLOSE_THRESHOLD_Y:
#             zone = get_zone(cx)
#             obstacles.append((bottom_y, zone, cx))

#             if bottom_y > VIBRATION_THRESHOLD_Y:
#                 color = (0, 0, 255)
#                 label = f"{zone} CLOSE!"
#             else:
#                 color = (0, 255, 255)
#                 label = f"{zone}"

#             cv2.rectangle(debug_frame, (x, y), (x + w_box, y + h_box), color, 2)
#             cv2.putText(debug_frame, label, (x, y - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

#     return obstacles, debug_frame, obstacle_mask


# def decide_action(obstacles, tof_distance_mm):
#     """
#     Uses ToF sensor for accurate center distance.
#     Uses camera for left/right zone detection.
#     Falls back to camera-only if sensor unavailable.
#     """
#     should_vibrate = False
#     nudge = None

#     # -- ToF sensor: accurate center distance --
#     center_close = False
#     if tof_distance_mm is not None:
#         if tof_distance_mm < VIBRATE_DISTANCE_MM:
#             should_vibrate = True
#         if tof_distance_mm < CLOSE_DISTANCE_MM:
#             center_close = True

#     # -- Camera: zone detection --
#     left_blocked = any(o[1] == "LEFT" and o[0] > CLOSE_THRESHOLD_Y for o in obstacles)
#     right_blocked = any(o[1] == "RIGHT" and o[0] > CLOSE_THRESHOLD_Y for o in obstacles)

#     if center_close or any(o[1] == "CENTER" and o[0] > CLOSE_THRESHOLD_Y for o in obstacles):
#         # Something ahead -- go toward the clearer side
#         if left_blocked and not right_blocked:
#             nudge = "RIGHT"
#         elif right_blocked and not left_blocked:
#             nudge = "LEFT"
#         elif not left_blocked and not right_blocked:
#             nudge = "LEFT"
#         else:
#             left_count = sum(1 for o in obstacles if o[1] == "LEFT")
#             right_count = sum(1 for o in obstacles if o[1] == "RIGHT")
#             nudge = "LEFT" if left_count <= right_count else "RIGHT"
#     elif right_blocked:
#         nudge = "LEFT"
#     elif left_blocked:
#         nudge = "RIGHT"

#     # Camera-only vibration fallback (when no ToF sensor)
#     if tof_distance_mm is None and obstacles:
#         closest = max(obstacles, key=lambda o: o[0])
#         if closest[0] > VIBRATION_THRESHOLD_Y:
#             should_vibrate = True

#     return nudge, should_vibrate


# last_command = None
# last_command_time = 0

# def send_command(nudge, vibrate):
#     global last_command, last_command_time

#     # Only send commands every 200ms, not every frame
#     now = time.time()
#     if now - last_command_time < 0.2:
#         return
#     last_command_time = now

#     command = ""

#     if nudge == "LEFT":
#         command += "L"
#     elif nudge == "RIGHT":
#         command += "R"

#     if vibrate:
#         command += "V"

#     if command == "":
#         command = "S"

#     if command != last_command:
#         print(f">>> Sending: {command}")
#         ser.write((command + "\n").encode())
#         last_command = command


# def mouse_callback(event, x, y, flags, param):
#     if event == cv2.EVENT_LBUTTONDOWN:
#         zone = get_zone(x)
#         print(f"Clicked: x={x}, y={y} | Zone: {zone}"
#               f" | {'VIBRATE' if y > VIBRATION_THRESHOLD_Y else 'CLOSE' if y > CLOSE_THRESHOLD_Y else 'far'}")


# # ============================================================
# # MAIN LOOP
# # ============================================================
# print("Smart Walker Vision System")
# print(f"Rotated frame: {FRAME_WIDTH}x{FRAME_HEIGHT}")
# print(f"Jetson mode: {USE_JETSON}")
# print("Arduino serial: /dev/ttyACM0")
# print("Press 'q' to quit | 'c' for snapshot | click for coordinates")
# print("-" * 50)

# cv2.namedWindow("Walker Vision - Debug")
# cv2.setMouseCallback("Walker Vision - Debug", mouse_callback)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("ERROR: Lost camera feed")
#         break

#     obstacles, debug_frame, mask = process_frame(frame)
#     read_serial()
#     nudge, vibrate = decide_action(obstacles, tof_dist_mm)
#     send_command(nudge, vibrate)

#     # Show ToF distance on debug window
#     if tof_dist_mm is not None:
#         dist_text = f"ToF: {tof_dist_mm}mm ({tof_dist_mm/304.8:.1f}ft)"
#         if tof_dist_mm < VIBRATE_DISTANCE_MM:
#             tof_color = (0, 0, 255)
#         elif tof_dist_mm < CLOSE_DISTANCE_MM:
#             tof_color = (0, 255, 255)
#         else:
#             tof_color = (0, 255, 0)
#         cv2.putText(debug_frame, dist_text, (10, FRAME_HEIGHT - 20),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, tof_color, 2)
#     else:
#         cv2.putText(debug_frame, "ToF: no reading", (10, FRAME_HEIGHT - 20),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

#     cv2.imshow("Walker Vision - Debug", debug_frame)
#     cv2.imshow("Detection Mask", mask)
#     cv2.imshow("Floor Region", mask ^ 255)

#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('q'):
#         break
#     elif key == ord('c'):
#         cv2.imwrite("calibration_snapshot.png", debug_frame)
#         print("Saved calibration_snapshot.png")

# cap.release()
# cv2.destroyAllWindows()
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import serial
import socket
import threading

# ============================================================
# ARDUINO SERIAL SETUP
# ============================================================
ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)
ser.reset_input_buffer()

# ============================================================
# FSR SOCKET BROADCAST SERVER (port 5005)
# ============================================================
clients = []
clients_lock = threading.Lock()

def handle_client(conn):
    with clients_lock:
        clients.append(conn)
    try:
        while True:
            if conn.recv(1) == b'':
                break
    except:
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()

def start_server(port=5005):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"FSR broadcast server listening on port {port}")
    while True:
        conn, addr = server.accept()
        print(f"plot_force client connected: {addr}")
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

threading.Thread(target=start_server, daemon=True).start()

# ============================================================
# BACKGROUND SERIAL READER THREAD
# Continuously reads from Arduino so no data is missed
# ============================================================
tof_dist_mm = None

def serial_reader():
    global tof_dist_mm
    while True:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if not line:
                continue
            if line.startswith("D:"):
                try:
                    val = int(line[2:])
                    print(f"[TOF] {val}mm")
                    if 20 <= val <= 4000:
                        tof_dist_mm = val
                except ValueError:
                    pass
            elif "," in line:
                try:
                    left, right = line.split(",")
                    int(left); int(right)
                    msg = (line + "\n").encode()
                    with clients_lock:
                        for conn in list(clients):
                            try:
                                conn.sendall(msg)
                            except:
                                clients.remove(conn)
                except:
                    pass
        except Exception:
            pass

threading.Thread(target=serial_reader, daemon=True).start()

# Distance thresholds in millimeters
VIBRATE_DISTANCE_MM = 1830    # 6 feet -- warn user first
CLOSE_DISTANCE_MM = 1220      # 4 feet -- steer if user hasn't reacted

# ============================================================
# CONFIGURATION
# ============================================================
CAMERA_INDEX = 0
USE_JETSON = False

RAW_WIDTH = 640
RAW_HEIGHT = 480

FRAME_WIDTH = RAW_HEIGHT   # 480
FRAME_HEIGHT = RAW_WIDTH   # 640

ROTATION = cv2.ROTATE_90_CLOCKWISE
# ROTATION = cv2.ROTATE_90_CLOCKWISE

CLOSE_THRESHOLD_Y = 420     # ~6 feet
VIBRATION_THRESHOLD_Y = 500  # ~4 feet

MIN_OBSTACLE_AREA = 8000
FLOOR_COLOR_TOLERANCE = 45

# ============================================================
# CAMERA SETUP
# ============================================================
if USE_JETSON:
    gst_pipeline = (
        f"v4l2src device=/dev/video{CAMERA_INDEX} ! "
        f"video/x-raw, width={RAW_WIDTH}, height={RAW_HEIGHT}, framerate=30/1 ! "
        f"videoconvert ! video/x-raw, format=BGR ! appsink drop=1"
    )
    cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
else:
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RAW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RAW_HEIGHT)

if not cap.isOpened():
    print("ERROR: Cannot open camera")
    exit()

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_zone(cx):
    if cx < FRAME_WIDTH // 3:
        return "LEFT"
    elif cx < 2 * FRAME_WIDTH // 3:
        return "CENTER"
    else:
        return "RIGHT"


def detect_floor_region(hsv_frame):
    """Grows the floor region UPWARD from the bottom of the frame."""
    h, w = hsv_frame.shape[:2]

    sample = hsv_frame[h - 40 : h - 5, w // 4 : 3 * w // 4]
    h_mean = int(np.mean(sample[:, :, 0]))
    s_mean = int(np.mean(sample[:, :, 1]))
    v_mean = int(np.mean(sample[:, :, 2]))

    seed_mask = np.zeros((h, w), dtype=np.uint8)
    seed_mask[h - 40 : h - 5, :] = 255

    tol = FLOOR_COLOR_TOLERANCE
    floor_lower = np.array([
        max(0, h_mean - tol),
        max(0, s_mean - tol * 2),
        max(0, v_mean - tol * 2)
    ], dtype=np.uint8)
    floor_upper = np.array([
        min(180, h_mean + tol),
        min(255, s_mean + tol * 2),
        min(255, v_mean + tol * 2)
    ], dtype=np.uint8)
    color_match = cv2.inRange(hsv_frame, floor_lower, floor_upper)

    floor_mask = seed_mask.copy()
    grow_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    for _ in range(h // 3):
        expanded = cv2.dilate(floor_mask, grow_kernel, iterations=1)
        expanded = cv2.bitwise_and(expanded, color_match)
        if np.array_equal(expanded | floor_mask, floor_mask):
            break
        floor_mask = expanded | floor_mask

    floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return floor_mask


def process_frame(frame):
    """Detects obstacles using floor detection + edge detection."""
    rotated = cv2.rotate(frame, ROTATION)
    blurred = cv2.GaussianBlur(rotated, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    h, w = rotated.shape[:2]

    floor_mask = detect_floor_region(hsv)

    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_dilated = cv2.dilate(edges, kernel, iterations=1)

    obstacle_mask = cv2.bitwise_not(floor_mask)
    edges_outside_floor = cv2.bitwise_and(edge_dilated, obstacle_mask)
    obstacle_mask = cv2.bitwise_or(obstacle_mask, edges_outside_floor)

    obstacle_mask[0 : FRAME_HEIGHT // 3, :] = 0

    obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_OPEN, kernel, iterations=2)

    contours, _ = cv2.findContours(
        obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    obstacles = []
    debug_frame = rotated.copy()

    cv2.rectangle(debug_frame, (w // 4, h - 40), (3 * w // 4, h - 5), (0, 255, 0), 1)
    cv2.putText(debug_frame, "floor sample", (w // 4 + 5, h - 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    floor_overlay = debug_frame.copy()
    floor_overlay[floor_mask > 0] = (
        floor_overlay[floor_mask > 0] * 0.7 + np.array([0, 80, 0]) * 0.3
    ).astype(np.uint8)
    debug_frame = floor_overlay

    third = FRAME_WIDTH // 3
    cv2.line(debug_frame, (third, 0), (third, FRAME_HEIGHT), (255, 255, 0), 1)
    cv2.line(debug_frame, (third * 2, 0), (third * 2, FRAME_HEIGHT), (255, 255, 0), 1)
    cv2.putText(debug_frame, "LEFT", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    cv2.putText(debug_frame, "CENTER", (third + 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    cv2.putText(debug_frame, "RIGHT", (third * 2 + 10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

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


def decide_action(obstacles, tof_distance_mm):
    should_vibrate = False
    nudge = None

    center_close = False
    if tof_distance_mm is not None:
        if tof_distance_mm < VIBRATE_DISTANCE_MM:
            should_vibrate = True
        if tof_distance_mm < CLOSE_DISTANCE_MM:
            center_close = True

    left_blocked = any(o[1] == "LEFT" and o[0] > CLOSE_THRESHOLD_Y for o in obstacles)
    right_blocked = any(o[1] == "RIGHT" and o[0] > CLOSE_THRESHOLD_Y for o in obstacles)

    if center_close or any(o[1] == "CENTER" and o[0] > CLOSE_THRESHOLD_Y for o in obstacles):
        if left_blocked and not right_blocked:
            nudge = "RIGHT"
        elif right_blocked and not left_blocked:
            nudge = "LEFT"
        elif not left_blocked and not right_blocked:
            nudge = "LEFT"
        else:
            left_count = sum(1 for o in obstacles if o[1] == "LEFT")
            right_count = sum(1 for o in obstacles if o[1] == "RIGHT")
            nudge = "LEFT" if left_count <= right_count else "RIGHT"
    elif right_blocked:
        nudge = "LEFT"
    elif left_blocked:
        nudge = "RIGHT"

    if tof_distance_mm is None and obstacles:
        closest = max(obstacles, key=lambda o: o[0])
        if closest[0] > VIBRATION_THRESHOLD_Y:
            should_vibrate = True

    return nudge, should_vibrate


last_command = None
last_command_time = 0

def send_command(nudge, vibrate):
    global last_command, last_command_time

    now = time.time()
    if now - last_command_time < 0.2:
        return
    last_command_time = now

    command = ""

    if nudge == "LEFT":
        command += "L"
    elif nudge == "RIGHT":
        command += "R"

    if vibrate:
        command += "V"

    if command == "":
        command = "S"

    if command != last_command:
        print(f">>> Sending: {command}")
        ser.write((command + "\n").encode())
        last_command = command


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        zone = get_zone(x)
        print(f"Clicked: x={x}, y={y} | Zone: {zone}"
              f" | {'VIBRATE' if y > VIBRATION_THRESHOLD_Y else 'CLOSE' if y > CLOSE_THRESHOLD_Y else 'far'}")


# ============================================================
# MAIN LOOP
# ============================================================
print("Smart Walker Vision System")
print(f"Rotated frame: {FRAME_WIDTH}x{FRAME_HEIGHT}")
print(f"Jetson mode: {USE_JETSON}")
print("ToF sensor: via Arduino serial (background thread)")
print("Press 'q' to quit | 'c' for snapshot | click for coordinates")
print("-" * 50)

cv2.namedWindow("Walker Vision - Debug")
cv2.setMouseCallback("Walker Vision - Debug", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Lost camera feed")
        break

    obstacles, debug_frame, mask = process_frame(frame)
    nudge, vibrate = decide_action(obstacles, tof_dist_mm)
    send_command(nudge, vibrate)

    # Show ToF distance on debug window
    if tof_dist_mm is not None:
        dist_text = f"ToF: {tof_dist_mm}mm ({tof_dist_mm/304.8:.1f}ft)"
        if tof_dist_mm < VIBRATE_DISTANCE_MM:
            tof_color = (0, 0, 255)
        elif tof_dist_mm < CLOSE_DISTANCE_MM:
            tof_color = (0, 255, 255)
        else:
            tof_color = (0, 255, 0)
        cv2.putText(debug_frame, dist_text, (10, FRAME_HEIGHT - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, tof_color, 2)
    else:
        cv2.putText(debug_frame, "ToF: no reading", (10, FRAME_HEIGHT - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

    cv2.imshow("Walker Vision - Debug", debug_frame)
    cv2.imshow("Detection Mask", mask)
    cv2.imshow("Floor Region", mask ^ 255)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        cv2.imwrite("calibration_snapshot.png", debug_frame)
        print("Saved calibration_snapshot.png")

cap.release()
cv2.destroyAllWindows()
