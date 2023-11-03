import pygame
import random
import json
from modules.config import *
from modules.buttons import create_button
from assets.sound import *
from modules.img_management import load_img
from modules.bg_animation import animate_background
from data import *

pygame.init()
try:
    with open("data/score.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    print("No se ha encontrado archivo")


points_count_list = []
pause_music = False

def death():
    """Control de la fase de game over
    """

    points_count = points_count_list[-1]
    clock = pygame.time.Clock()
    game_over = True
    pygame.display.set_caption("My friend Capybara")
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) 

    game_over, game_over_rect = load_img("./assets/img/game_over.png", (0, 0))
    pygame.mixer.music.stop()
    font = pygame.font.Font(None, 26)
    user_text = ""

    while game_over:
        clock.tick(FPS)

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.KEYDOWN:
                if len(user_text) < 12:
                    if event.key == pygame.K_RETURN:
                        print("El usuario escribe:", user_text)
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode
                
                if event.key == pygame.K_RETURN:
                    if user_text.strip():
                        user_text += event.unicode
                        entry = {"name": user_text, "score": points_count_list[-1]}
                        data.append(entry)
                        with open("data/new_score.json", 'w') as file:
                            json.dump(data, file)
                    user_text = ""

                    play()

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                    
        
        # --- carga del game_over
        screen.blit(game_over, game_over_rect)
        text_surface = font.render(user_text, True, BLACK)
        points_surface = font.render(str(points_count), True, BLACK)
        screen.blit(text_surface, (WIDTH / 2 - 60, HEIGHT - 133))
        screen.blit(points_surface, (WIDTH / 2 - 60, HEIGHT - 211))

        pygame.display.flip()

def pause():
    """Control de la fase de pausa
    """
    clock = pygame.time.Clock() # controlador del framerate
    paused = True
    pygame.display.set_caption("My friend Capybara [EN JUEGO]")
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
    pygame.mixer.music.pause()
    font = pygame.font.Font(None, 26)
    pause_text = "EN PAUSA. Presiona 'ESC' para continuar o 'Q' para salir del juego"

    while paused:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.unpause()
                    paused = False

                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                    

        pause_text_surface = font.render(pause_text, True, BLACK)
        screen.fill(WHITE)
        screen.blit(pause_text_surface, (WIDTH / 2 - 260, HEIGHT - 60))
        pygame.display.flip()

