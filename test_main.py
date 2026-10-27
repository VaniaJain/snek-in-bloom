import asyncio
import pygame

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pygbag Test")

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((190, 230, 190))
        text = font.render("Pygbag works!", True, (30, 90, 50))
        screen.blit(text, (280, 270))
        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
