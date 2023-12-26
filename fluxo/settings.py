import flet as ft
import os


class AppSettings:
    '''Configurações da aplicação Fluxo'''
    VERSION = 'v0.13.4'
    PORT = 8080
    ASSETS_DIR = 'fluxo_server/assets'

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
    GREEN = ft.colors.GREEN
    RED = ft.colors.RED
    BLUE = ft.colors.BLUE

class Db:
    NAME = 'database_fluxo.sqlite3'
    PATH = os.path.join(os.getcwd(), NAME)

class PathFilesPython:
    FOLDER = 'python_files'
    PATH_FILES_PYTHON = os.path.join(os.getcwd(), FOLDER)

# Fontes
FONTS = {
    'Open Sans': '/fonts/OpenSans-Regular.ttf',
    'Open Sans Bold': '/fonts/OpenSans-Bold.ttf'
}
