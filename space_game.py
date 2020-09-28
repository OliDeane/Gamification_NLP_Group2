import pygame
import time
import random

pygame.init()

# define colors
black=(0,0,0)
white=(255,255,255)
red=(255,0,0)
green=(0,255,0)


# Create game environment
display_width=800
display_height=600
gameDisplay=pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Train The Model!")
clock=pygame.time.Clock()

# Load in player background images
player_img=pygame.image.load(r"C:\Users\Oli\Documents\Python_Game_Devs\cropped_rocket.png")
player_width = 60
bg_1 = pygame.image.load(r"C:\Users\Oli\Documents\Python_Game_Devs\starry_night.png")
bg_2 = pygame.image.load(r"C:\Users\Oli\Documents\Python_Game_Devs\starry_night.png")



def draw_scoreboard(count):
    font=pygame.font.SysFont(None,40)
    text=font.render("Score "+str(count),True,white)
    gameDisplay.blit(text,(20,20))


def set_player_icon(x,y):
    gameDisplay.blit(player_img,(x,y))
    

def insert_obstacle(obstaclex,obstacley,obstaclew,obstacleh,color):
    pygame.draw.rect(gameDisplay,color,[obstaclex,obstacley,obstaclew,obstacleh])

# Create the 'alien'
def insert_prize(obstaclex,obstacley,obstaclew,obstacleh,color):
    pygame.draw.circle(gameDisplay, color, [obstaclex, obstacley], 40)

# Function for creating general text
def text_objects(text,font):
    textSurface=font.render(text, True, red)
    return textSurface, textSurface.get_rect()

# Used for when users crash
def message_display(text):
    largeText=pygame.font.Font('freesansbold.ttf',115)
    TextSurf, TextRect=text_objects(text, largeText)
    TextRect.center=((display_width/2),(display_height/2))
    gameDisplay.blit(TextSurf, TextRect)

    pygame.display.update()

    time.sleep(2)

    game_loop()

# Call when users crash into an obstacle
def crash():
    message_display('You Crashed')

# For now this is just a placeholder. It creates a lame white box with red writing - not an input box.
def make_input_box():

    pygame.draw.rect(gameDisplay,black,[200,200,400,250], 8)
    pygame.draw.rect(gameDisplay,white,[200,200,400,250])
    pygame.display.update()

    text = 'Type your example here:'
    largeText=pygame.font.Font('freesansbold.ttf',20)
    TextSurf, TextRect=text_objects(text, largeText)
    TextRect.center=((display_width/2 - 65),(display_height/2-70))
    gameDisplay.blit(TextSurf, TextRect)

    pygame.display.update()

    time.sleep(2)
    game_loop()


# This makes the rolling background. As one background image lowers, the other follows. When the first reaches
# the end of the display screen it returns to its starting position. This cycle is continuous. 
def update_background(bg_1_xpos, bg_2_xpos, bg_2, display_height):
    if bg_1_xpos > display_height:
        bg_1_xpos = 0
        bg_2_xpos = bg_1_xpos - bg_2.get_size()[1]
    else:
        bg_1_xpos += 5
        bg_2_xpos = bg_1_xpos - bg_2.get_size()[1]
    return bg_1_xpos, bg_2_xpos


# Function for producing a crash when the play hits an obstacle
def check_obstacle_crash(player_x, player_y, obstacle_startx, obstacle_starty,\
            obstacle_height, obstacle_width, player_width):

            # If the obstacle's y position matches the 
            if player_y < obstacle_starty + obstacle_height:
                print('y crossover')

                # if the player position overalps with obstacle positon - call the crash function
                if player_x > obstacle_startx and player_x < obstacle_startx + obstacle_width\
                    or player_x + player_width > obstacle_startx and player_x + player_width < obstacle_startx + obstacle_width:
                    print('x crossover')
                    crash()

