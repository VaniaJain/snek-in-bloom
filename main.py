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
normal_move_delay=140#milliseconds between moves
move_delay=normal_move_delay
last_move=0

#snake tongue animation
tongue_interval=700#time between flickers of the tongue
tongue_duration=160#how long the tongue is visible
tongue_start_time=pygame.time.get_ticks()

#frostberry settings
frost_duration=5000 #milliseconds
frost_slowdown=1.5
frost_active=False
frost_start_time=0
frost_overlay_colour=(125, 195, 255, 65)

#harvest frenzy settings
frenzy_interval=30000
frenzy_duration=8000
frenzy_active=False
frenzy_start_time=0
last_frenzy_time=0
frenzy_paused_at=0

#garden colour palette
background= (242,248, 232)
grid_colour= (229, 237, 216)
snake_green=(105, 145, 91)
snake_head=(75, 115, 72)
dark_green= (62, 89, 57)
strawberry_red=(185, 48, 68)
white=(255, 255,255)
golden_yellow=(245, 190, 65)
petal_pink=(242,160, 177)
flower_yellow=(250, 210, 100)
grass_accent=(170, 196, 133)
mud_colour=(151, 119, 91)
mud_dark=(119, 91,70)
frostberry_blue=(105, 180, 235)
ice_highlight=(210,240,255)
grass_light=(225, 239, 207)
grass_dark=(218, 233, 199)
hud_panel=(240, 246, 222)
hud_border=(105, 145, 91)
rainbow_colours=[(255,90,100),(255, 165, 70), (255, 220, 90), (100, 190,110), (85, 155,235), (165,115,210)]
rainbow_bonus=10
popup_colour=(105,45,100)

#hud safe zone
hud_cols=range(0,10)
hud_rows=range(0,4)
hud_cells={(col,row) for col in hud_cols for row in hud_rows}

#fonts
title_font= pygame.font.Font(None, 52)
subtitle_font= pygame.font.Font(None, 25)

#text surfaces
title= title_font.render("Snek in Bloom", True, dark_green)
subtitle=subtitle_font.render("a tiny garden adventure", True, snake_green)

#snake position, meanured in grid cells
snake= [(20,15), (19,15), (18,15)]
direction=(1,0)

#drawing strawberries
def draw_strawberry(x, y, berry_type):
    #choosing colours for every berry type
    if berry_type=="golden":
        berry_colour=golden_yellow
        highlight_colour=white
    elif berry_type=="frost":
        berry_colour=frostberry_blue
        highlight_colour=(255,155,165)
    elif berry_type=="rainbow":
        berry_colour=random.choice(rainbow_colours)
        highlight_colour=white
    else:
        berry_colour=strawberry_red
        highlight_colour=(255, 155, 165)

    #leafy green top
    pygame.draw.rect(screen, dark_green, (x+6, y+3, 8,3))
    pygame.draw.rect(screen, snake_green,(x+4, y+4, 4, 3))
    pygame.draw.rect(screen, snake_green, (x+12, y+4, 4,3))
    pygame.draw.rect(screen, snake_green, (x+8, y+1, 4,4))

    #berry body
    pygame.draw.rect(screen, berry_colour, (x+5, y+6, 10, 3))
    pygame.draw.rect(screen, berry_colour, (x+3, y+9, 14, 4))
    pygame.draw.rect(screen, berry_colour, (x+5, y+13, 10, 3))
    pygame.draw.rect(screen, berry_colour, (x+7, y+16, 6, 2))

    #rainbow pixel stripes
    if berry_type=="rainbow":
        pygame.draw.rect(screen, (255, 90,100), (x+5, y+6, 10, 3))
        pygame.draw.rect(screen, (255, 165, 70), (x+3, y+9, 14,2))
        pygame.draw.rect(screen, (100, 190, 110), (x+3, y+11, 14,2))
        pygame.draw.rect(screen, (85, 155, 235), (x+5, y+13, 10, 3))

    #tiny pixel highlights
    pygame.draw.rect(screen, highlight_colour,(x+6, y+8, 3,2))
    pygame.draw.rect(screen, highlight_colour, (x+11, y+12, 2,2))

    #icy sparkles on frostberry
    if berry_type=="frost":
        pygame.draw.rect(screen, white, (x+12, y+6, 3,2))

                     

