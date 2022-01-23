import pygame
from pygame import mixer
import os
import random
import csv

# дефолтный экран
HEIGHT = 600
WIDTH = int(HEIGHT * 1.3)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption('Shootshot')
main_ICON = 'img/icons/shootshot.ico'
programIcon = pygame.image.load(main_ICON)
pygame.display.set_icon(programIcon)
# установка частоты кадров
clock = pygame.time.Clock()

# игровве переменные
lines = 16
plitka_raz = HEIGHT // lines

# Гравитация
return_to_earth = 0.80

# Все про уровни
tek_lvl = 1
maximum_lvl = 2

screen_scroll = 0
scroll_background = 0
t_scroll = 200
colonna = 150
plitka_tip = 21

# Переменные старта
game_begin = False
intro_begin = False

# всевозможные действия игрока
left_move = False
right_move = False

shoot = False


mixer.init()

# загрузка музыки и звуков
sound_shootshot = pygame.mixer.Sound('audio/shot.wav')
sound_shootshot.set_volume(0.03)

sound_jump = pygame.mixer.Sound('audio/jump.wav')
sound_jump.set_volume(0.03)

# загрузка картинок

# картинки кнопки
image_exit = pygame.image.load('img/exit.png')
image_exit.convert_alpha()

image_restart = pygame.image.load('img/restart.png')
image_restart.convert_alpha()

image_start = pygame.image.load('img/start.png')
image_start.convert_alpha()

# задний фон
background_first = pygame.image.load('img/background_first.png')
background_first.convert_alpha()


global score
score = 0


def score_for_box():
    global score
    score += 5


def score_for_enemy():
    global score
    score += 10

# хранение плиток в списке list_png
list_png = []
for x in range(plitka_tip):
    list_png.append(pygame.transform.scale(pygame.image.load(f'img/tile/{x}.png'), (plitka_raz, plitka_raz)))

# пуля
bullet_img = pygame.image.load('img/icons/bullet.png')
bullet_img.convert_alpha()

# открывание коробки
health_box_img = pygame.image.load('img/icons/health.png').convert_alpha()
health_box_img.convert_alpha()

ammo_box_img = pygame.image.load('img/icons/ammo.png').convert_alpha()
ammo_box_img.convert_alpha()

damage_box_img = pygame.image.load('img/icons/damage.png').convert_alpha()
damage_box_img.convert_alpha()

all_boxes = {'Ammo': ammo_box_img, 'Health': health_box_img, 'Damage': damage_box_img}
# главный цвет заднего фона
color_background = (150, 199, 119)

pygame.init()

# установка дефолтного шрифта
name_font = 'georgia'
size_font = 17
font = pygame.font.SysFont(name_font, size_font)


class Button:
    def __init__(self, button_x, button_y, image, scale):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (int(self.width * scale), int(self.height * scale)))
        self.rect = self.image.get_rect()
        self.button_x = button_x
        self.button_y = button_y
        self.rect.topleft = (self.button_x, self.button_y)
        self.clicked = False

    def draw(self, surface):
        # проверка наведения и нажатия
        activity = True
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                activity = False
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # рисование кнопки
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return not activity


# нанесение текста
def draw_text(text, font_text, text_col, text_x, text_y):
    screen.blit(font_text.render(text, not False, text_col), (text_x, text_y))


# зарисовка заднего фона
def draw_background():
    screen.fill(color_background)
    for background_x in range(5):
        screen.blit(background_first, ((background_x * background_first.get_width()) - scroll_background * 0.8,
                                       HEIGHT - background_first.get_height()))
        screen.blit(background_first, ((background_x * background_first.get_width()) - scroll_background * 0.5, 0))
        screen.blit(background_first, ((background_x * background_first.get_width()) - scroll_background * 0.6,
                                       HEIGHT - background_first.get_height() - 300))


# обновление уровня
def update_lvl():
    # декорации
    decoration_group.empty()
    water_group.empty()

    # варги
    enemy_group.empty()

    # предметы
    bullet_group.empty()
    item_box_group.empty()

    exit_group.empty()

    # создание пустого списка плит
    empty_list = []
    for _ in range(lines):
        empty_list.append([-1] * colonna)

    return empty_list


