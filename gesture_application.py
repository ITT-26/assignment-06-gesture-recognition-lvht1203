# Gesture Detection Game for Task 3
# Built on the $1 recognizer from task 1.
# Controls: draw the shown gesture with the mouse to cast a spell.
import random
import pyglet
pyglet.options["shadow_window"] = False
from pyglet import shapes

from recognizer import DollarRecognizer, Point

# Window and game configuration
WIDTH = 1000
HEIGHT = 700

# Supported gesture classes
GESTURES = ["circle", "check", "delete", "rectangle"]

# Minimum recognition confidence required
MIN_SCORE = 0.62

# UI layout configuration
SIDEBAR_WIDTH = 170
PLAY_AREA_START = SIDEBAR_WIDTH
PLAY_AREA_CENTER_X = (SIDEBAR_WIDTH + WIDTH) // 2

# Enemy movement boundaries
TOP_MARGIN = 230
BOTTOM_MARGIN = 120
WIZARD_SAFE_ZONE = SIDEBAR_WIDTH + 70

# Text positions (refined with AI assistance)
TEXT_X = SIDEBAR_WIDTH // 2
TARGET_LABEL_Y = HEIGHT - 45
TARGET_TEXT_Y = HEIGHT - 90


window = pyglet.window.Window(WIDTH, HEIGHT, "Gesture Spell Game")
recognizer = DollarRecognizer()

# Load game assets
# source: https://www.flaticon.com/free-icon/wizard_7551422?related_id=7551358&origin=search
wizard_img = pyglet.image.load("assets/wizard.png")
monster_images = [
    pyglet.image.load("assets/monster1.png"), # source: https://www.flaticon.com/de/kostenloses-icon/monster_9415016
    pyglet.image.load("assets/monster2.png"), # source: https://www.flaticon.com/free-icon/monster_1236412
    pyglet.image.load("assets/monster3.png"), # source: https://www.magnific.com/icon/monster_1477182
]

# Center image origins for easier positioning
wizard_img.anchor_x = wizard_img.width // 2
wizard_img.anchor_y = wizard_img.height // 2

# Apply centered anchors to all monster sprites
for img in monster_images:
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2

