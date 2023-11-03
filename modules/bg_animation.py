from modules.config import WIDTH

def animate_background(list: list, speed: int = -2):
    """Animar el fondo del menú principal y del juego en sí

    Args:
        list (list): de imagenes
        speed (int, optional): velocidad del movimiento del slide del fondo
    """

    background_rect_speed = speed # mover a la izquierda

    for bg_rect in list:
        bg_rect.x += background_rect_speed
        if bg_rect.right <= 0:
            bg_rect.x = WIDTH