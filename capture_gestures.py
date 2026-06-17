import os
import xml.etree.ElementTree as ET
import math
import pyglet
pyglet.options["shadow_window"] = False
from pyglet import shapes
from recognizer import Point

# Window configuration
WIDTH = 900
HEIGHT = 650

window = pyglet.window.Window(WIDTH, HEIGHT, "Gesture Capture Tool")

current_points = []
drawn_lines = []
SAVE_DIR = "datasets/logs_custom"

LABELS = [
    "arrow",
    "caret",
    "check",
    "circle",
    "delete_mark",
    "left_curly_brace",
    "left_sq_bracket",
    "pigtail",
    "question_mark",
    "rectangle",
    "right_curly_brace",
    "right_sq_bracket",
    "star",
    "triangle",
    "v",
    "x"
]

current_label = LABELS[0]
result_text = "Draw a gesture. Release mouse to save automatically."

def save_gesture():
    global result_text

    if len(current_points) < 10:
        result_text = "Too few points."
        return

    folder = os.path.join(SAVE_DIR, current_label)
    os.makedirs(folder, exist_ok=True)

    existing = len([
        f for f in os.listdir(folder)
        if f.endswith(".xml")
    ])

    filename = f"{current_label}{existing + 1:02d}.xml"
    filepath = os.path.join(folder, filename)

    root = ET.Element("Gesture")

    for p in current_points:
        ET.SubElement(
            root,
            "Point",
            X=str(int(p.x)),
            Y=str(int(HEIGHT - p.y))
        )

    ET.ElementTree(root).write(filepath)

    result_text = (
        f"Saved {filename} "
        f"({existing + 1}/10)"
    )

# Render the current application state
@window.event
def on_draw():
    window.clear()
    title = pyglet.text.Label("Task 1: $1 Gesture Recognizer", x=20, y=HEIGHT - 30, font_size=16, color=(255, 255, 255, 255))
    title.draw()
    result = pyglet.text.Label(result_text, x=20, y=HEIGHT - 60, font_size=12, color=(255, 255, 255, 255))
    result.draw()
    label = pyglet.text.Label(
        f"Label: {current_label}",
        x=20,
        y=HEIGHT - 90,
        font_size=12,
        color=(255, 255, 0, 255)
    )

    label.draw()
    for line in drawn_lines:
        line.draw()


# Start recording a new gesture
@window.event
def on_mouse_press(x, y, button, modifiers):
    global current_points, drawn_lines, result_text
    current_points = [Point(x, y)]
    drawn_lines = []
    result_text = "Drawing..."


# Record mouse positions and draw the gesture path
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global current_points, drawn_lines
    if current_points:
        last = current_points[-1]
        drawn_lines.append(shapes.Line(last.x, last.y, x, y, width=3, color=(255, 255, 255)))
    current_points.append(Point(x, y))


@window.event
def on_mouse_release(x, y, button, modifiers):
    current_points.append(Point(x, y))
    save_gesture()


@window.event
def on_key_press(symbol, modifiers):
    global current_points, drawn_lines
    global current_label, result_text

    if symbol == pyglet.window.key.C:
        current_points = []
        drawn_lines = []
        result_text = "Canvas cleared."

    elif symbol == pyglet.window.key.RIGHT:
        idx = LABELS.index(current_label)
        current_label = LABELS[(idx + 1) % len(LABELS)]
        result_text = f"Current label: {current_label}"

    elif symbol == pyglet.window.key.LEFT:
        idx = LABELS.index(current_label)
        current_label = LABELS[(idx - 1) % len(LABELS)]
        result_text = f"Current label: {current_label}"


if __name__ == "__main__":
    pyglet.app.run()