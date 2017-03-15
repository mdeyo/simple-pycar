# Import a library of functions called 'pygame'
import pygame
import math

from car_model import Car

# Initialize the game engine
pygame.init()

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)

size = (1400, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("mdeyo car sim")
background = pygame.Surface(screen.get_size())
background.fill((0, 0, 0))
PI = math.pi

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

car = Car(RED,60,260,screen)
allSprites = pygame.sprite.Group(car)

def updateSteering(screen,car):
    pygame.draw.arc(screen, GREEN, [20, 20, 250, 200], PI / 4, 3*PI/4, 5)
    pygame.draw.arc(screen, RED, [20, 20, 250, 200], 3*PI/4, PI, 5)
    pygame.draw.arc(screen, RED, [20, 20, 250, 200], 0 , PI / 4, 5)
    pygame.draw.circle(screen, BLACK, [145, 120], 20)
    # rotate tip of needle from 145,10
    # centered at 145,120
    x1 = 145 - 145;
    y1 = 10 - 120;
    x2 = x1 * math.cos(car.steering_angle) - y1 * math.sin(car.steering_angle)
    y2 = x1 * math.sin(car.steering_angle) + y1 * math.cos(car.steering_angle)
    x = x2 + 145;
    y = y2 + 120;
    pygame.draw.line(screen, BLACK, [x, y], [145, 120], 5)

def updateSpeedometer(screen,car):
    # Select the font to use, size, bold, italics
    font = pygame.font.SysFont('Calibri', 25, True, False)

    # Render the text. "True" means anti-aliased text.
    # Black is the color. This creates an image of the
    # letters, but does not put it on the screen

    if car.gear =="D":
        gear_text = font.render("Gear: Drive", True, BLACK)
    elif car.gear == "STOP":
        gear_text = font.render("Gear: Stopped", True, BLACK)
    elif car.gear == "R":
        gear_text = font.render("Gear: Reverse", True, BLACK)
    else:
        gear_text = font.render("Gear: unknown", True, BLACK)

    # Put the image of the gear_text on the screen
    screen.blit(gear_text, [300, 40])

    speed_text = font.render("Speed: "+str(car.speed/5), True, BLACK)
    screen.blit(speed_text, [300, 60])



# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    keys = pygame.key.get_pressed()  #checking pressed keys
    if keys[pygame.K_UP]:
        car.accelerate(1)
    if keys[pygame.K_DOWN]:
        car.accelerate(-1)
    if keys[pygame.K_LEFT]:
        car.turn(-1)
    if keys[pygame.K_RIGHT]:
        car.turn(1)

    for event in pygame.event.get(): # User did something

        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop

        elif event.type == pygame.KEYDOWN:
            # print("User pressed a key.")
            if event.key == pygame.K_LEFT:
                car.turn(-1)
            elif event.key == pygame.K_RIGHT:
                car.turn(1)
            elif event.key == pygame.K_UP:
                car.accelerate(1)
            elif event.key == pygame.K_DOWN:
                car.accelerate(-1)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                car.release_down(-1)
            if event.key == pygame.K_UP:
                car.release_down(1)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("User pressed a mouse button")

    # --- Game logic should go here

    # --- Drawing code should go here

    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    # Draw a rectangle
    # pygame.draw.rect(screen, BLACK, [20, 20, 250, 100], 2)
    # Draw an ellipse, using a rectangle as the outside boundaries
    # pygame.draw.ellipse(screen, BLACK, [20, 20, 250, 100], 2)
    # Draw an arc as part of an ellipse.
    # Use radians to determine what angle to draw.
    # pygame.draw.arc(screen, BLACK, [20, 220, 250, 200], 0, PI / 2, 2)

    updateSteering(screen,car)
    updateSpeedometer(screen,car)

    # pygame.draw.arc(screen, BLUE, [20, 220, 250, 200], PI, 3 * PI / 2, 2)
    # pygame.draw.arc(screen, RED, [20, 220, 250, 200], 3 * PI / 2, 2 * PI, 2)

    # This draws a triangle using the polygon command
    # pygame.draw.polygon(screen, BLACK, [[100, 100], [0, 200], [200, 200]], 5)

    # allSprites.clear(screen, background)
    car.update(1/60)
    # allSprites.draw(screen)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)

# top = tkinter.Tk()

# C = tkinter.Canvas(top,bg="blue",height=250,width=300)

# coord = 10, 50, 240, 210
# arc = C.create_arc(coord, start=0, extent=150, fill="red")

# C.pack()
# top.mainloop()
