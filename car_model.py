
import pygame
import math

def dampenSteering(angle,elasticity,delta):
    if angle == 0:
        return 0
    elif angle > 0:
        new_angle = angle - elasticity*delta
        if new_angle <= 0:
            new_angle = 0
        return new_angle
    elif angle < 0:
        new_angle = angle + elasticity*delta
        if new_angle >= 0:
            new_angle = 0
        return new_angle

def dampenSpeed(speed,velocity_dampening,delta):
    if speed == 0:
        new_speed = 0
    elif speed > 0:
        new_speed = speed - velocity_dampening*delta*(speed/10)
        if new_speed <= 0:
            new_speed = 0
    elif speed < 0:
        new_speed = speed + velocity_dampening*delta*(speed/10)
        if new_speed >= 0:
            new_speed = 0
    return int(new_speed)

class Car(pygame.sprite.Sprite):
    def __init__(self, color, x, y,screen):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.vel = [0,0]
        self.speed = 0
        self.angle = 0
        self.steering_angle = 0
        self.pose = [x,y]
        self.screen = screen
        self.width = 50
        self.length = 100
        self.originalImage = pygame.image.load("images/red_car.png").convert_alpha()
        self.originalImage = pygame.transform.scale(self.originalImage,(self.length,self.width))
        self.image = self.originalImage.copy() # The variable that is changed whenever the car is rotated.
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.maxSteer = math.pi/3
        self.acceleration_rate = 5
        self.speed_dampening = 0.1
        self.maxSpeed = 300;
        self.steering_elasticity = 5
        self.gear = "STOP"

    def accelerate(self,dv):
        if self.gear == "STOP":
            if dv>0: # start accelerating forward
                self.gear = "D"
                self.speed += self.acceleration_rate*dv
                self.speed = min(self.speed, self.maxSpeed)
            elif dv<0:
                self.gear = "R"
                self.speed += self.acceleration_rate*dv
                self.speed = max(-self.speed, self.maxSpeed)

        elif self.gear == "D":
            self.speed += self.acceleration_rate*dv
            self.speed = min(self.speed, self.maxSpeed)
            if self.speed <=0:
                self.speed = 0;

        elif self.gear == "R":
            self.speed += self.acceleration_rate*dv
            self.speed = max(self.speed, -self.maxSpeed)
            if self.speed >=0:
                self.speed = 0;

        # print('gear: '+self.gear+' speed:'+str(self.speed))

    def release_down(self,direction):
        if direction>0 and self.gear == "R":
            self.gear = "STOP"
        elif direction<0 and self.gear == "D":
            self.gear = "STOP"

    def turn(self,direction):
        new_steering_angle = self.steering_angle+direction*(math.pi/20)
        # print(new_steering_angle)
        if new_steering_angle > self.maxSteer:
            # print('too much positive turn')
            self.steering_angle = self.maxSteer
        elif new_steering_angle < -self.maxSteer:
            self.steering_angle = -self.maxSteer
        else:
            self.steering_angle = new_steering_angle

    def update(self,delta):

        self.angle += self.steering_angle*delta*self.speed/100

        self.vel[0] = math.cos(self.angle)*self.speed
        self.vel[1] = math.sin(self.angle)*self.speed
        self.pose[0] += self.vel[0]*delta
        self.pose[1] += self.vel[1]*delta

        self.steering_angle = dampenSteering(self.steering_angle,self.steering_elasticity,delta)
        self.speed = dampenSpeed(self.speed,self.speed_dampening,delta)

        # img = pygame.draw.rect(self.screen,self.color,[self.pose[0],self.pose[1],80,50],2)
        # car_img = self.originalImage.copy()
        # loc = car_img.get_rect().center  #rot_image is not defined
        # self.image = pygame.transform.rotate(car_img, (-self.angle*360/(2*math.pi)))
        # self.image.get_rect().center = loc

        oldCenter = self.rect.center
        car_img = self.originalImage.copy()
        self.image = pygame.transform.rotate(car_img, (-self.angle*360/(2*math.pi)))
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

        # print(self.image.get_size())
        w, h = self.image.get_size()
        self.screen.blit(self.image, (self.pose[0]-w/2, self.pose[1]-h/2))

        # print('drew car: '+str(self.pose))
        # pygame.transform.rotate(img,45)
        return self.pose

    def updateMinute(self):
        self.odo_miles += speed

        if self.odo_miles >= 500:
            return True
        self.speed = random.randrange(120)
        return False
