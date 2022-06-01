from turtle import pos
import pygame
import time
import math
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()


# load in images
# adding Masks (images within images that are showing)
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.7)
FINISH = scale_image(pygame.image.load("imgs/finish.png"), 0.75)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (100,210)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.7)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.35)
GREY_CAR = scale_image(pygame.image.load("imgs/grey-car.png"), 0.35)
PURPLE_CAR = scale_image(pygame.image.load("imgs/purple-car.png"), 0.35)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.35)
WHITE_CAR = scale_image(pygame.image.load("imgs/white-car.png"), 0.35)

# make our window
WIDTH,HEIGHT = TRACK.get_width(), TRACK.get_height()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 29)

class AbstractCar: # this means we are programming for the player and CPU cars
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1 / 1.5

    def rotate(self, left = False, right = False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = min(self.vel - self.acceleration, -self.max_vel/3)
        self.move()

    def move(self): # defining the side movements
        radians = math.radians(self.angle) # need to use constant trig to find the velocities
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi
    
    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        
        self.vel = 0


class PlayerCar(AbstractCar):#putting AbstractCar in the parenthesis means everything from it can be used by PlayerCar
    IMG = RED_CAR
    START_POS = (145, 180)

    # these methods go here and not in AbstractCar since this is only the player car, not the opponent car
    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration/2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (115, 180)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0 # what point in the path is it at
        self.vel = max_vel

    def draw_points(self,win):
        for point in self.path:
            pygame.draw.circle(win, (255,0,0), point, 5)

    def draw(self,win):
        super().draw(win)
        # self.draw_points(win) # this drew the path that we made by clicking
    
    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        diffence_in_angle = self.angle - math.degrees(desired_radian_angle)
        if diffence_in_angle >= 180:
            diffence_in_angle -= 360
        
        if diffence_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(diffence_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(diffence_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self): # path following code
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

    #update speed based on current level
    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0

# Add a core function to this, put all our images through this
def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images: # this will go through our images IN THEIR ORDER and add them
        win.blit(img, pos)

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255,255,255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255,255,255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255,255,255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))    

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def move_player(player_car):
        # Key-pressing to move the car
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()

    if not moved:
        player_car.reduce_speed()


# event loop to keep the screen running and display the images
FPS = 60
PATH = [(135, 122), (108, 55), (41, 125), (42, 364), (229, 548), (276, 557), (325, 436), (329, 402), (400, 373), (463, 435), (455, 506), (490, 546), (548, 542), (563, 375), (558, 310), (406, 288), (332, 247), (387, 201), (518, 210), (554, 82), (264, 69), (232, 285), (121, 218)]

class GameInfo: # keeps track of game info like main menu or the level we are on
    LEVELS = 10

    def __init__(self, level = 1): # starting at level 1
        self.level = level # current level
        self.started = False # have we started?
        self.level_start_time = 0 # how much time has elapsed in current level

    def next_level(self): 
        self.level += 1 # increments the level
        self.started = False # it hasnt started until we say so

    def reset(self):
        self.level = 1 # if it resets, level 1
        self.started = False # hasnt started yet
        self.level_start_time = 0 # no time has elapsed just yet

    def game_finished(self):
        return self.level > self.LEVELS
    
    def start_level(self): # when you start a level
        self.started = True # now you started
        self.level_start_time = time.time() # it starts at the time of the clock

    def get_level_time(self):
        if not self.started: # if you havent started the level, no time has elapsed
            return 0
        return round(time.time() - self.level_start_time) # if you have started, it gets how much time during the level

def handle_collision(player_car, computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        blit_text_center(WIN, MAIN_FONT, "You Lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)

run = True
clock = pygame.time.Clock() # this makes it so we can track the speed the game is running then set a speed it can't universally exceed
images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))] # contains the static images we want to insert; adding the border again to get rid of any overlap
player_car = PlayerCar(2, 2)
computer_car = ComputerCar(1, 2, PATH)
game_info = GameInfo()

while run:
    clock.tick(FPS) #while running it stays at this FPS
    
    draw(WIN, images, player_car, computer_car, game_info)    

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

#        if event.type == pygame.MOUSEBUTTONDOWN: # these are meant to help the computer car navigate to a new point
#            pos = pygame.mouse.get_pos()
#            computer_car.path.append(pos)

    
    move_player(player_car)
    computer_car.move()

    handle_collision(player_car, computer_car, game_info)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()


# print(computer_car.path) # needed if we are making paths for the CPU car
pygame.quit()