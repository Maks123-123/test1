import pygame
import random
import sys
import json
import os

# Инициализация
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
BASE_FPS = 10
SPEED_BOOST_DURATION = 5000  # миллисекунд

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
GOLD = (255, 215, 0)

# Настройки окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка: бонусная версия")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 30)

# Загрузка рекорда
HIGHSCORE_FILE = "snake_highscore.json"
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f).get("highscore", 0)
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump({"highscore": score}, f)

def show_score(score, highscore, speed_multiplier):
    text_score = font.render(f"Счёт: {score}", True, WHITE)
    text_high = font.render(f"Рекорд: {highscore}", True, WHITE)
    text_speed = font.render(f"Скорость: x{speed_multiplier:.1f}", True, BLUE)
    screen.blit(text_score, (10, 10))
    screen.blit(text_high, (10, 35))
    screen.blit(text_speed, (10, 60))

def get_random_position(snake):
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in snake:
            return (x, y)

def spawn_food(snake, bonus_chance=0.2):
    """
    Создаёт еду с бонусом:
    0.6 - обычная (зелёная), +1 очко, +1 длина
    0.2 - золотая (жёлтая), +3 очка, +2 длина
    0.1 - отравленная (красная), -1 очко, -1 длина
    0.1 - ускорение (синяя), временно увеличивает скорость
    """
    r = random.random()
    pos = get_random_position(snake)
    if r < 0.6:
        return {"pos": pos, "type": "normal", "score": 1, "grow": 1, "color": GREEN}
    elif r < 0.8:
        return {"pos": pos, "type": "gold", "score": 3, "grow": 2, "color": GOLD}
    elif r < 0.9:
        return {"pos": pos, "type": "poison", "score": -1, "grow": -1, "color": RED}
    else:
        return {"pos": pos, "type": "speed", "score": 0, "grow": 0, "color": BLUE, "speed_boost": True}

def game_over_screen(score, highscore):
    screen.fill(BLACK)
    text1 = big_font.render(f"ИГРА ОКОНЧЕНА! Счёт: {score}", True, WHITE)
    text2 = font.render(f"Рекорд: {highscore}", True, WHITE)
    text3 = font.render("Нажмите R для новой игры, Q для выхода", True, WHITE)
    text1_rect = text1.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
    text2_rect = text2.get_rect(center=(WIDTH//2, HEIGHT//2))
    text3_rect = text3.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    screen.blit(text1, text1_rect)
    screen.blit(text2, text2_rect)
    screen.blit(text3, text3_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(10)

def main():
    # Начальные параметры
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = (1, 0)
    next_direction = direction
    food = spawn_food(snake)
    score = 0
    highscore = load_highscore()
    fps = BASE_FPS
    speed_multiplier = 1.0
    speed_boost_end_time = 0

    running = True

    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        direction = next_direction
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Столкновение со стенами (без телепортации)
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            if game_over_screen(score, highscore):
                return main()
            else:
                return

        # Проверка, съели ли еду
        ate_food = (new_head == food["pos"])
        if ate_food:
            # Применяем эффекты еды
            score += food["score"]
            grow = food["grow"]
            if food["type"] == "speed" and "speed_boost" in food:
                speed_boost_end_time = pygame.time.get_ticks() + SPEED_BOOST_DURATION
                speed_multiplier = 1.2
            # Обработка отравленной еды: если змея слишком короткая (<=3), то не укорачиваем
            if food["type"] == "poison" and len(snake) <= 3:
                grow = 0  # не укорачиваем, чтобы не умереть сразу
            # Изменяем длину
            for _ in range(grow if grow > 0 else 0):
                snake.insert(0, new_head)
            if grow < 0:
                for _ in range(-grow):
                    if len(snake) > 1:
                        snake.pop()
            # Спавним новую еду
            food = spawn_food(snake)
        else:
            # Обычное движение
            snake.insert(0, new_head)
            snake.pop()

        # Проверка столкновения с собой
        if snake[0] in snake[1:]:
            if game_over_screen(score, highscore):
                return main()
            else:
                return

        # Обновление скорости (если закончился буст)
        if speed_boost_end_time and pygame.time.get_ticks() > speed_boost_end_time:
            speed_multiplier = 1.0
            speed_boost_end_time = 0

        # Обновление FPS с множителем
        current_fps = int(BASE_FPS * speed_multiplier)
        if current_fps < 3:
            current_fps = 3

        # Отрисовка
        screen.fill(BLACK)

        # Рисуем сетку (опционально)
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))

        # Еда
        fx, fy = food["pos"]
        pygame.draw.rect(screen, food["color"],
                         (fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Змейка
        for i, (sx, sy) in enumerate(snake):
            color = DARK_GREEN if i == 0 else GREEN
            pygame.draw.rect(screen, color,
                             (sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        show_score(score, highscore, speed_multiplier)
        pygame.display.flip()
        clock.tick(current_fps)

        # Обновление рекорда после каждого шага (если побит)
        if score > highscore:
            highscore = score
            save_highscore(highscore)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()