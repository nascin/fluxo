import flet as ft
import os


class AppSettings:
    '''Configurações da aplicação Fluxo'''
    VERSION = '0.1.0'
    PORT = 777
    ASSETS_DIR = 'fluxo/assets'


class AppThemeColors:
    '''Cores do tema da aplicação Fluxo'''
    PRIMARY = '#6929F2'
    SECONDARY = '#8F49F2'
    TERTIARY = '#BC6BF2'
    QUARTENARY = '#BFA7F2'
    BLACK = ft.colors.BLACK
    BLACK_SECONDARY = ft.colors.BLACK87
    BLACK_TERTIARY = ft.colors.BLACK54
    GREY = '#F2F2F2'
    WHITE = ft.colors.WHITE
    WHITE_SECONDARY = ft.colors.WHITE70

# Fontes
FONTS = {
    'Open Sans': '/fonts/OpenSans-Regular.ttf',
    'Open Sans Bold': '/fonts/OpenSans-Bold.ttf'
}