class Mir:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        # повторение каждого значения в файле с лвлом
        for mir_y, row in enumerate(data):
            for mir_x, tile in enumerate(row):
                if 21 >= tile >= 0:
                    img = list_png[tile]
                    img_rect = img.get_rect()
                    img_rect.x = mir_x * plitka_raz
                    img_rect.y = mir_y * plitka_raz
                    tile_data = (img, img_rect)
                    if tile in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                        self.obstacle_list.append(tile_data)
                    elif tile in [9, 10]:
                        water = Water(img, mir_x * plitka_raz, mir_y * plitka_raz)
                        water_group.add(water)
                    elif tile in [11, 12, 13, 14]:
                        decoration = Decoration(img, mir_x * plitka_raz, mir_y * plitka_raz)
                        decoration_group.add(decoration)
                    elif tile == 15:  # создание игрока
                        player = People('player', mir_x * plitka_raz, mir_y * plitka_raz, 1.65, 7, 20, 25)
                        player_health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:  # создание врагов
                        enemy = People('enemy', mir_x * plitka_raz, mir_y * plitka_raz, 1.65, 2, 20, 25)
                        enemy_group.add(enemy)
                    elif tile == 17:  # создание коробки с боеприпасами
                        item_box = ItemBox('Ammo', mir_x * plitka_raz, mir_y * plitka_raz)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Damage', mir_x * plitka_raz, mir_y * plitka_raz)
                        item_box_group.add(item_box)
                    elif tile == 19:  # создание ящика для пополнения здоровья
                        item_box = ItemBox('Health', mir_x * plitka_raz, mir_y * plitka_raz)
                        item_box_group.add(item_box)
                    elif tile == 20:  # создание выхода
                        exit = Exit(img, mir_x * plitka_raz, mir_y * plitka_raz)
                        exit_group.add(exit)

        return player, player_health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class People(pygame.sprite.Sprite):
    def __init__(self, char_type, soldier_x, soldier_y, soldier_scale, soldier_speed, ammo, soldier_damage):
        pygame.sprite.Sprite.__init__(self)
        # логические переменные для проверки
        self.alive = self.in_air = self.for_score = True
        self.jump = self.idling = self.flip = False

        self.char_type = char_type
        self.health = 100
        self.max_health = self.health
        self.damage = soldier_damage
        self.speed = soldier_speed
        self.start_ammo = ammo
        self.ammo = ammo

        self.direction = 1
        self.vel_y = self.shoot_cooldown = self.frame_index = self.action = self.move_counter = self.idling_counter = 0

        self.vision = pygame.Rect(0, 0, 150, 20)

        self.animation_list = []

        self.update_time = pygame.time.get_ticks()

        # загрузка всех изображений для игрока
        for animation in ['Idle', 'Run', 'Jump', 'Death']:
            # сброс временного списка изображений
            temp_list = []
            # количество файлов в папке
            for i in range(len(os.listdir(f'img/{self.char_type}/{animation}'))):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                temp_list.append(pygame.transform.scale(img, (int(img.get_width() * soldier_scale),
                                                              int(img.get_height() * soldier_scale))))
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        # прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = (soldier_x, soldier_y)
        # размер
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self, moving_left, moving_right):
        # сброс переменных перемещения
        first_screen_scroll = 0
        dx = dy = 0

        # движение влево и вправо
        if moving_right:
            self.flip = False
            self.direction = 1
            dx = self.speed

        if moving_left:
            self.direction = -1
            dx = -self.speed
            self.flip = True

        # прыжок
        # режим бога - if self.jump
        # для обычного игрока отключено
        if self.jump and not self.in_air:
            self.jump = False
            self.in_air = True
            self.vel_y = -15

        # сила тяжести
        self.vel_y += return_to_earth
        dy += self.vel_y

        # проверка на столкновение
        for tile in mir.obstacle_list:
            # проверка столкновения по х
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # разворот ИИ в случае врезания в стену
                if self.char_type == 'enemy':
                    self.move_counter = 0
                    self.direction *= -1

            # проверка столкновения по у
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # проверка, что он над землей(прыгает)
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0

                # проверка, что он под землей(падает)
                elif self.vel_y >= 0:
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0

        # провереа на столкновение с водой
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # проверка на столкновение с выходом
        first_level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            first_level_complete = True

        # проверка на выход из-за предел карты
        if self.rect.bottom > HEIGHT:
            self.health = 0

        # не выходит ли изображение за края экрана
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > WIDTH:
                dx = 0

        # обновление положения треугольника
        self.rect.x += dx
        self.rect.y += dy

        # обновление прокрутки в зависимости от позиции игрока
        if self.char_type == 'player':
            if (self.rect.right > WIDTH - t_scroll and scroll_background < (
                    mir.level_length * plitka_raz) - WIDTH) \
                    or (self.rect.left < t_scroll and scroll_background > abs(dx)):
                # изменение скрола
                self.rect.x -= dx
                first_screen_scroll = -dx

        return first_screen_scroll, first_level_complete

    def update_animation(self):
        # обновление анимации
        # обновление изображения в зависимости от текущего кадра
        self.image = self.animation_list[self.action][self.frame_index]
        # достаточно ли времени прошло с момента последнего обновления
        if pygame.time.get_ticks() - self.update_time > 100:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # если анимация закончилась, возвращение к началу
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 22
            bullet = Bullet(self.rect.centerx + (0.76 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction, self.damage)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            sound_shootshot.play()

    def update(self):
        self.update_animation()
        self.check_alive()
        # обновление кулдауна
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        # подсчет очков
        if not self.alive and self.for_score:
            score_for_enemy()
            self.for_score = False

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 150) == 1:
                # 0: действие
                self.update_action(0)  # 0: действие

                self.idling_counter = 50
                self.idling = True

            # проверка на нахождение игрока и ИИ
            if self.vision.colliderect(player.rect):
                # остоновка и поворот в сторону игрока
                self.update_action(0)  # 0: idle
                # огонь
                self.shoot()
            else:
                if not self.idling:

                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False

                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)

                    # 1: run
                    self.update_action(1)
                    self.move_counter += 1
                    # обновление видения ИИ по мере продвежения врага
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > plitka_raz:
                        # поворот в другую сторону
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # скрол
        self.rect.x += screen_scroll

    def check_alive(self):
        if self.health <= 0:
            # обнуление всего
            self.speed = self.health = 0
            self.alive = False
            self.update_action(3)

    def update_action(self, new_action):
        # проверка на отличие действия текущего от предудущего
        if new_action != self.action:
            self.action = new_action
            # обновление настройки анамации
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, item_x, item_y):
        pygame.sprite.Sprite.__init__(self)

        self.item_type = item_type
        self.image = all_boxes[self.item_type]
        # прямоугольник
        self.rect = self.image.get_rect()
        self.rect.midtop = (item_x + plitka_raz // 2, item_y + (plitka_raz - self.image.get_height()))

    def update(self):
        # скрол
        self.rect.x += screen_scroll
        # проверка на поднятие игроком коробки
        if pygame.sprite.collide_rect(self, player):
            # проверка на то, что в коробке
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Damage':
                player.damage += 5
            # удаление коробки с поля зрения
            self.kill()
            score_for_box()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_x, bullet_y, bullet_direction, bullet_damage):
        pygame.sprite.Sprite.__init__(self)

        self.image = bullet_img

        # начальные данные
        self.speed = 10
        self.direction = bullet_direction
        self.damage = bullet_damage

        # прямоугольник
        self.rect = self.image.get_rect()
        self.rect.center = (bullet_x, bullet_y)

    def update(self):
        # движение потрона
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # проверка на то, не исчезла ли пуля с экрана
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
        # проверка на то, нет ли столкновения с уровнем
        for tile in mir.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # проверка на столкновение с игроком
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= self.damage
                    self.kill()


