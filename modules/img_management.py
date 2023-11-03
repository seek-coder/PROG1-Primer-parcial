def load_img(dir, position):
    """Facilitar la carga de imagenes en forma de surfaces y rects

    Args:
        dir (_type_): dirección de la carpeta/archivo
        position (_type_): posición en la que se pretende ubicar el rect

    """
    from pygame import image

    img = image.load(dir).convert_alpha()
    img_rect = img.get_rect()
    img_rect.topleft = position
    
    return img, img_rect