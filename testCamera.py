import cv2

cap = cv2.VideoCapture(0)  # 0 = first USB camera

if not cap.isOpened():
    print("ERROR: Cannot open camera.")
    print("Try changing the 0 to 1 or 2 if you have multiple cameras.")
    exit()

print("Camera opened successfully. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Cannot read frame.")
        break
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()