class HealthBar:
    def __init__(self, x_health, y_health, health, max_health):
        self.health = health
        self.max_health = max_health

        # расположение
        self.x_health = x_health
        self.y_health = y_health

    def draw(self, health):
        # новое здоровье
        self.health = health
        # расчитывание коэффицента здоровья

        pygame.draw.rect(screen, (255, 0, 0), (self.x_health, self.y_health, 150, 20))
        pygame.draw.rect(screen, (0, 0, 0), (self.x_health - 2, self.y_health - 2, 154, 24))
        pygame.draw.rect(screen, (0, 255, 0), (self.x_health, self.y_health, 150 * self.health / self.max_health, 20))


class ScreenFade:
    def __init__(self, direction_fade, colour_fade, speed_fade):
        self.fade_counter = 0

        # направление исчезания
        self.direction_fade = direction_fade

        # скорость исчезания
        self.speed_fade = speed_fade

        # цвет исчезания
        self.colour_fade = colour_fade

    def fade(self):
        # завершение исчезания
        fade_complete = True
        self.fade_counter += self.speed_fade

        # вертикальный экран исчезает
        if self.direction_fade == 2:
            pygame.draw.rect(screen, self.colour_fade, (0, 0, WIDTH, 0 + self.fade_counter))

        if self.direction_fade == 3:
            pygame.draw.rect(screen, self.colour_fade, (0, 0, WIDTH, 0 + self.fade_counter))

        if self.fade_counter >= WIDTH:
            fade_complete = False

        # исчезание всего экрана
        if self.direction_fade == 1:
            pygame.draw.rect(screen, self.colour_fade, (0, 0 - self.fade_counter, WIDTH, HEIGHT // 2))
            pygame.draw.rect(screen, self.colour_fade, (0 - self.fade_counter, 0, WIDTH // 2, HEIGHT))
            pygame.draw.rect(screen, self.colour_fade, (0, HEIGHT // 2 + self.fade_counter, WIDTH, HEIGHT))
            pygame.draw.rect(screen, self.colour_fade, (WIDTH // 2 + self.fade_counter, 0, WIDTH, HEIGHT))

        return not fade_complete


class Exit(pygame.sprite.Sprite):
    def __init__(self, exit_img, exit_x, exit_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = exit_img

        # прямоугольник
        self.rect = self.image.get_rect()
        self.rect.midtop = (exit_x + plitka_raz // 2, exit_y + (plitka_raz - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, water_img, water_x, water_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = water_img

        # прямоугольник
        self.rect = self.image.get_rect()
        self.rect.midtop = (water_x + plitka_raz // 2, water_y + (plitka_raz - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Decoration(pygame.sprite.Sprite):
    def __init__(self, decoration_img, decoration_img_x, decoration_img_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = decoration_img

        # прямоугольник
        self.rect = self.image.get_rect()
        self.rect.midtop = (decoration_img_x + plitka_raz // 2, decoration_img_y + (plitka_raz - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


# Новый уровень
def update():
    with open(f'lvl{tek_lvl}.csv', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for reader_x, second in enumerate(reader):
            for reader_y, tile in enumerate(second):
                data_mir[reader_x][reader_y] = int(tile)


# создание затухания экрана
transition_fade = ScreenFade(1, (0, 0, 0), 4)
death_fade = ScreenFade(2, (236, 66, 55), 4)
win_fade = ScreenFade(3, (50, 255, 0), 4)

# создание кнопок
button_start = Button(WIDTH // 2 - 130, HEIGHT // 2 - 150, image_start, 1)
button_exit = Button(WIDTH // 2 - 110, HEIGHT // 2 + 50, image_exit, 1)
button_restart = Button(WIDTH // 2 - 100, HEIGHT // 2 - 50, image_restart, 2)

# создание групп спрайтов

enemy_group = pygame.sprite.Group()

# предметы
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

# фон
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

all_groups = [bullet_group, item_box_group, decoration_group, water_group, exit_group]

# создание пустого списка плиток
data_mir = []
for _ in range(lines):
    data_mir.append([-1] * colonna)
# загрузка данных об уровне и создание мира
update()
mir = Mir()

player, health_bar = mir.process_data(data_mir)

run = True
while run:
    # прописываем fps
    clock.tick(60)

    for event in pygame.event.get():
        # выход
        if event.type == pygame.QUIT:
            run = False
        # реакции на нажатия
        if event.type == pygame.KEYDOWN:
            # полноэкранный режим
            if event.key == pygame.K_F1:
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            # дефолтный режим
            if event.key == pygame.K_F2:
                screen = pygame.display.set_mode((WIDTH, HEIGHT))

            # прыжок
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                sound_jump.play()
            # влево
            if event.key == pygame.K_a:
                left_move = True
            # враво
            if event.key == pygame.K_d:
                right_move = True
            # огонь
            if event.key == pygame.K_SPACE:
                shoot = True

            # выход
            if event.key == pygame.K_ESCAPE:
                run = False

        # отпущенная кнопка клавиатуры
        if event.type == pygame.KEYUP:
            # остановка движения
            if event.key == pygame.K_a:
                left_move = False
            if event.key == pygame.K_d:
                right_move = False
            # остановка огня
            if event.key == pygame.K_SPACE:
                shoot = False

    if not game_begin:
        # рисование меню
        screen.fill(color_background)
        # добавление кнопок
        if button_start.draw(screen):
            game_begin = True
            intro_begin = True
        if button_exit.draw(screen):
            run = False
    else:
        # обновление заднего фона
        draw_background()
        # рисование карты
        mir.draw()
        # показывание здоровья
        health_bar.draw(player.health)
        # показывание количества боеприпасов
        draw_text('AMMO: ', font, (255, 255, 255), 10, 35)
        # количество боеприпасов
        count_ammo = player.ammo
        for one in range(count_ammo):
            screen.blit(bullet_img, (90 + (one * 10), 40))

        # обновление и рисовка
        player.update()
        player.draw()

        # включение врагов
        for vrag in enemy_group:
            vrag.ai()
            vrag.update()
            vrag.draw()

        # обновление групп

        for group in all_groups:
            group.update()

        # рисование групп
        for group in all_groups:
            group.draw(screen)

        # показание интро
        if intro_begin:
            if transition_fade.fade():
                intro_begin = False
                transition_fade.fade_counter = 0

        # обновление действий пользователя
        if player.alive:
            # огонь
            if shoot:
                player.shoot()
            if player.in_air:
                player.update_action(2)  # 2: прыжок
            elif left_move or right_move:
                player.update_action(1)  # 1: бег
            else:
                player.update_action(0)  # 0: простаивание

            screen_scroll, level_complete = player.move(left_move, right_move)
            scroll_background -= screen_scroll

            # проверка на прохождения лвла
            if level_complete:
                # проверка на то, что все уровни уже пройдены
                if tek_lvl == maximum_lvl:
                    win_fade.fade()

                    if win_fade.fade():
                        # нельзя ничего сделать после конца
                        for event in pygame.event.get():
                            pass
                        # конечное окно с результатами
                        second_name_font = 'Arial'
                        second_size_font = 50
                        second_font = pygame.font.SysFont(second_name_font, second_size_font)
                        draw_text(f'SCORE: {score}', second_font, (255, 255, 255), WIDTH // 2 - 100, HEIGHT // 2 - 100)
                        if button_restart.draw(screen):
                            # обнуление всего
                            tek_lvl = 1
                            intro_begin = True

                            win_fade.fade_counter = 0
                            scroll_background = 0
                            data_mir = update_lvl()

                            # загрузка данных об новом уровне
                            update()
                            # создание мира
                            mir = Mir()
                            player, health_bar = mir.process_data(data_mir)

                else:
                    intro_begin = True

                    scroll_background = 0
                    # уровни
                    tek_lvl += 1
                    data_mir = update_lvl()
                    if tek_lvl <= maximum_lvl:
                        # загрузка данных об новом уровне
                        update()
                        # создание мира
                        mir = Mir()
                        player, health_bar = mir.process_data(data_mir)

        else:
            screen_scroll = 0

            if death_fade.fade():
                if button_restart.draw(screen):
                    # обнуление всего
                    intro_begin = True

                    death_fade.fade_counter = 0
                    scroll_background = 0
                    data_mir = update_lvl()

                    # загрузка данных об новом уровне
                    update()
                    # создание мира
                    mir = Mir()
                    player, health_bar = mir.process_data(data_mir)

    pygame.display.update()

pygame.quit()
