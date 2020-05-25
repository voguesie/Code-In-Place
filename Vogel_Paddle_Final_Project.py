import tkinter
import time
import random
import math

# import numpy as np
# import matplotlib.pyplot as plt

NUMBER_OF_GAMES = 3  # Number of games before the player loses.

CANVAS_HEIGHT = 800  # height of canvas
CANVAS_WIDTH = 600  # width of canvas

# Defines the rectangular dimensions of the ball.
BALL_SIZE = 20  # diameter of ball

BALL_START_X = CANVAS_WIDTH / 3
BALL_START_Y = CANVAS_HEIGHT / 3

START_X_DIR = 9  # start x direction of the ball
START_Y_DIR = 9  # start y direction of the ball

PADDLE_WIDTH = 60  # width of the paddle
PADDLE_HEIGHT = 15  # height of the paddle
PADDLE_START_X = 0  # starting position of paddle
PADDLE_START_Y = CANVAS_HEIGHT - PADDLE_HEIGHT

NUM_BRICKS_ACROSS = 10  # number of bricks across a row
BRICK_WIDTH = CANVAS_WIDTH / NUM_BRICKS_ACROSS  # bricks span the full width of the canvas, sitting side-by-side
BRICK_HEIGHT = 15  # brick height
NUM_BRICK_ROWS = 10
BRICK_START = 80  # The bricks start at this vertical position from the top.

BRICK_COLORS = ['red', 'red', 'orange', 'orange', 'yellow', 'yellow', 'green', 'green', 'blue', 'blue', 'indigo',
                'indigo', 'violet', 'violet',
                'indigo', 'indigo', 'blue', 'blue', 'green', 'green', 'yellow', 'yellow', 'orange', 'orange']

TIME_FOR_NEW_BRICKS = 5  # The number of seconds before a new row of bricks is added.

start_playing = False


def main():
    canvas = make_canvas(CANVAS_WIDTH, CANVAS_HEIGHT, 'Bouncing Ball')

    # make paddle
    paddle = canvas.create_rectangle(PADDLE_START_X, PADDLE_START_Y, PADDLE_START_X + PADDLE_WIDTH,
                                     PADDLE_START_Y + PADDLE_HEIGHT, fill='black', outline='black')

    """
    The for loop lays out the bricks, one row at a time.
    The number of rows of bricks is NUM_BRICK_ROWS, and the number of coluns is NUM_BRICKS_ACROSS.

    The bricks list is a list of the rectangles that are created.
    """
    bricks = []  # empty list. bricks will be a list of rectangles.
    for row in range(NUM_BRICK_ROWS):
        add_brick_row(canvas, bricks, row)

    # Play game 3 times.

    num_games = 0
    win_lose = 'lose'

    while num_games < NUMBER_OF_GAMES:
        win_lose = play_game(canvas, paddle, bricks)
        global start_playing
        start_playing = False
        if (win_lose == 'win') or (win_lose == 'LOSE'):
            num_games = NUMBER_OF_GAMES  # Break loop if player wins.
        else:
            num_games += 1

    end_of_game_message(canvas, win_lose)

    canvas.mainloop()


def play_game(canvas, paddle, bricks):
    game_time = time.time()

    """
    Each iteration of the game starts with the ball being drawn.

    The ball's initial speed and direction is selected somewhat randomly. The vertical component remains the same,
    but the horizontal of the ball's direction is a random number from between -1.5 X_DIR and 1.5 X_DIR.
    """

    ball = canvas.create_oval(BALL_START_X - BALL_SIZE / 2, BALL_START_Y - BALL_SIZE / 2, BALL_START_X + BALL_SIZE / 2,
                              BALL_START_Y + BALL_SIZE / 2, fill='black')

    x_dir = random.uniform(-2 * START_X_DIR, 2 * START_X_DIR)
    y_dir = START_Y_DIR

    """
    The game will continue with the ball bouncing around until it hits the bottom.
    The variables x_dir and y_dir change by -1 whenever they hit walls, bricks, or the paddle.
    """

    while True:

        # move paddle to position of mouse
        move_paddle(canvas, paddle)

        # Move ball in x direction of x_dir, and y direction of y_dir
        # THE MOUSE MUST MOVE IN ORDER FOR THE FIRST GAME TO INITIATE!
        if start_playing:
            canvas.move(ball, x_dir, y_dir)
        canvas.update()

        """
        Change ball's horizontal direction if hit left or right wall. By multiplying by -1, the ball's direction
         will either change from positive (right) to negative (left), or from negative (left) to positive (right).
        """

        if hit_left_or_right_wall(canvas, ball):
            x_dir *= -1

        """
        Change ball's vertical direction if hits top. Hitting top should result in
        the ball's vertical direction being multiplied by -1, which will chnage the ball's direction from positive (down)
        to negative (up), or from negative (up) to positive (down).
        """
        if hit_top(canvas, ball):
            y_dir *= -1

        """
        Change ball's vertical diredction if it hits brick.
        The game will end if all bricks have been hit.
        """

        if hit_brick(canvas, ball, bricks):
            if len(bricks) == 0:
                game_result = "win"
                return game_result
            else:
                y_dir *= -1

        """
        Change ball's vertical direction if hits paddle. Additionally, change the horizontal direction if the ball hits
        to the right of center while in the direction of left, or to the left of center while in the direction of right.
        """

        if hit_paddle(canvas, ball, paddle):
            y_dir *= -1
            if (get_x(canvas, ball) < get_x(canvas, paddle) + PADDLE_WIDTH / 2 - BALL_SIZE / 2):
                x_dir = -1 * abs(x_dir)
            else:
                x_dir = abs(x_dir)

        """
        A game ends when the ball hits the bottom. If the number of games played is less than 3, then the game 
        will start over.
        """

        if hit_bottom(canvas, ball):
            canvas.delete(ball)
            game_result = 'lose'
            return game_result

        """
        Every TIME_FOR_NEW_BRICKS seconds, a row of bricks is added.
        """

        if time.time() - game_time >= TIME_FOR_NEW_BRICKS:
            for brick in bricks:
                canvas.move(brick, 0, BRICK_HEIGHT)
                brick_row = int((get_y(canvas, brick) - BRICK_START) // BRICK_HEIGHT)
                canvas.itemconfig(brick, fill=get_brick_color(brick_row))
                if (CANVAS_HEIGHT - get_y(canvas, brick) <= 2 * BRICK_HEIGHT):
                    game_result = 'LOSE'
                    return game_result
            add_brick_row(canvas, bricks, 0)
            game_time = time.time()

        time.sleep(1 / 50.)


"""
Function prints final message.
"""


def end_of_game_message(canvas, string):
    if string == 'win':
        canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, font='Courier 52', text='YOU WIN!!!!')
    else:
        canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, font='Courier 52', text='YOU LOSE!!!!')