# Create the player sprite
wizard = pyglet.sprite.Sprite(wizard_img, x=SIDEBAR_WIDTH // 2, y=HEIGHT // 2)
wizard.scale = 0.25 # Scale refined with AI assistance for visual balance

# Game state variables
current_points = []
drawn_lines = []
spell_lines = []
monsters = []
score = 0
lives = 5
level = 1
target_gesture = random.choice(GESTURES)
message = "Draw the target gesture to cast a spell. Press R to restart."
message_timer = 0.0
game_over = False

# Register templates in both directions to reduce
# sensitivity to drawing direction
def add_template_with_reverse(name, points):
    recognizer.add_template(name, points)
    recognizer.add_template(name, list(reversed(points)))

# Load gesture templates from the original $1 Recognizer dataset
def train_default_templates():
    add_template_with_reverse("rectangle", [
        Point(78,149),Point(78,153),Point(78,157),Point(78,160),Point(79,162),Point(79,164),Point(79,167),Point(79,169),Point(79,173),Point(79,178),Point(79,183),Point(80,189),Point(80,193),Point(80,198),Point(80,202),Point(81,208),Point(81,210),Point(81,216),Point(82,222),Point(82,224),Point(82,227),Point(83,229),Point(83,231),Point(85,230),Point(88,232),Point(90,233),Point(92,232),Point(94,233),Point(99,232),Point(102,233),Point(106,233),Point(109,234),Point(117,235),Point(123,236),Point(126,236),Point(135,237),Point(142,238),Point(145,238),Point(152,238),Point(154,239),Point(165,238),Point(174,237),Point(179,236),Point(186,235),Point(191,235),Point(195,233),Point(197,233),Point(200,233),Point(201,235),Point(201,233),Point(199,231),Point(198,226),Point(198,220),Point(196,207),Point(195,195),Point(195,181),Point(195,173),Point(195,163),Point(194,155),Point(192,145),Point(192,143),Point(192,138),Point(191,135),Point(191,133),Point(191,130),Point(190,128),Point(188,129),Point(186,129),Point(181,132),Point(173,131),Point(162,131),Point(151,132),Point(149,132),Point(138,132),Point(136,132),Point(122,131),Point(120,131),Point(109,130),Point(107,130),Point(90,132),Point(81,133),Point(76,133)
    ])

    add_template_with_reverse("check", [
        Point(91,185),Point(93,185),Point(95,185),Point(97,185),Point(100,188),Point(102,189),Point(104,190),Point(106,193),Point(108,195),Point(110,198),Point(112,201),Point(114,204),Point(115,207),Point(117,210),Point(118,212),Point(120,214),Point(121,217),Point(122,219),Point(123,222),Point(124,224),Point(126,226),Point(127,229),Point(129,231),Point(130,233),Point(129,231),Point(129,228),Point(129,226),Point(129,224),Point(129,221),Point(129,218),Point(129,212),Point(129,208),Point(130,198),Point(132,189),Point(134,182),Point(137,173),Point(143,164),Point(147,157),Point(151,151),Point(155,144),Point(161,137),Point(165,131),Point(171,122),Point(174,118),Point(176,114),Point(177,112),Point(177,114),Point(175,116),Point(173,118)
    ])

    add_template_with_reverse("delete", [
        Point(123,129),Point(123,131),Point(124,133),Point(125,136),Point(127,140),Point(129,142),Point(133,148),Point(137,154),Point(143,158),Point(145,161),Point(148,164),Point(153,170),Point(158,176),Point(160,178),Point(164,183),Point(168,188),Point(171,191),Point(175,196),Point(178,200),Point(180,202),Point(181,205),Point(184,208),Point(186,210),Point(187,213),Point(188,215),Point(186,212),Point(183,211),Point(177,208),Point(169,206),Point(162,205),Point(154,207),Point(145,209),Point(137,210),Point(129,214),Point(122,217),Point(118,218),Point(111,221),Point(109,222),Point(110,219),Point(112,217),Point(118,209),Point(120,207),Point(128,196),Point(135,187),Point(138,183),Point(148,167),Point(157,153),Point(163,145),Point(165,142),Point(172,133),Point(177,127),Point(179,127),Point(180,125)
    ])

    add_template_with_reverse("pigtail", [
        Point(81,219),Point(84,218),Point(86,220),Point(88,220),Point(90,220),Point(92,219),Point(95,220),Point(97,219),Point(99,220),Point(102,218),Point(105,217),Point(107,216),Point(110,216),Point(113,214),Point(116,212),Point(118,210),Point(121,208),Point(124,205),Point(126,202),Point(129,199),Point(132,196),Point(136,191),Point(139,187),Point(142,182),Point(144,179),Point(146,174),Point(148,170),Point(149,168),Point(151,162),Point(152,160),Point(152,157),Point(152,155),Point(152,151),Point(152,149),Point(152,146),Point(149,142),Point(148,139),Point(145,137),Point(141,135),Point(139,135),Point(134,136),Point(130,140),Point(128,142),Point(126,145),Point(122,150),Point(119,158),Point(117,163),Point(115,170),Point(114,175),Point(117,184),Point(120,190),Point(125,199),Point(129,203),Point(133,208),Point(138,213),Point(145,215),Point(155,218),Point(164,219),Point(166,219),Point(177,219),Point(182,218),Point(192,216),Point(196,213),Point(199,212),Point(201,211)
    ])

    add_template_with_reverse("circle", [
        Point(127,141),Point(124,140),Point(120,139),Point(118,139),Point(116,139),Point(111,140),Point(109,141),Point(104,144),Point(100,147),Point(96,152),Point(93,157),Point(90,163),Point(87,169),Point(85,175),Point(83,181),Point(82,190),Point(82,195),Point(83,200),Point(84,205),Point(88,213),Point(91,216),Point(96,219),Point(103,222),Point(108,224),Point(111,224),Point(120,224),Point(133,223),Point(142,222),Point(152,218),Point(160,214),Point(167,210),Point(173,204),Point(178,198),Point(179,196),Point(182,188),Point(182,177),Point(178,167),Point(170,150),Point(163,138),Point(152,130),Point(143,129),Point(140,131),Point(129,136),Point(126,139)
    ])
    
train_default_templates()


def next_target():
    """Select a new target gesture different from the previous one."""
    global target_gesture
    old = target_gesture
    choices = [g for g in GESTURES if g != old]
    target_gesture = random.choice(choices)


def reset_game():
    """Restore the initial game state."""
    global current_points, drawn_lines, spell_lines, monsters, score, lives, level, message, message_timer, game_over
    current_points = []
    drawn_lines = []
    spell_lines = []
    monsters = []
    score = 0
    lives = 5
    level = 1
    message = "Game restarted. Draw the target gesture."
    message_timer = 2.0
    game_over = False
    next_target()


def spawn_monster():
    """Spawn a random enemy outside the right edge of the play area."""
    y = random.randint(BOTTOM_MARGIN, HEIGHT - TOP_MARGIN) # Keep enemies away from the target UI area
    radius = random.randint(18, 28)
    speed = random.uniform(70, 100) + level * 8

    sprite = pyglet.sprite.Sprite(random.choice(monster_images), x=WIDTH + radius, y=y)
    sprite.scale = 0.2

    # Store gameplay data separately from visual sprite data
    monsters.append({"x": WIDTH + radius,"y": y,"r": radius,"speed": speed,"sprite": sprite})


def cast_spell(success, target=None):
    """Create a short visual spell effect towards a target enemy."""
    global spell_lines
    if target is None:
        return
    color = (80, 220, 120) if success else (220, 80, 80)
    sprite = target["sprite"]

    monster_width = sprite.width * sprite.scale
    monster_height = sprite.height * sprite.scale

    # Calculate a fixed hit position on the monster sprite
    # for more natural-looking spell effects
    target_x = sprite.x - monster_width * 0.35
    target_y = sprite.y + monster_height * 0.05

    spell_lines = [{"line": shapes.Line(wizard.x + 20, wizard.y + 10, target_x, target_y, width=5, color=color),"time": 0.1}]


def handle_gesture(points):
    """Recognize the gesture and update game state accordingly."""
    global score, lives, level, message, message_timer, game_over, spell_lines
    if game_over:
        return

    # Run the $1 recognizer on the collected points
    name, confidence = recognizer.recognize(points)
    if name is None:
        message = "Too few points. Draw a longer gesture."
        message_timer = 2.0
        return

    if confidence < MIN_SCORE:
        message = f"Unclear gesture: {name} ({confidence:.2f}). Try again."
        message_timer = 2.0
        target = min(monsters, key=lambda m: m["x"]) if monsters else None
        cast_spell(False, target)
        return

    # Successful recognition: destroy the nearest monster
    if name == target_gesture:
        score += 10
        level = 1 + score // 50
        message = f"Correct: {name} ({confidence:.2f}) +10"
        message_timer = 2.0
        target = min(monsters, key=lambda m: m["x"]) if monsters else None
        cast_spell(True, target)
        if target in monsters:
            monsters.remove(target)
        next_target()
    
    # Incorrect gestures only trigger visual feedback
    # and do not reduce player lives
    else:
        message = f"Wrong gesture: {name} ({confidence:.2f}). Target was {target_gesture}."
        message_timer = 2.5
        target = min(monsters, key=lambda m: m["x"]) if monsters else None
        cast_spell(False, target)


def draw_text(text,x,y,size=14,bold=False,color=(255, 255, 255, 255),anchor_x="left"):
    """Helper function for rendering text labels."""
    label = pyglet.text.Label(text, x=x, y=y, font_size=size, bold=bold, color=color, anchor_x=anchor_x)
    label.draw()


def draw_target_hint():
    """Draw the current target gesture.
    Positioning and typography were refined with AI assistance."""
    draw_text(
        "TARGET",
        PLAY_AREA_CENTER_X,
        TARGET_LABEL_Y,
        16,
        True,
        (200, 200, 200, 255),
        anchor_x="center"
    )

    draw_text(
        target_gesture.upper(),
        PLAY_AREA_CENTER_X,
        TARGET_TEXT_Y,
        32,
        True,
        (255, 230, 120, 255),
        anchor_x="center"
    )


def update(dt):
    """Main game loop: update timers, move enemies, and handle collisions."""
    global lives, message, message_timer, game_over, spell_lines
    if game_over:
        return

    if message_timer > 0:
        message_timer -= dt
        if message_timer <= 0:
            message = ""

    # Remove expired spell effects
    for effect in list(spell_lines):
        effect["time"] -= dt
        if effect["time"] <= 0:
            spell_lines.remove(effect)

    wanted = 1 if level < 4 else 2

    # Maintain a minimum number of active enemies
    while len(monsters) < wanted:
        spawn_monster()

    for monster in list(monsters):
        monster["x"] -= monster["speed"] * dt
        monster["sprite"].x = monster["x"]
        monster["sprite"].y = monster["y"]
        # Use the left edge of the sprite for collision checks
        monster_left = (monster["sprite"].x - monster["sprite"].width * monster["sprite"].scale / 2)

        if monster_left < WIZARD_SAFE_ZONE:
            monsters.remove(monster)
            lives -= 1

            message = "A monster reached you!"
            message_timer = 1.5

            if lives <= 0:
                game_over = True
                message = "Game over. Press R to restart."
                message_timer = 999


@window.event
def on_draw():
    window.clear()

    # background
    shapes.Rectangle(0, 0, WIDTH, HEIGHT, color=(25, 28, 38)).draw()
    shapes.Rectangle(0, 0, SIDEBAR_WIDTH, HEIGHT, color=(34, 43, 60)).draw()

    # wizard
    wizard.draw()

    # UI text
    draw_text("Gesture Spell", SIDEBAR_WIDTH // 2, HEIGHT - 35, 18, True, anchor_x="center")
    draw_text(f"Score: {score}", TEXT_X, HEIGHT - 70, 14, anchor_x="center")
    draw_text(f"Lives: {lives}", TEXT_X, HEIGHT - 95, 14, anchor_x="center")
    draw_text(f"Level: {level}", TEXT_X, HEIGHT - 120, 14, anchor_x="center")

    draw_target_hint()

    # monsters
    for monster in monsters:
        monster["sprite"].draw()

    # Draw spell effects and gesture lines
    for effect in spell_lines:
        effect["line"].draw()
    for line in drawn_lines:
        line.draw()
    if message:
        draw_text(message, 190, 30, 13, False, (255, 230, 120, 255))
    if game_over:
        shapes.Rectangle(260, 260, 480, 150, color=(20, 20, 25)).draw()
        draw_text("GAME OVER", 395, 355, 32, True, (255, 120, 120, 255))
        draw_text(f"Final score: {score}", 430, 320, 16)
        draw_text("Press R to restart", 420, 290, 14)


@window.event
def on_mouse_press(x, y, button, modifiers):
    """Start recording a new gesture."""
    global current_points, drawn_lines
    current_points = [Point(x, y)]
    drawn_lines = []


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    """Record gesture points and display the drawing preview."""
    global current_points, drawn_lines
    if current_points:
        last = current_points[-1]
        drawn_lines.append(shapes.Line(last.x, last.y, x, y, width=4, color=(255, 255, 255)))
    current_points.append(Point(x, y))


@window.event
def on_mouse_release(x, y, button, modifiers):
    """Finish the gesture and trigger recognition."""
    global current_points, drawn_lines
    current_points.append(Point(x, y))
    handle_gesture(current_points)
    current_points = []
    drawn_lines = []


@window.event
def on_key_press(symbol, modifiers):
    """Restart the game when R is pressed."""
    global current_points, drawn_lines, message, message_timer
    if symbol == pyglet.window.key.R:
        reset_game()


if __name__ == "__main__":
    spawn_monster()
    pyglet.clock.schedule_interval(update, 1 / 60.0)
    pyglet.app.run()
