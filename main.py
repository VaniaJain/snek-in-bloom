import pygame
import random
import json
import math

pygame.init()

#creating the game window
width=800
height=600
cell_size=20 

screen=pygame.display.set_mode((width, height))
pygame.display.set_caption("Snek in Bloom")

#updating the game at 60 fps
clock= pygame.time.Clock()
FPS=60
move_delay=140#milliseconds between moves
last_move=0


#garden colour palette
background= (242,248, 232)
grid_colour= (229, 237, 216)
snake_green=(105, 145, 91)
snake_head=(75, 115, 72)
dark_green= (62, 89, 57)
strawberry_red=(220,91,112)
white=(255, 255,255)
golden_yellow=(245, 190, 65)
petal_pink=(242,160, 177)
flower_yellow=(250, 210, 100)
grass_accent=(170, 196, 133)
mud_colour=(151, 119, 91)
mud_dark=(119, 91,70)

#fonts
title_font= pygame.font.Font(None, 52)
subtitle_font= pygame.font.Font(None, 25)

#text surfaces
title= title_font.render("Snek in Bloom", True, dark_green)
subtitle=subtitle_font.render("a tiny garden adventure", True, snake_green)

#snake position, meanured in grid cells
snake= [(20,15), (19,15), (18,15)]
direction=(1,0)

