import flet as ft
from fluxo.settings import AppSettings, AppThemeColors


class Footer(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        value=AppSettings.VERSION,
                        color=AppThemeColors.BLACK_SECONDARY
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=ft.padding.all(15)
        )