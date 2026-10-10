import pygame

pygame.init()
pygame.display.set_caption("Platformer Game")
screen = pygame.display.set_mode((900, 500))

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
player_rect = pygame.Rect(100, 440, 40, 60)
platform_rects = []
platform_rects.append(pygame.Rect(200, 400, 200, 20))
platform_rects.append(pygame.Rect(500, 320, 150, 20))
platform_rects.append(pygame.Rect(700, 230, 120, 20))
coin_rects = []
coin_rects.append(pygame.Rect(450, 350, 20, 20))
coin_rects.append(pygame.Rect(550, 290, 20, 20))
coin_rects.append(pygame.Rect(750, 200, 20, 20))
score = 0

y_velocity = 0
x_velocity = 0
gravity = 1
on_ground = True

def draw_score(score):
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
def draw_coins(coins,gold_color=(255, 215, 0)):
    for coin_rect in coins : 
        pygame.draw.rect(screen, gold_color, coin_rect)
def draw_platforms(platform_rects):
    for platform_rect in platform_rects:
        pygame.draw.rect(screen, (0, 255, 0), platform_rect)

running = True
while running:
    clock.tick(60)  # Limit the frame rate to 60 FPS
    x_velocity = 0  # Reset horizontal velocity each frame  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        if player_rect.right < 900:  # Prevent moving off the right edge
            x_velocity = 5
    if keys[pygame.K_LEFT]:
        if player_rect.left > 0:  # Prevent moving off the left edge
            x_velocity = -5
    if keys[pygame.K_SPACE] and on_ground:  # Allow jumping only if on the ground
            y_velocity = -15
    on_ground = False

    # Apply gravity
    y_velocity += gravity
    player_rect.y += y_velocity
    player_rect.x += x_velocity

    for platform_rect in platform_rects:
        if player_rect.colliderect(platform_rect):
            if y_velocity > 0 and player_rect.bottom - y_velocity <= platform_rect.top:
                player_rect.bottom = platform_rect.top
                y_velocity = 0
                on_ground = True  # Reset on_ground when player is on the platform
            if y_velocity < 0 and player_rect.top - y_velocity >= platform_rect.bottom:
                player_rect.top = platform_rect.bottom
                y_velocity = 0
            if x_velocity > 0 and player_rect.right - x_velocity <= platform_rect.left:
                player_rect.right = platform_rect.left
            if x_velocity < 0 and player_rect.left - x_velocity >= platform_rect.right:
                player_rect.left = platform_rect.right
    if player_rect.bottom >= 500:
            player_rect.bottom = 500
            y_velocity = 0  
            on_ground = True  # Reset on_ground when player is on the ground
    for coin_rect in coin_rects.copy():
        if player_rect.colliderect(coin_rect):
            coin_rects.remove(coin_rect)
            score += 1
    screen.fill((50, 50, 255))
    draw_score(score)
    draw_coins(coin_rects)
    pygame.draw.rect(screen, (255, 0, 0), player_rect)
    draw_platforms(platform_rects)
    pygame.display.flip()

pygame.quit()