#spawning strawberries
def spawn_food(snake, score, mud_patches):
    while True:
        new_food=( random.randint(0, width//cell_size-1),
            random.randint(0, height//cell_size-1))
        if new_food not in snake and new_food not in mud_patches:
            is_golden=score>=5 and random.random()<0.20
            return new_food, is_golden

#loading the best score
def load_best_score():
    try:
        with open("best_score.json", "r") as file: 
            data=json.load(file)
            return data["best_score"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return 0
#saving a new best score
def save_best_score(best_score):
    with open("best_score.json", "w") as file:
        json.dump({"best_score": best_score}, file)

#initialising food and score
score=0
best_score=load_best_score()
sparkles=[]
#creating fixed decor for the pixel garden
garden_decor=[]
used_cells=set()

decoration_types=["flower", "grass", "clover"]
decoration_colours=[petal_pink, flower_yellow, white, grass_accent]

cols= width//cell_size
rows= height//cell_size

#four corner regions: (column start, column end, row start, row end)
corner_regions=[(1,12,7,13), 
               (cols-12, cols-1, 7, 13), 
               (1, 12,  rows-8, rows-2),
               (cols-12, cols-1, rows-8, rows-2)]
for col_start, col_end, row_start, row_end in corner_regions:
    for _ in range(18):
        col=random.randint(col_start, col_end)
        row= random.randint(row_start, row_end)
        position=(col, row)
        if position not in used_cells:
            used_cells.add(position)
            kind= random.choice(decoration_types)
            colour=random.choice(decoration_colours)
            garden_decor.append((col, row, kind, colour))

mud_patches= set()
food, golden_food=spawn_food(snake,score,mud_patches)
while len(mud_patches)<8:
    col= random.randint(1, width//cell_size-2)
    row=random.randint(7, height//cell_size-2)
    position=(col, row)
    if(position not in snake and position!=food and position not in used_cells):
        mud_patches.add(position)

while len(garden_decor)<45:
    col=random.randint(0, width//cell_size-1)
    row=random.randint(7, height//cell_size-1)
    position=(col, row)

    if position not in used_cells and position not in snake and position!=food:
        used_cells.add(position)
        kind=random.choice(decoration_types)
        colour=random.choice(decoration_colours)
        garden_decor.append((col, row, kind, colour))

#keep the game running till the player closes it
game_started=False
game_over=False
running=True

#adding sparkles ✨
def create_sparkles(position):
    col, row=position

    #converting grid position to the center of the cell
    x=col*cell_size+cell_size//2
    y=row*cell_size+cell_size//2

    #creating 10 particles spreading in different directions
    #dividing a circle into 10 angles and each article travels in one direction
    for i in range(10):
        angle= (2*math.pi*i)/10
        speed=2
        sparkles.append({"x": x, "y": y, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "life": 30})

#handling events such as clicking the close button
while running:
    #1. handling events
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        #keyboard controls
        if event.type==pygame.KEYDOWN:
            #starts the game
            if not game_started and event.key==pygame.K_SPACE:
                game_started=True
                last_move=pygame.time.get_ticks()
            #restarts after game over
            elif game_over and event.key==pygame.K_r:
                snake=[(20,15), (19,15), (18,15)]
                direction=(1,0)
                score=0
                food, golden_food=spawn_food(snake, score, mud_patches)
                game_over= False
                last_move= pygame.time.get_ticks()
            #movement controls during game play
            new_direction= direction
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                new_direction=(1,0)
            elif event.key in(pygame.K_LEFT, pygame.K_a):
                new_direction=(-1,0)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                new_direction=(0,1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                new_direction=(0,-1)
                #rejecting a 180 degree turn
            if new_direction!=(-direction[0], -direction[1]):
                direction= new_direction
    #2. moving snake at regular intervals
    current_time=pygame.time.get_ticks()

    #updating sparkle particles
    for particle in sparkles[:]:
        particle["x"]+=particle["vx"]
        particle["y"]+=particle["vy"]
        particle["life"]-=1
        if particle["life"]<=0:
            sparkles.remove(particle)

    if game_started and not game_over and current_time-last_move >= move_delay:
        head_col, head_row=snake[0]
        dx,dy=direction
        new_head=(head_col+dx, head_row+dy)
        if(#checking if the head hits a wall
            new_head[0]<0 or new_head[0]>=width//cell_size
            or new_head[1]<0 or new_head[1]>=height//cell_size
        ):
            game_over=True
        elif new_head in snake[:-1]:#checking if head hits snake's body
            game_over=True
        elif new_head in mud_patches:
            game_over=True
        if not game_over:
            #putting the new head at the front and removing the last segment so that the snake stays the same length
            snake.insert(0, new_head)
            if new_head==food:
                if golden_food:
                    score=score+5
                    create_sparkles(new_head)
                else:
                    score=score+1
                if score>best_score:
                    best_score=score
                    save_best_score(best_score)
                food, golden_food=spawn_food(snake, score, mud_patches)
            else:
                snake.pop()
            last_move=current_time
    #3. drawing the background
    screen.fill(background)
    #drawing tiny garden decorations
    for col, row in mud_patches:
        x=col*cell_size
        y=row*cell_size
        pygame.draw.rect(screen, mud_colour, (x+3, y+5, 14, 10))
        pygame.draw.rect(screen, mud_dark, (x+6, y+7, 4,3))
        pygame.draw.rect(screen, mud_dark, (x+12, y+10, 3, 2))
    for col, row, kind, colour in garden_decor:
        position=(col, row)
        #keeping decor underneath the snake and the food
        if position in snake or position==food:
            continue
        x=col*cell_size
        y=row*cell_size
        if kind=="flower":
            #four square petals and a centre
            pygame.draw.rect(screen, colour, (x+7, y+3, 5,5))
            pygame.draw.rect(screen, colour, (x+3, y+7, 5,5))
            pygame.draw.rect(screen, colour, (x+12, y+7, 5,5))
            pygame.draw.rect(screen, colour, (x+7, y+12, 5,5))
            pygame.draw.rect(screen, flower_yellow, (x+8, y+8, 4,4))
        elif kind=="grass":
            #three little blades of grass
            pygame.draw.rect(screen, grass_accent, (x+5, y+9, 3, 7))
            pygame.draw.rect(screen, grass_accent, (x+9, y+5, 3, 11))
            pygame.draw.rect(screen, grass_accent, (x+13, y+8, 3, 8))
        elif kind=="clover":
            #tiny three leaf clover
            pygame.draw.rect(screen, snake_green, (x+5, y+5, 5, 5))
            pygame.draw.rect(screen, snake_green, (x+11, y+5, 5,5))
            pygame.draw.rect(screen, snake_green, (x+8, y+10, 5, 5))
            pygame.draw.rect(screen, dark_green, (x+9, y+13, 2, 4))
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, grid_colour, (x,0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, grid_colour, (0,y), (width, y))
    #drawing the food, score
    food_x=food[0]*cell_size
    food_y=food[1]*cell_size
    if golden_food:
        food_colour=golden_yellow
    else:
        food_colour=strawberry_red
    pygame.draw.circle(screen, food_colour, (food_x+cell_size//2, food_y+cell_size//2), cell_size//2-2)

    #drawing the particles
    for particle in sparkles:
        radius=max(1, particle["life"]//10)
        pygame.draw.circle(screen, golden_yellow, (int(particle["x"]), int(particle["y"])), radius)
    #drawing the snake
    for index, (col, row) in enumerate(snake):
        x=col*cell_size
        y=row*cell_size
        colour=snake_head if index==0 else snake_green
        pygame.draw.rect(screen, colour, (x+1, y+1, cell_size-2, cell_size-2), border_radius=5)

    #drawing score, title and subtitle
    score_text=subtitle_font.render(f"Strawberries: {score}", True, dark_green)
    best_text=subtitle_font.render(f"Best: {best_score}", True, dark_green)
    screen.blit(score_text,(20,15))
    screen.blit(best_text, (20, 40))
    screen.blit(title, title.get_rect(center=(width//2, 65)))
    screen.blit(subtitle, subtitle.get_rect(center=(width//2, 100)))

    #start screen
    if not game_started:
        overlay=pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((242, 248, 232, 235))
        screen.blit(overlay, (0,0))
        menu_font=pygame.font.Font(None, 34)
        instruction_font= pygame.font.Font(None, 27)
        controls_text= instruction_font.render("Use arrow keys or WASD to move", True, snake_green)
        start_text= menu_font.render("Press SPACE to begin", True, dark_green)
        screen.blit(controls_text, controls_text.get_rect(center=(width//2, height//2-10)))
        screen.blit(start_text, start_text.get_rect(center= (width//2, height//2+40)))
    #game over screen:
    elif game_over:
        overlay=pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((242, 248, 232, 210))
        screen.blit(overlay, (0,0))

        game_over_font= pygame.font.Font(None, 64)
        message_font=pygame.font.Font(None,30)
        game_over_text= game_over_font.render("Garden Over!", True, dark_green)
        score_message= message_font.render(f"Strawberries collected: {score}", True, snake_green)
        restart_message=message_font.render("Press R to try again", True, dark_green)
        screen.blit(game_over_text, game_over_text.get_rect(center= (width//2, height//2-60)))
        screen.blit(score_message, score_message.get_rect(center=(width//2, height//2)))
        screen.blit(restart_message, restart_message.get_rect(center=(width//2, height//2+45)))


    #4. displaying the frame and regulating the refresh rate
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()

