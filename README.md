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
