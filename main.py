import pygame
from pygame.locals import *
import random

pygame.init()

# Game resolution
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Racecar Game')

# colors var
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)
dark_green = (1, 50, 32)

#game music
pygame.mixer.init()
pygame.mixer.music.load("DRIVE.mp3")
pygame.mixer.music.set_volume(0.07)
pygame.mixer.music.play()
# road and border
road_width = 300
marker_width = 10
marker_height = 50

# lane coord
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road size
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)
right_grass = (100, 0, marker_width, height)

# movement of car
lane_marker_move_y = 0

# player spawn location
player_x = 250
player_y = 400

#fps
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
speed = 2
score = 0
high_score = 0


class Car(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        #scale image so it is perfect size
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerCar(Car):

    def __init__(self, x, y):
        image = pygame.image.load('picture/racing-red-car-drawing.png')
        super().__init__(image, x, y)


# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

#player car
player = PlayerCar(player_x, player_y)
player_group.add(player)

# render car pics
picture_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_picture = []
for picture_filename in picture_filenames:
    picture = pygame.image.load('picture/' + picture_filename)
    vehicle_picture.append(picture)

# load the crash image
crash = pygame.image.load('picture/crash.png')
crash_rect = crash.get_rect()

# game loop
running = True
while running:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        # move the player's car using the left/right arrow keys
        if event.type == KEYDOWN:

            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 100
            elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 100

            # check if there's a side swipe collision after changing lanes
            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):

                    gameover = True

                    # place the player's car next to other vehicle
                    # and determine where to position the crash image
                    if event.key == K_LEFT:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    elif event.key == K_RIGHT:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]

    #Grass
    screen.fill(green)

    #Road
    pygame.draw.rect(screen, gray, road)

    #Border
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)


    #Lane markings on road
    lane_marker_move_y += speed * 2
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    #Draw the player's car
    player_group.draw(screen)

    #Add car
    if len(vehicle_group) < 2:

        #Create gap between each car
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False

        if add_vehicle:
            #Spawn cars in random lanes
            lane = random.choice(lanes)

            # select a random vehicle image
            image = random.choice(vehicle_picture)
            vehicle = Car(image, lane, height / -2)
            vehicle_group.add(vehicle)

    #Make car move like npc
    for vehicle in vehicle_group:
        vehicle.rect.y += speed

        #Delete car when they are off the screen
        if vehicle.rect.top >= height:
            vehicle.kill()

            #Add 1 point to score whenever player pass 1 car
            score += 1

            # Game gets faster after player pass 5 cars
            if score > 0 and score % 5 == 0:
                speed += 1
            if score > high_score:
                high_score = score

    # draw the vehicles
    vehicle_group.draw(screen)

    # Show Score
    font = pygame.font.Font(pygame.font.get_default_font(), 14)
    text = font.render('Score: ' + str(score), True, white)
    high_score_text = font.render("High Score: " + str(high_score), True, white)
    screen.blit(high_score_text, (1,10))
    text_rect = text.get_rect()
    text_rect.center = (50, 30)
    screen.blit(text, text_rect)

    # If player crash into another car, then game is over
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        crash_rect.center = [player.rect.center[0], player.rect.top]

    # Show game over
    if gameover:
        screen.blit(crash, crash_rect)

        pygame.draw.rect(screen, red, (0, 50, width, 100))
        pygame.mixer_music.stop()
        pygame.mixer.init()
        pygame.mixer.music.load('WoodCrashesDistant FS022705.mp3')
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play()

        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Crash Detected! Try again? (Enter Y or N)', True, white)
        text_rect = text.get_rect()
        text_rect.center = (width / 2, 100)
        screen.blit(text, text_rect)

    pygame.display.update()

    # Wait for player to decide if they want to play again
    while gameover:

        clock.tick(fps)

        for event in pygame.event.get():

            if event.type == QUIT:
                gameover = False
                running = False

            # get the player's input (y or n)
            if event.type == KEYDOWN:
                if event.key == K_y:
                    # restart the game
                    gameover = False
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]
                    pygame.mixer_music.stop()
                    pygame.mixer.music.load('DRIVE.mp3')
                    pygame.mixer.music.set_volume(0.07)
                    pygame.mixer.music.play()
                elif event.key == K_n:
                    # exit the loops
                    gameover = False
                    running = False

pygame.quit()