# Task 1 – $1 Gesture Recognizer

This project implements the **$1 Unistroke Recognizer** in Python and provides a simple user interface for testing gestures using the mouse.

## Supported Gestures

The recognizer is trained with the following five gestures:

* Rectangle
* Circle
* Check
* Delete
* Pigtail

To improve recognition robustness, each gesture template is stored in both the original and reversed drawing direction.

## Requirements

* Python 3.10 or newer
* Pyglet

Install the required package:

```bash
pip install -r requirements.txt
```

## Run the Application

Start the gesture input interface with:

```bash
python gesture_input.py
```

A window will open where gestures can be drawn using the mouse.

## Controls

* **Left mouse button + drag:** Draw a gesture
* **Release mouse button:** Recognize the gesture
* **C:** Clear the canvas and start a new gesture

## Output

After a gesture is completed, the application displays:

* The recognized gesture name
* A confidence score between `0.0` and `1.0`

Higher scores indicate a closer match to the stored gesture templates.

## Project Structure

* `recognizer.py` – Implementation of the $1 Recognizer algorithm
* `gesture_input.py` – Pyglet-based user interface for gesture input

# Task 2 – Unistroke Gesture Recognition

## Overview

This task implements and evaluates LSTM-based unistroke gesture recognition using the gesture logs provided by Wobbrock et al. The notebook compares multiple LSTM architectures with the classical $1 Recognizer.

The original gesture logs are used exclusively for training. A separate custom test set was created using the provided gesture capture tool.

---

## File Structure

```text
02-unistroke-gestures/
├── unistroke_gestures.ipynb
├── recognizer.py
├── capture_gestures.py
├── datasets/
│   ├── logs/
│   │   ├── s01/
│   │   ├── s02/
│   │   └── ...
│   └── logs_custom/
│       ├── arrow/
│       ├── caret/
│       ├── check/
│       └── ...
```

### Files

* `unistroke_gestures.ipynb` – Main notebook containing data loading, preprocessing, model training, evaluation, and comparison with the $1 Recognizer.
* `recognizer.py` – Implementation of the $1 Recognizer.
* `capture_gestures.py` – Tool for recording custom gesture samples in the same XML format as the original dataset.
* `datasets/logs/` – Original gesture logs provided by Wobbrock et al. (training data).
* `datasets/logs_custom/` – User-generated gesture logs used as the test set.

---

## Custom Test Dataset

The custom test set must contain ten samples for each of the following gesture classes:

* arrow
* caret
* check
* circle
* delete_mark
* left_curly_brace
* left_sq_bracket
* pigtail
* question_mark
* rectangle
* right_curly_brace
* right_sq_bracket
* star
* triangle
* v
* x

The folder structure inside `datasets/logs_custom/` must match the gesture names exactly.

Example:

```text
datasets/logs_custom/
├── arrow/
│   ├── arrow01.xml
│   └── ...
├── check/
│   ├── check01.xml
│   └── ...
```

---

## Capturing Gestures

Run:

```bash
python capture_gestures.py
```

Controls:

* Left / Right Arrow Keys: switch gesture class
* Mouse: draw gesture
* Release mouse button: automatically save gesture
* C: clear canvas

Recorded gestures are automatically stored in:

```text
datasets/logs_custom/
```

The capture tool converts the coordinate system to match the original Wobbrock dataset format.

---

## Running the Notebook

Open and run:

```text
unistroke_gestures.ipynb
```

The notebook performs the following steps:

1. Load the original training dataset from `datasets/logs/`
2. Load the custom test dataset from `datasets/logs_custom/`
3. Preprocess all gestures
4. Train multiple LSTM configurations
5. Evaluate the models on the custom test set
6. Compare the results with the $1 Recognizer

Run all notebook cells in order.

---

## Requirements

Required Python packages:

* numpy
* matplotlib
* scikit-learn
* tensorflow
* tqdm
* pyglet
* jupyter

---

## Note
The original dataset (`datasets/logs/`) is not included in this repository due to its size.

Please place the training dataset (logs) in:

datasets/logs/

# Task 3 – Gesture Spell Game

A simple 2D gesture-controlled game built with **Python**, **Pyglet**, and the **$1 Gesture Recognizer** from Task 1.

The player controls a wizard by drawing gestures with the mouse to cast spells and defeat incoming monsters.

## Features

* Gesture-based interaction using the **$1 Recognizer**
* Four supported gestures:

  * `circle`
  * `rectangle`
  * `check`
  * `delete`
* Visual spell effects when casting gestures
* Randomly spawned monster sprites with increasing difficulty
* Score, level, and lives system
* Restart functionality using the `R` key
* Custom UI with wizard and monster sprites

## Game Rules

* A target gesture is displayed at the top of the play area.
* Draw the corresponding gesture with the mouse to cast a spell.
* Correct gestures destroy the nearest monster and award **10 points**.
* Incorrect or unclear gestures do **not** reduce lives.
* Lives are only lost when a monster reaches the wizard area.
* The number and speed of monsters increase with higher levels.
* The game ends when all lives are lost.

## Controls

| Action         | Input                               |
| -------------- | ----------------------------------- |
| Draw gesture   | Hold and drag the left mouse button |
| Submit gesture | Release the mouse button            |
| Restart game   | `R`                                 |

## How to Run

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Start the game:

```bash
python gesture_application.py
```

## Project Structure

```text
gesture_application.py   # Main game application
recognizer.py            # $1 Gesture Recognizer implementation
assets/
├── wizard.png
├── monster1.png
├── monster2.png
└── monster3.png
```

## Implementation Notes

* The game reuses the $1 Gesture Recognizer implemented in Task 1.
* Gesture templates are based on the original $1 Recognizer dataset.
* Each template is registered in both drawing directions to improve robustness.
* Visual refinements such as sprite positioning and UI alignment were iteratively improved with AI assistance.
* Core game logic, gesture handling, state management, and recognizer integration were implemented manually.
