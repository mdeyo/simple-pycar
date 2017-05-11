# Import a library of functions called 'pygame'
import pygame
import math

from car_model import Car
from lane_following import CurvedRoad

# Initialize the game engine
pygame.init()

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)

size = (1400, 600)
PI = math.pi

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

def drawRoad(screen):
    # pygame.draw.lines(screen, BLACK, False, [(100,100),(240,100)], 60)

    pygame.draw.lines(screen, GREEN, False, [(100,385),(250,385)], 10)
    pygame.draw.arc(screen,GREEN,[100,90,300,300],-PI/2,0,10)
    pygame.draw.arc(screen,GREEN,[100,90,300,300],-PI/2,0,10)

    # pygame.draw.arc(screen,BLACK,[210,90,300,300],-PI/2,0,60)
    # pygame.draw.arc(screen,BLACK,[470,100,300,300],0,PI,60)
    # pygame.draw.arc(screen,BLACK,[710,100,300,300],PI,3*PI/2,60)


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

def gameLoop(action,car,screen):
    if action==1 or action=='a' or action=='left':
        print('left')
        car.turn(-1)
    elif action==2 or action=='d' or action=='right':
        print('right')
        car.turn(1)


def learningGameLoop():
    print('more code here')

class laneFollowingCar1(Car):
    def __init__(self):
        super().__init__(RED,60,385,screen)
        self.car = super().car
        self.car.constant_speed = True
        self.car.speed = 100


if __name__ == "__main__":

    t = 0

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("mdeyo car sim")
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    car = Car(RED,60,385,screen)
    road = CurvedRoad(1200,60,385,'45')
    car.constant_speed = True
    car.speed = 100
    # car = laneFollowingCar1()

    screen.fill(WHITE)

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
        # print(t)
        # inputKey = input('press a key')
        # gameLoop(inputKey,car,screen)
        t+=1
        #t = 114 if driving straight to x=1200 at car.speed=100
        #t =
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


        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill(WHITE)

        # --- Game logic and drawing code combined

        drawRoad(screen)
        road.plotRoad(screen)

        rate = 10
        car.update(1/rate)
        updateSteering(screen,car)
        updateSpeedometer(screen,car)
        print(road.reward(car))

        if(t>200):
            car.speed=0
            print('done!')
            done=True

        if(car.pose[0]>1200):
            print('reached x=1200')
            car.speed=0
            done=True

        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # --- Limit to 60 frames per second
        clock.tick(rate)