# Function that generates an input box when an 'alien' is hit
def check_prize_crash(player_x, player_y, prize_startx, prize_starty,\
    prize_height, prize_width, player_width):

    if player_y < prize_starty+prize_height:
        print('y crossover')

        if player_x > prize_startx and player_x<prize_startx+prize_width \
            or player_x + player_width > prize_startx and player_x + player_width < prize_startx + prize_width:
            make_input_box()
        

"""
Below is the main game loop where all functions are called. 
"""

def game_loop():

    # Defint the background image's starting position
    bg_1_xpos = 0
    bg_2_xpos = 0 - bg_2.get_size()[1]

    # define the players initial position
    player_x = (display_width*0.48)
    player_y = (display_height*0.79)

    # define the player's initial movement - begins still so = 0
    x_change = 0

    # define the first obstacle's starting position and speed. Speed will be random between two integers.
    obstacle_startx=random.randrange(200,display_width-200)
    obstacle_starty=-600
    obstacle_speed= random.randrange(5,10)
    obstacle_width=100
    obstacle_height=100

    # define the first 'alien''s starting potision and speed. 
    prize_startx = random.randrange(80,display_width-80)
    prize_starty = -300
    prize_speed = random.randrange(5,7)
    prize_width = 40
    prize_height = 40

    #Define player's current score
    dodge_count=0

    gameExit=False

    while not gameExit:
        
        # Didsplay background images at up-to-date x positions
        gameDisplay.blit(bg_1, (0, bg_1_xpos))
        gameDisplay.blit(bg_2, (0,bg_2_xpos))

        # Receive user's movement commands
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()

            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_LEFT:
                    x_change=-5
                elif event.key==pygame.K_RIGHT:
                    x_change=5

            if event.type==pygame.KEYUP:
                if event.key==pygame.K_LEFT or event.key==pygame.K_RIGHT:
                    x_change=0
            
        # Update player's x-axis position based on movement commands. Display the player at this position.
        player_x += x_change
        set_player_icon(player_x, player_y)

        # Display the obstacle and update its position on screen according to its pre-defined speed
        insert_obstacle(obstacle_startx,obstacle_starty,obstacle_width,obstacle_height,red)
        obstacle_speed = random.randrange(5,15)
        obstacle_starty += obstacle_speed

        # Display the 'alien' and update its position 
        insert_obstacle(prize_startx, prize_starty, prize_width, prize_height, green)
        prize_speed = random.randrange(5,15)
        prize_starty+=prize_speed

        # Update the scoreboard depending on how many obstacles have been dodged.
        # Scoring system will change when we're able to receive input messages.
        draw_scoreboard(dodge_count)

        # The player will crash if they stray beyond the display boundaries
        if player_x > display_width-player_width or player_x < 0:
            crash()


        # Move the obstacle
        # If the obstacle's current position is beyond the display height, then reset with a random x position        
        if obstacle_starty>display_height:
            obstacle_starty=0-obstacle_height
            obstacle_startx=random.randrange(0,display_width) # position of obstacle will be random in the boundry of the display
            dodge_count+=1

        # the player crashes if an obstacle is hit
        check_obstacle_crash(player_x, player_y, obstacle_startx, obstacle_starty,\
            obstacle_height, obstacle_width, player_width)
        

        # Move the 'alien' 
        if prize_starty>display_height:
            prize_starty=0-prize_height
            prize_startx=random.randrange(0,display_width) # position of prize will be random in the boundry of the display
            dodge_count+=1

        # Generate input input box when 'alien' is hit
        check_prize_crash(player_x, player_y, prize_startx, prize_starty,\
            prize_height, prize_width, player_width)


        #Update the background image position to ensure a rolling background
        bg_1_xpos, bg_2_xpos = update_background(bg_1_xpos, bg_2_xpos, bg_2, display_height)     

        pygame.display.update()
        clock.tick(80)
        


# Run the game loop
game_loop()
pygame.quit()
quit()
