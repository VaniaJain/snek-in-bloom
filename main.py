import pygame
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

#fonts
title_font= pygame.font.Font(None, 52)
subtitle_font= pygame.font.Font(None, 25)

#text surfaces
title= title_font.render("Snek in Bloom", True, dark_green)
subtitle=subtitle_font.render("a tiny garden adventure", True, snake_green)

#snake position, meanured in grid cells
snake= [(20,15), (19,15), (18,15)]
direction=(1,0)

#keep the game running till the player closes it
running=True

#handling events such as clicking the close button
while running:
    #1. handling events
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        #keyboard controls
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                direction=(1,0)
            elif event.key in(pygame.K_LEFT, pygame.K_a):
                direction=(-1,0)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                direction=(0,1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                direction=(0,-1)
    #2. moving snake at regular intervals
    current_time=pygame.time.get_ticks()

    if current_time-last_move >= move_delay:
        head_col, head_row=snake[0]
        dx,dy=direction
        new_head=(head_col+dx, head_row+dy)
        #putting the new head at the front and removing the last segment so that the snake stays the same length
        snake.insert(0, new_head)
        snake.pop()
        last_move=current_time
    #3. drawing the background
    screen.fill(background)
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, grid_colour, (x,0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, grid_colour, (0,y), (width, y))

    #drawing the snake
    for index, (col, row) in enumerate(snake):
        x=col*cell_size
        y=row*cell_size
        colour=snake_head if index==0 else snake_green
        pygame.draw.rect(screen, colour, (x+1, y+1, cell_size-2, cell_size-2), border_radius=5)

    #drawing title and subtitle
    screen.blit(title, title.get_rect(center=(width//2, 65)))
    screen.blit(subtitle, subtitle.get_rect(center=(width//2, 100)))

    #4. displaying the frame and regulating the refresh rate
    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()