def play():
    """Control de la fase de juego
    """
    points_count = 0
    # A) VARIABLES
    # --- bucle principal
    running = True

    game_over = False

    # --- contadores
    lives_count = 3
    # --- movimiento del jugador
    gravity_y = 0.65
    player_speed_x, player_speed_y = 5, 0
    player_initial_x, player_initial_y = 0, 336

    right = left = space = jumping = False

    # --- otros movimientos
    animals_initial_x, animals_initial_y = WIDTH + 200, player_initial_y + 20

    # --- manejo de tiempos
    bad_animals_cooldown = random.randrange(1000, 1500)
    good_animals_cooldown = random.randrange(1000, 2000)
    food_cooldown = random.randrange(1000, 2500)

    # B) CONFIGURACIÓN GENERAL

    # --- eventos de aparición aleatoria de enemigos
    GOOD_APPEAR = pygame.USEREVENT + 1 # donde el 1 representa el evento
    pygame.time.set_timer(GOOD_APPEAR, good_animals_cooldown)

    BAD_APPEAR = pygame.USEREVENT + 2 # donde el 1 representa el evento
    pygame.time.set_timer(BAD_APPEAR, bad_animals_cooldown)

    FOOD_APPEAR = pygame.USEREVENT + 3 # donde el 1 representa el evento
    pygame.time.set_timer(FOOD_APPEAR, food_cooldown)

    # --- cargar música de fondo
    pygame.mixer.init()
    if pause_music == False:
        pygame.mixer.music.load("./assets/sound/ost.wav")
        pygame.mixer.music.set_volume(0.4) 
        # inicio de música
        pygame.mixer.music.play(-1) # -1 es para dejar en bucle infinito
    hit_wav = pygame.mixer.Sound("./assets/sound/hit.wav")
    goal_wav = pygame.mixer.Sound("./assets/sound/goal.wav")
    dead_wav = pygame.mixer.Sound("./assets/sound/dead.wav")
    food_wav = pygame.mixer.Sound("./assets/sound/food.wav")
    clock = pygame.time.Clock() # controlador del framerate

    pygame.display.set_caption("My friend Capybara [EN JUEGO]")

    font = pygame.font.Font(None, 36)
    life_points_text = font.render(f"VIDAS: 3", False, WHITE)
    # C) PANTALLA
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
    # --- carga del fondo, conformado por dos imágenes que van moviéndose hacia la izquierda y saltando al otro lado de la pantalla para dar un efecto de slide
    background_front, background_front_rect = load_img("./assets/img/bg_front.png", (-(WIDTH // 2), 0))
    background_back, background_back_rect = load_img("./assets/img/bg_back.png", (-(WIDTH // 2), 0))
    background_front_2, background_front_rect_2 = load_img("./assets/img/bg_front.png", ((WIDTH // 2), 0))
    background_back_2, background_back_rect_2 = load_img("./assets/img/bg_back.png", ((WIDTH // 2), 0))
    background_rect_list = [background_back_rect, background_back_rect_2, background_front_rect, background_front_rect_2]

    # --- carga del jugador
    player, player_rect = load_img("./assets/img/player.png", (player_initial_x, player_initial_y))


    # --- listas
    # --- --- animales buenos
    good_animals_list = []
    bad_animals_list = []
    food_list = []

    good_animals_that_touch_player = []
    bad_animals_that_hit_player = []
    food_eaten = []

    difficulty_checkpoints = [300, 600, 900, 1200, 1500]
    quantity = len(difficulty_checkpoints)

    while running:
        clock.tick(FPS)
        # 1. DETECTAR EVENTOS
        # --- controlador de eventos
        if lives_count == 0:
            points_count_list.append(points_count)
            pygame.mixer.music.stop()
            pygame.time.delay(500)
            dead_wav.play()
            death()
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                

            # --- si se presiona la tecla
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    right = True
                elif event.key == pygame.K_LEFT:
                    left = True
                elif event.key == pygame.K_SPACE:
                    space = True
                if event.key == pygame.K_ESCAPE:
                    pause()

            # --- si se suelta la tecla
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    right = False
                elif event.key == pygame.K_LEFT:
                    left = False
                elif event.key == pygame.K_SPACE:
                    space = False

            if event.type == GOOD_APPEAR or event.type == BAD_APPEAR or event.type == FOOD_APPEAR:
                roulette = random.randint(0, 6)
                print(event.type)
                print(roulette)

            if event.type == GOOD_APPEAR:# cada vez que pasan los segundos randoms de 1 a 4, se llega a esta condición donde se hace una ruleta
                if roulette == 0: # si la ruleta da 0, ocurre el evento solicitado
                    cocodrile, cocodrile_rect = load_img("./assets/img/cocodrile.png", (animals_initial_x, animals_initial_y))
                    good_animals_list.append((cocodrile, cocodrile_rect))
                if roulette == 1:
                    turtle, turtle_rect = load_img("./assets/img/turtle.png", (animals_initial_x, animals_initial_y + 4))
                    good_animals_list.append((turtle, turtle_rect))
                if roulette == 2:
                    bird, bird_rect = load_img("./assets/img/bird.png", (animals_initial_x, animals_initial_y - 180))
                    good_animals_list.append((bird, bird_rect))

            if event.type == BAD_APPEAR:
                if roulette == 0 or roulette == 4:
                    bad_cocodrile, bad_cocodrile_rect = load_img("./assets/img/bad_cocodrile.png", (animals_initial_x, animals_initial_y + 15))
                    bad_cocodrile_rect = bad_cocodrile_rect.inflate(-60, -30)
                    bad_animals_list.append((bad_cocodrile, bad_cocodrile_rect))
                if roulette == 1:
                    bad_turtle, bad_turtle_rect = load_img("./assets/img/bad_turtle.png", (animals_initial_x, animals_initial_y + 20))
                    bad_turtle_rect = bad_turtle_rect.inflate(-60, -30)
                    bad_animals_list.append((bad_turtle, bad_turtle_rect))
                if roulette == 2 or roulette == 5:
                    bad_bird, bad_bird_rect = load_img("./assets/img/bad_bird.png", (animals_initial_x, animals_initial_y - 10))
                    bad_bird_rect = bad_bird_rect.inflate(-60, -30)
                    bad_animals_list.append((bad_bird, bad_bird_rect))
                if roulette == 3:
                    bad_bird, bad_bird_rect = load_img("./assets/img/bad_bird.png", (animals_initial_x, animals_initial_y - 100))
                    bad_bird_rect = bad_bird_rect.inflate(-60, -30)
                    bad_animals_list.append((bad_bird, bad_bird_rect))

            if event.type == FOOD_APPEAR:   
                if roulette == 6:
                    watermelon, watermelon_rect = load_img("./assets/img/watermelon.png", (animals_initial_x, animals_initial_y - 100))
                    food_list.append((watermelon, watermelon_rect))
        # 2. ACTUALIZAR EVENTOS / IMÁGENES
        # --- texto

        # 3. DIBUJAR PANTALLA (RENDERIZAR)
        screen.fill(CYAN)

        # --- movimiento hacia la izquierda del fondo
        animate_background(background_rect_list)

        # --- control del movimiento del jugador
        if right:
            player_rect.x += player_speed_x
        if left:
            player_rect.x -= player_speed_x 

        # --- manejo del salto
        if space and not jumping:
            player_speed_y = 17
            jumping = True
        
        if jumping: # si se está saltando
            player_speed_y -= gravity_y # permite que el movimiento sea más curvo y BAJE al personaje, porque hay un valor que se va restando en cada frame
            player_rect.y -= player_speed_y # cuando el valor de speed pasa de positivo a negativo, el personaje empieza a caer
            
            if player_rect.y >= player_initial_y: # cuando el jugador vuelve a Y inicial
                player_speed_y = 0
                jumping = False 

        # --- límite del jugador en la pantalla
        if player_rect.left <= 0:
            player_rect.left = 0
        elif player_rect.right >= WIDTH:
            player_rect.right = WIDTH

        screen.blit(background_back, background_back_rect)
        screen.blit(background_back_2, background_back_rect_2)

        # --- movimiento de animales

        # -------------- GOOD ANIMALS -------------- #
        player.set_alpha(255)
        points_text = font.render(f"PUNTUACIÓN: {int(points_count):08d}", False, WHITE)

        for surface, rect in good_animals_list:
            # pygame.draw.rect(screen, GREEN, rect)
            try:
                rect.x -= 3
                for checkpoint in range(quantity):
                    if points_count >= difficulty_checkpoints[checkpoint]:
                        rect.x -= 1.4

                screen.blit(surface, rect)
                
                if player_rect.colliderect(rect):
                    if rect not in good_animals_that_touch_player:
                        goal_wav.play()
                        points_count += 100
                        surface.set_alpha(150)
                    good_animals_that_touch_player.append(rect)

                good_animals_list = [animal for animal in good_animals_list if animal[1].right > 0]
            except TypeError:
                print("Sólo se puede asignar enteros a este atributo")
        # -------------- BAD ANIMALS -------------- #
        for surface, rect in bad_animals_list:
            # pygame.draw.rect(screen, RED, rect)
            try:
                rect.x -= 5
                screen.blit(surface, (rect[0] - 40, rect[1] - 30))
                for checkpoint in range(quantity):
                    if points_count >= difficulty_checkpoints[checkpoint]:
                        rect.x -= 1.6

                if player_rect.colliderect(rect):
                    if rect not in bad_animals_that_hit_player:
                        hit_wav.play()
                        if lives_count <= 3 and lives_count > 0:
                            life_points_text = font.render(f"VIDAS: {lives_count - 1}", False, (WHITE))
                            lives_count -= 1
                        bad_animals_that_hit_player.append(rect)
                    player.set_alpha(130)

                bad_animals_list = [animal for animal in bad_animals_list if animal[1].right > 0]
            except NameError:
                print("Nombre no definido")


        # -------------- FOOD -------------- #
        for surface, rect in food_list:
            rect.x -= 10
            screen.blit(surface, rect)

            if player_rect.colliderect(rect):
                    if rect not in food_eaten:
                        food_wav.play()
                        points_count += 50
                        surface.set_alpha(0)
                    food_eaten.append(rect)
            food_list = [food for food in food_list if food[1].right > 0]

        screen.blit(player, player_rect)
            
        screen.blit(background_front, background_front_rect)
        screen.blit(background_front_2, background_front_rect_2)

        screen.blit(points_text, (60, 40))
        screen.blit(life_points_text, (WIDTH - 160, 40))

        # 4. ACTUALIZAR PANTALLA
        pygame.display.flip()

def rules():
    """Control de la fase de reglas
    """
    clock = pygame.time.Clock()
    rules = True
    pygame.display.set_caption("My friend Capybara")
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) 

    rules, rules_rect = load_img("./assets/img/rules.png", (0, 0))
    pygame.mixer.music.stop()

    while rules:
        clock.tick(FPS)

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    rules = False
                    play()
        
        # --- carga de las reglas
        screen.blit(rules, rules_rect)
        pygame.display.flip()

def options():
    """Control de la fase de opciones
    """
    options_menu = True
    pygame.display.set_caption("My friend Capybara [MENÚ PRINCIPAL]")

    player_initial_x, player_initial_y = 0, 336
    clock = pygame.time.Clock() # controlador del framerate
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
    
    background_front, background_front_rect = load_img("./assets/img/bg_front.png", (-(WIDTH // 2), 0))
    background_back, background_back_rect = load_img("./assets/img/bg_back.png", (-(WIDTH // 2), 0))
    background_front_2, background_front_rect_2 = load_img("./assets/img/bg_front.png", ((WIDTH // 2), 0))
    background_back_2, background_back_rect_2 = load_img("./assets/img/bg_back.png", ((WIDTH // 2), 0))
    background_rect_list = [background_back_rect, background_back_rect_2, background_front_rect, background_front_rect_2]

    player, player_rect = load_img("./assets/img/player.png", (player_initial_x, player_initial_y))
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(ACTUAL_BLACK)
    overlay.set_alpha(120)
    overlay_rect = overlay.get_rect()



    sound_on_button = create_button(WIDTH / 3 - 10, 130, 300, 50, BLACK, GREY, 100, "MUSICA ON", WHITE)
    sound_off_button = create_button(WIDTH / 3 - 10, 230, 300, 50, BLACK, GREY, 100, "MUSICA OFF", WHITE)
    back_button = create_button(WIDTH / 3 - 10, 330, 300, 50, BLACK, GREY, 100, "VOLVER", WHITE)
    
    while options_menu:
        global pause_music
        clock.tick(FPS)

        mouse_x, mouse_y = pygame.mouse.get_pos() # obtener posición del cursor

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                

        if sound_off_button["button"].collidepoint(mouse_x, mouse_y):
            sound_off_button["color"] = sound_off_button["color_hover"]
            if pygame.mouse.get_pressed()[0]: # 0 es el click izquierdo
                pygame.mixer.music.pause()
                pause_music = True
        else:
            sound_off_button["color"] = BLACK

        if sound_on_button["button"].collidepoint(mouse_x, mouse_y):
            sound_on_button["color"] = sound_on_button["color_hover"]
            if pygame.mouse.get_pressed()[0]: # 0 es el click izquierdo
                pygame.mixer.music.unpause()
        else:
            sound_on_button["color"] = BLACK

        if back_button["button"].collidepoint(mouse_x, mouse_y):
            back_button["color"] = back_button["color_hover"]
            if pygame.mouse.get_pressed()[0]: # 0 es el click izquierdo
                pygame.time.delay(200)
                options_menu = False
        else:
            back_button["color"] = BLACK
        
        screen.fill(CYAN)

        animate_background(background_rect_list, -1)
        screen.blit(background_back, background_back_rect)
        screen.blit(background_back_2, background_back_rect_2)
        screen.blit(player, player_rect)
            
        screen.blit(background_front, background_front_rect)
        screen.blit(background_front_2, background_front_rect_2)
        screen.blit(overlay, overlay_rect)

        font = pygame.font.Font(None, 26)
        
        pygame.draw.rect(screen, sound_on_button["color"], sound_on_button["button"], 0, sound_on_button["border"])
        pygame.draw.rect(screen, sound_off_button["color"], sound_off_button["button"], 0, sound_off_button["border"])
        pygame.draw.rect(screen, back_button["color"], back_button["button"], 0, back_button["border"])

        sound_on_button_text = font.render(sound_on_button["text"], True, sound_on_button["text_color"])
        sound_on_button_text_rect = sound_on_button_text.get_rect()
        sound_on_button_text_rect.center = (sound_on_button["button"].centerx, sound_on_button["button"].centery)

        sound_off_button_text = font.render(sound_off_button["text"], True, sound_off_button["text_color"])
        sound_off_button_text_rect = sound_off_button_text.get_rect()
        sound_off_button_text_rect.center = (sound_off_button["button"].centerx, sound_off_button["button"].centery)

        back_button_text = font.render(back_button["text"], True, back_button["text_color"])
        back_button_text_rect = back_button_text.get_rect()
        back_button_text_rect.center = (back_button["button"].centerx, back_button["button"].centery)

        copyright_text = font.render("Creado por Catriel Gatto, 2023", True, WHITE)
        copyright_text_rect = copyright_text.get_rect()
        copyright_text_rect.center = (WIDTH / 2, HEIGHT - 20)
        
        screen.blit(sound_on_button_text, sound_on_button_text_rect)
        screen.blit(sound_off_button_text, sound_off_button_text_rect)
        screen.blit(back_button_text, back_button_text_rect)
        screen.blit(copyright_text, copyright_text_rect)
        
        pygame.display.flip()

def main_menu():
    """Control de la fase de menu principal
    """
    menu = True
    pygame.display.set_caption("My friend Capybara [MENÚ PRINCIPAL]")

    player_initial_x, player_initial_y = 0, 336
    clock = pygame.time.Clock() # controlador del framerate
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
    try:
        background_front, background_front_rect = load_img("./assets/img/bg_front.png", (-(WIDTH // 2), 0))
        background_back, background_back_rect = load_img("./assets/img/bg_back.png", (-(WIDTH // 2), 0))
        background_front_2, background_front_rect_2 = load_img("./assets/img/bg_front.png", ((WIDTH // 2), 0))
        background_back_2, background_back_rect_2 = load_img("./assets/img/bg_back.png", ((WIDTH // 2), 0))
        background_rect_list = [background_back_rect, background_back_rect_2, background_front_rect, background_front_rect_2]
    except ZeroDivisionError:
        print("No puedes dividir por cero")

    player, player_rect = load_img("./assets/img/player.png", (player_initial_x, player_initial_y))
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(ACTUAL_BLACK)
    overlay.set_alpha(120)
    overlay_rect = overlay.get_rect()

    if pause_music == False:
        pygame.mixer.music.load("./assets/sound/menu.wav")
        pygame.mixer.music.set_volume(0.4) 
        pygame.mixer.music.play(-1)

    play_button = create_button(WIDTH / 3 - 10, 130, 300, 50, BLACK, GREY, 100, "JUGAR", WHITE)
    options_button = create_button(WIDTH / 3 - 10, 230, 300, 50, BLACK, GREY, 100, "OPCIONES", WHITE)
    quit_button = create_button(WIDTH / 3 - 10, 330, 300, 50, BLACK, GREY, 100, "SALIR", WHITE)

    while menu:
        clock.tick(FPS)

        mouse_x, mouse_y = pygame.mouse.get_pos() # obtener posición del cursor

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                

        if play_button["button"].collidepoint(mouse_x, mouse_y):
            play_button["color"] = play_button["color_hover"]
            if pygame.mouse.get_pressed()[0]: # 0 es el click izquierdo
                menu = False
                rules()
        else:
            play_button["color"] = BLACK

        if options_button["button"].collidepoint(mouse_x, mouse_y):
            options_button["color"] = options_button["color_hover"]
            if pygame.mouse.get_pressed()[0]: # 0 es el click izquierdo
                pygame.time.delay(200)
                options()
        else:
            options_button["color"] = BLACK

        if quit_button["button"].collidepoint(mouse_x, mouse_y):
            quit_button["color"] = quit_button["color_hover"]
            if pygame.mouse.get_pressed()[0]: # 0 es el click izquierdo
                menu = False
        else:
            quit_button["color"] = BLACK
        
        screen.fill(CYAN)

        animate_background(background_rect_list, -1)
        screen.blit(background_back, background_back_rect)
        screen.blit(background_back_2, background_back_rect_2)
        screen.blit(player, player_rect)
            
        screen.blit(background_front, background_front_rect)
        screen.blit(background_front_2, background_front_rect_2)
        screen.blit(overlay, overlay_rect)

        font = pygame.font.Font(None, 26)
        
        pygame.draw.rect(screen, play_button["color"], play_button["button"], 0, play_button["border"])
        pygame.draw.rect(screen, options_button["color"], options_button["button"], 0, options_button["border"])
        pygame.draw.rect(screen, quit_button["color"], quit_button["button"], 0, quit_button["border"])

        play_button_text = font.render(play_button["text"], True, play_button["text_color"])
        play_button_text_rect = play_button_text.get_rect()
        play_button_text_rect.center = (play_button["button"].centerx, play_button["button"].centery)

        options_button_text = font.render(options_button["text"], True, options_button["text_color"])
        options_button_text_rect = options_button_text.get_rect()
        options_button_text_rect.center = (options_button["button"].centerx, options_button["button"].centery)

        quit_button_text = font.render(quit_button["text"], True, quit_button["text_color"])
        quit_button_text_rect = quit_button_text.get_rect()
        quit_button_text_rect.center = (quit_button["button"].centerx, quit_button["button"].centery)

        copyright_text = font.render("Creado por Catriel Gatto, 2023", True, WHITE)
        copyright_text_rect = copyright_text.get_rect()
        copyright_text_rect.center = (WIDTH / 2, HEIGHT - 20)
        
        screen.blit(play_button_text, play_button_text_rect)
        screen.blit(options_button_text, options_button_text_rect)
        screen.blit(quit_button_text, quit_button_text_rect)
        screen.blit(copyright_text, copyright_text_rect)
        
        pygame.display.flip()

main_menu()

pygame.quit()