"""
Function creates a row of bricks.
"""


def add_brick_row(canvas, bricks, row):
    for column in range(NUM_BRICKS_ACROSS):
        brick_color = get_brick_color(row)  # Get color for the brick, based on the row of bricks.
        brick = canvas.create_rectangle(column * BRICK_WIDTH, row * BRICK_HEIGHT + BRICK_START,
                                        column * BRICK_WIDTH + BRICK_WIDTH,
                                        row * BRICK_HEIGHT + BRICK_START + BRICK_HEIGHT, fill=brick_color,
                                        outline='white')
        bricks.append(brick)
    return bricks


"""
Function returns a color for the brick based on which row of the bricks the brick is in.
"""


def get_brick_color(row):
    brick_color_index = row % len(BRICK_COLORS)
    return BRICK_COLORS[brick_color_index]


"""
Function mvoes the paddle.
"""


def move_paddle(canvas, paddle):
    mouse_x = canvas.winfo_pointerx()
    if (mouse_x >= PADDLE_WIDTH / 2) and (mouse_x <= CANVAS_WIDTH - PADDLE_WIDTH / 2):
        canvas.moveto(paddle, mouse_x - PADDLE_WIDTH / 2, PADDLE_START_Y)


"""
Function returns True if the x_coordinate hits 0 (left wall) or is within the ball's diameter of the right wall.
"""


def hit_left_or_right_wall(canvas, shape):
    x = get_x(canvas, shape)
    return (x <= 0) or (x >= CANVAS_WIDTH - BALL_SIZE)


"""
Function returns True if the y-coordinate hits 0 (top wall).
"""


def hit_top(canvas, shape):  # Returns True if shape hits the top.
    y = get_y(canvas, shape)
    return (y <= 0)


"""
Function returns True if the y-coordinate is within the ball's diameter of the bottom.
"""


def hit_bottom(canvas, shape):
    y = get_y(canvas, shape)
    return (y >= CANVAS_HEIGHT - BALL_SIZE)


"""
Function returns True if the ball encounters a brick, while removing the brick from the canvas.
"""


def hit_brick(canvas, shape, bricks):
    x = get_x(canvas, shape)
    y = get_y(canvas, shape)
    overlaps = canvas.find_overlapping(x, y, x + BALL_SIZE, y + BALL_SIZE)
    brick_check = False
    for brick in bricks:
        if brick in overlaps:
            brick_check = True
            canvas.delete(brick)
            bricks.remove(brick)
    return brick_check


"""
Function returns True if the ball encounters the paddle.
"""


def hit_paddle(canvas, shape, paddle):
    x = get_x(canvas, shape)
    y = get_y(canvas, shape)
    overlaps = canvas.find_overlapping(x, y, x + BALL_SIZE, y + BALL_SIZE)
    return (paddle in overlaps)


"""
Returns the x-coordinate of shape.
"""


def get_x(canvas, shape):
    return canvas.coords(shape)[0]


"""
Returns y-coordinate of shape.
"""


def get_y(canvas, shape):
    return canvas.coords(shape)[1]


def mouse_moved(event):
    global start_playing
    start_playing = True
    return start_playing


######## DO NOT MODIFY ANY CODE BELOW THIS LINE ###########

# This function is provided to you and should not be modified.
# It creates a window that contains a drawing canvas that you
# will use to make your drawings.
def make_canvas(width, height, title):
    """
    DO NOT MODIFY
    Creates and returns a drawing canvas
    of the given int size with a blue border,
    ready for drawing.
    """
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1)

    canvas.bind("<Button>", mouse_moved)
    canvas.pack()

    return canvas


if __name__ == '__main__':
    main()
