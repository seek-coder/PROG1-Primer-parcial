def create_button(left: float = 0, top: float = 0, width: float = 100, height: float = 50, color: tuple = (255, 255, 255), color_hover: tuple = (180, 180, 180), border = 0, text: str = "", text_color: tuple = (50, 50, 50)):
    """Crear bloques cuya función principal es la de un botón

    Args:
        left (float, optional): valor de posición desde la izquierda
        top (float, optional): valor de posición desde arriba
        width (float, optional): largo del botón
        height (float, optional): alto del botón
        color (tuple, optional): color del botón
        color_hover (tuple, optional): color del botón al pasar mouse por encima
        border (int, optional): tipo de borde
        text (str, optional): texto del botón
        text_color (tuple, optional): texto del botón al pasar por encima
    """
    from pygame import Rect

    return {
        "button": Rect(left, top, width, height),
        "color": color,
        "color_hover": color_hover,
        "border": border,
        "text": text,
        "text_color": text_color
    }