#spawning strawberries
def spawn_food(snake, score, mud_patches):
    while True:
        new_food=( random.randint(0, width//cell_size-1),
            random.randint(0, height//cell_size-1))
        if new_food not in snake and new_food not in mud_patches and new_food not in hud_cells:
            golden_chance=0.60 if frenzy_active else 0.20 #chances of getting a golden strawberry during harvest frenzy increases
            is_golden=score>=5 and random.random()<golden_chance
            is_frost=not is_golden and random.random()<0.15
            is_rainbow=(not is_golden and not is_frost and score>=10 and random.random()<0.1)
            return new_food, is_golden, is_frost, is_rainbow

#spawning multiple strawberries incase harvest frenzy is triggered
def spawn_frenzy_strawberries(snake, mud_patches, food, count):
    strawberries=[]
    occupied=set(snake)|set(mud_patches)|hud_cells
    if food is not None:
        occupied.add(food)
    while len(strawberries)<count:
        position=(random.randint(0,width//cell_size-1), random.randint(0, height//cell_size-1))
        if position in occupied:
            continue
        occupied.add(position)
        roll=random.random()
        if roll<0.60:
            berry_type="golden"
        elif roll<0.75:
            berry_type="frost"
        else:
            berry_type="normal"
        strawberries.append({"position":position,"type": berry_type})
    return strawberries

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
berry_bursts=[]
collection_rings=[]
growth_effects=[]
#creating fixed decor for the pixel garden
garden_decor=[]
used_cells=set()
score_popups=[]

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
safe_start_cells={(20,15), (19,15), (18,15), (21,15), (22,15), (23,15), (24,15)}
food, golden_food, frost_food, rainbow_food=spawn_food(snake,score,mud_patches)
frenzy_strawberries=[]
while len(mud_patches)<8:
    col= random.randint(1, width//cell_size-2)
    row=random.randint(7, height//cell_size-2)
    position=(col, row)
    if(position not in snake and position not in safe_start_cells and position!=food and position not in used_cells):
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
paused=False

def create_score_popups(position, points):
    col, row=position
    x=col*cell_size+cell_size//2
    y=row*cell_size
    score_popups.append({"x": x, "y":y, "text":f"+{points}", "life": 40})
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

#creating a burst when strawberries are collected
def create_berry_burst(position, berry_type="normal"):
    col, row=position
    x=col*cell_size+cell_size//2
    y=row*cell_size+cell_size//2
    if berry_type=="golden":
        colours=[golden_yellow, white]
    elif berry_type=="frost":
        colours=[frostberry_blue, ice_highlight]
    elif berry_type=="rainbow":
        colours=rainbow_colours
    else:
        colours=[strawberry_red, petal_pink, white]
    for i in range(12):
        angle=(2*math.pi*i)/12
        speed=random.uniform(1.5,3)
        berry_bursts.append({"x":x, "y": y, "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed, "colour": random.choice(colours), "life":22})

#creating a special ring for rare berries
def create_collection_ring(position, berry_type):
    col, row=position
    x=col*cell_size+cell_size//2
    y=row*cell_size+cell_size//2
    ring_colour=(rainbow_colours[0] if berry_type=="rainbow" else golden_yellow)
    collection_rings.append({"x": x, "y":y, "radius":4,"life":18, "colour":ring_colour})

#handling events such as clicking the close button
while running:
    #1. handling events
    for event in pygame.event.get():
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_p and game_started and not game_over:
                paused= not paused
                if not paused:
                    last_move=pygame.time.get_ticks()
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
                food, golden_food, frost_food, rainbow_food=spawn_food(snake, score, mud_patches)
                game_over= False
                frost_active=False
                frost_start_time=0
                frenzy_active=False
                frenzy_start_time=0
                last_frenzy_time=pygame.time.get_ticks()
                frenzy_paused_at=0
                move_delay=normal_move_delay
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
    tongue_visible=(current_time%tongue_interval<tongue_duration)
    #harvest frenzy timer
    if game_started and not game_over:
        if paused:
            if frenzy_paused_at==0:
                frenzy_paused_at=current_time
        else: 
            if frenzy_paused_at!=0:
                paused_duration=current_time-frenzy_paused_at
                if frenzy_active:
                    frenzy_start_time+=paused_duration
                last_frenzy_time+=current_time-frenzy_paused_at
                frenzy_paused_at=0
            if frenzy_active:
                 if current_time-frenzy_start_time>=frenzy_duration:
                     frenzy_active=False
                     frenzy_strawberries.clear()
                     last_frenzy_time=current_time
            elif current_time-last_frenzy_time>=frenzy_interval:
                 frenzy_active=True
                 frenzy_start_time=current_time
                 frenzy_count=random.randint(20,25)
                 frenzy_strawberries= spawn_frenzy_strawberries(snake, mud_patches, food, frenzy_count)

    #managing the temporary frostberry effect
    if frost_active and not paused:
        if current_time-frost_start_time>=frost_duration:
            frost_active=False
            move_delay=normal_move_delay
        else:
            move_delay=int(normal_move_delay*frost_slowdown)

    #updating sparkle particles
    for particle in sparkles[:]:
        particle["x"]+=particle["vx"]
        particle["y"]+=particle["vy"]
        particle["life"]-=1
        if particle["life"]<=0:
            sparkles.remove(particle)
    #updating berry burst particles
    for particle in berry_bursts[:]:
        particle["x"]+=particle["vx"]
        particle["y"]+=particle["vy"]
        particle["life"]-=1
        if particle["life"]<=0:
            berry_bursts.remove(particle)
    #updating special collection rings
    for ring in collection_rings[:]:
        ring["radius"]+=2
        ring["life"]-=1
        if ring["life"]<=0:
            collection_rings.remove(ring)
    #updating floating score popups
    for popup in score_popups[:]:
        popup["y"]-=1
        popup["life"]-=1
        if popup["life"]<=0:
            score_popups.remove(popup)

    if game_started and not game_over and not paused and current_time-last_move >= move_delay:
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
            #checking if the snake collected a harvest frenzy strawberry
            collected_frenzy_berry=None
            collected_berry_type=None
            if frenzy_active:
                for berry in frenzy_strawberries:
                    if new_head==berry["position"]:
                        collected_frenzy_berry=berry
                        break
            collected_normal_food=new_head==food
            if collected_frenzy_berry is not None:
                berry_type=collected_frenzy_berry["type"]
                create_berry_burst(new_head, berry_type)
                if berry_type in ("golden","rainbow"):
                    create_collection_ring(new_head, berry_type)
                if berry_type=="golden":
                    score+=5
                    create_sparkles(new_head)
                elif berry_type=="frost":
                    score+=3
                    frost_active=True
                    frost_start_time=current_time
                else:
                    score+=1
                frenzy_strawberries.remove(collected_frenzy_berry)
            elif collected_normal_food:
                berry_type=("rainbow" if rainbow_food else "frost" if frost_food else "golden" if golden_food else "normal")
                create_berry_burst(new_head, berry_type)
                if rainbow_food:
                    score+=rainbow_bonus
                    create_sparkles(new_head)
                elif frost_food:
                    score+=3
                    frost_active=True
                    frost_start_time=current_time
                elif golden_food:
                    score=score+5
                    create_sparkles(new_head)
                else:
                    score=score+1
                create_score_popups(new_head, rainbow_bonus if rainbow_food else 3 if frost_food else 5 if golden_food else 1)
                food, golden_food, frost_food, rainbow_food=spawn_food(snake, score, mud_patches)
            else:
                snake.pop()
            if collected_frenzy_berry is not None or collected_normal_food:
                 tail_col, tail_row=snake[-1]
                 growth_effects.append({"position": (tail_col, tail_row), "life":18})
            if score>best_score:
                best_score=score
                save_best_score(best_score)
        last_move=current_time
    #3. drawing the background
    for row in range(height//cell_size):
        for col in range(width//cell_size):
            tile_colour= grass_light if(row+col)%2==0 else grass_dark
            pygame.draw.rect(screen, tile_colour, (col*cell_size, row*cell_size, cell_size, cell_size))
    #blue tint while Frostberry effect is active
    if frost_active:
        frost_overlay=pygame.Surface((width, height), pygame.SRCALPHA)
        frost_overlay.fill(frost_overlay_colour)
        screen.blit(frost_overlay, (0,0))
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
    if rainbow_food:
        draw_strawberry(food_x, food_y, "rainbow")
    elif frost_food:
        draw_strawberry(food_x, food_y, "frost")
    elif golden_food:
        draw_strawberry(food_x, food_y, "golden")
    else:
        draw_strawberry(food_x, food_y, "normal")
    if frenzy_active:
        for berry in frenzy_strawberries:
            berry_x=berry["position"][0]*cell_size
            berry_y=berry["position"][1]*cell_size
            draw_strawberry(berry_x, berry_y, berry["type"])
    if frenzy_active:
        frenzy_font=pygame.font.Font(None,34)
        frenzy_text=frenzy_font.render("HARVEST FRENZY!", True, golden_yellow)
        screen.blit(frenzy_text, frenzy_text.get_rect(center=(width//2,145)))
    #drawing the particles
    for particle in sparkles:
        radius=max(1, particle["life"]//10)
        pygame.draw.circle(screen, golden_yellow, (int(particle["x"]), int(particle["y"])), radius)
    #drawing berry burst particles
    for particle in berry_bursts:
        size=max(1,particle["life"]//7)
        pygame.draw.rect(screen, particle["colour"], (int(particle["x"]), int(particle["y"]), size, size))
    #drawing special collection rings
    for ring in collection_rings:
        ring_surface=pygame.Surface((width, height), pygame.SRCALPHA)
        alpha=int(255*ring["life"]/18)
        pygame.draw.circle(ring_surface,(*ring["colour"], alpha), (int(ring["x"]), int(ring["y"])), ring["radius"],2)
        screen.blit(ring_surface,(0,0))
    #updating snake growth animations
    for effect in growth_effects[:]:
        effect["life"]-=1
        if effect["life"]<=0:
            growth_effects.remove(effect)
    #drawing floating score popups with a fade effect
    for popup in score_popups:
        popup_font=pygame.font.Font(None, 28)
        popup_text=popup_font.render(popup["text"], True, popup_colour)
        popup_text.set_alpha(int(255*popup["life"]/40))
        popup_rect=popup_text.get_rect(center=(int(popup["x"]), int(popup["y"])))
        screen.blit(popup_text, popup_rect)
    #drawing the snake
    for index, (col, row) in enumerate(snake):
        x=col*cell_size
        y=row*cell_size
        colour=snake_head if index==0 else snake_green
        pygame.draw.rect(screen, colour, (x+1, y+1, cell_size-2, cell_size-2), border_radius=5)
        if index!=0:
            pygame.draw.rect(screen, grass_accent, (x+5, y+5, 4, 4))
        if index==0:#eyes that move acc to direction
            dx, dy=direction
            if dx==1: #moving right
                eyes=[(x+12, y+4), (x+12, y+12)]
            elif dx==-1: #moving left
                eyes=[(x+4, y+4), (x+4, y+12)]
            elif dy==-1: #moving up
                eyes= [(x+4, y+4), (x+12, y+4)]
            else: #moving down
                eyes=[(x+4, y+12), (x+12, y+12)]
            for eye_x, eye_y in eyes:
                pygame.draw.rect(screen, white, (eye_x, eye_y, 5,5))
                pygame.draw.rect(screen, dark_green, (eye_x+1, eye_y+1, 3,3))
            if tongue_visible:
                tongue_colour=strawberry_red
                if dx==1: #right
                    pygame.draw.line(screen, tongue_colour, (x+18, y+10), (x+21, y+10),2)
                    pygame.draw.line(screen, tongue_colour, (x+21, y+10), (x+23, y+7), 2)
                    pygame.draw.line(screen, tongue_colour, (x+21, y+10), (x+23, y+13), 2)
                elif dx==-1: #left
                    pygame.draw.line(screen, tongue_colour, (x+2, y+10), (x-1, y+10),2)
                    pygame.draw.line(screen, tongue_colour, (x-1, y+10), (x-3, y+7),2)
                    pygame.draw.line(screen, tongue_colour, (x-1, y+10), (x-3, y+13),2)
                elif dy==-1:#up
                    pygame.draw.line(screen, tongue_colour, (x+2, y+10), (x-1, y+10), 2)
                    pygame.draw.line(screen, tongue_colour, (x+10, y-1), (x+7, y-3),2)
                    pygame.draw.line(screen, tongue_colour, (x+10, y-1), (x+13, y-3), 2)
                else: #down
                    pygame.draw.line(screen, tongue_colour, (x+10, y+18), (x+10, y+21),2)
                    pygame.draw.line(screen, tongue_colour, (x+10, y+21), (x+7, y+23),2)
                    pygame.draw.line(screen, tongue_colour, (x+10, y+21), (x+13, y+23),2)
    #drawing snake growth effects
    for effect in growth_effects:
        col, row=effect["position"]
        progress=effect["life"]/18
        size=int(10+10*progress)
        inset=(cell_size-size)//2
        glow_colour=(175, 220, 130)
        pygame.draw.rect(screen, glow_colour, (col*cell_size+inset, row*cell_size+inset, size, size), width=3, border_radius=5)

    #drawing score, title and subtitle
    pygame.draw.rect(screen, hud_panel, (10, 10, 175, 60), border_radius=6)
    pygame.draw.rect(screen, hud_border, (10, 10, 175, 60), 2, border_radius=6)
    score_text=subtitle_font.render(f"Berries: {score}", True, dark_green)
    best_text=subtitle_font.render(f"Best: {best_score}", True, snake_green)
    screen.blit(score_text, (18,17))
    screen.blit(best_text, (18,42))
    if frost_active:
        frost_font=pygame.font.Font(None, 30)
        frost_text=frost_font.render("FROSTED!", True, frostberry_blue)
        screen.blit(frost_text, (20, 68))
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
        #central garden-themed panel
        panel_rect=pygame.Rect(150, 165, 500, 280)
        pygame.draw.rect(screen, hud_panel, panel_rect, border_radius=20)
        game_over_font= pygame.font.Font(None, 60)
        message_font=pygame.font.Font(None,30)
        small_font=pygame.font.Font(None, 25)
        game_over_text= game_over_font.render("Garden Over!", True, dark_green)
        best_message= message_font.render(f"Best garden score: {best_score}", True, popup_colour)
        score_message= message_font.render(f"Strawberries collected: {score}", True, snake_green)
        restart_message=message_font.render("Press R to try again", True, dark_green)
        screen.blit(game_over_text, game_over_text.get_rect(center= (width//2, 220)))
        screen.blit(score_message, score_message.get_rect(center=(width//2, 280)))
        screen.blit(best_message, best_message.get_rect(center=(width//2, 325)))
        screen.blit(restart_message, restart_message.get_rect(center=(width//2, 385)))
        #tiny flower decorations
        pygame.draw.circle(screen, petal_pink, (180, 195), 7)
        pygame.draw.circle(screen, flower_yellow, (180, 195), 3)
        pygame.draw.circle(screen, petal_pink, (620, 415), 7)
        pygame.draw.circle(screen, flower_yellow, (620, 415), 3)    
        #pause screen
    elif paused:
        overlay=pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((242, 248, 232, 220))
        screen.blit(overlay, (0,0))
        #garden themes central panel
        panel_rect=pygame.Rect(190,190, 420,220)
        pygame.draw.rect(screen, hud_panel, panel_rect, border_radius=18)
        pygame.draw.rect(screen, hud_border, panel_rect, 4, border_radius=18)
        pause_font=pygame.font.Font(None, 54)
        instruction_font= pygame.font.Font(None, 29)
        small_font=pygame.font.Font(None, 23)
        pause_text= pause_font.render("Garden Paused", True, dark_green)
        resume_text=instruction_font.render("Press P to resume", True, snake_green)
        hint_text=small_font.render("Take a little breather!", True, popup_colour)
        screen.blit(pause_text, pause_text.get_rect(center=(width//2, 245)))
        screen.blit(resume_text, resume_text.get_rect(center=(width//2, 305)))
        screen.blit(hint_text, hint_text.get_rect(center=(width//2, 350)))
        #tiny decorative flowers
        pygame.draw.circle(screen, petal_pink, (220, 215), 6)
        pygame.draw.circle(screen, flower_yellow, (220, 215), 3)
        pygame.draw.circle(screen, petal_pink, (580, 385), 6)
        pygame.draw.circle(screen, flower_yellow, (580, 385), 3)


    #4. displaying the frame and regulating the refresh rate
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()

