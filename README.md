Summary
Components:
UI Integration:

The main window (MainWindow) manages the UI elements created in Qt Designer and connects their signals to respective functionalities.
Transparent frameless window for tracking visualization (Frame).
Gesture Recognition and Control:

Utilizes MediaPipe Hands (mp_hands) to detect hand landmarks.
A deep learning model (tiny_model.h5, amazing_model.h5) classifies gestures.
Custom logic links gestures to system actions (e.g., mouse clicks, scrolling, window movement).
Threads for Concurrency:

GestureRecognizer: Handles camera input, processes frames, detects gestures, and emits signals.
CursorController: Maps gestures to mouse actions (e.g., click, drag, scroll).
MouseController: Manages gesture-based window control and scrolling.
UI Functionalities:

Menu selection, camera switching, and model quality adjustments.
Various gesture-based interactions like moving the cursor, clicking, window hiding, and scrolling.


Basic Gestures
1. Single Click (LMB)
Simulates a left mouse button click at the pointer location.
Gesture: Touch your thumb to the base of your index finger.

2. Double Click
Simulates a double left mouse button click at the pointer location.
Gesture: Raise your index and middle fingers.

3. Right Click (RMB)
Simulates a right mouse button click.
Gesture: Raise your index and thumb fingers, then extend your pinky finger.

4. Left Mouse Button Hold (LMB Hold)
Useful for dragging or selecting objects.
Gesture: Perform the "OK" sign (connect your thumb and index finger in a circle).

Window Management
Move Window
Allows you to move the currently active window.
Gesture: Show a raised fist.

Minimize Window
Performed while moving a window.
Gesture: Rotate your fist downward.

Scrolling
Scroll Pages
Controls vertical or horizontal scrolling.
Gesture: Perform a pinch in the direction you want to scroll (move thumb and index fingers together).



