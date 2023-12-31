import flet as ft
from fluxo.settings import AppThemeColors


class AppBar(ft.UserControl):
    def __init__(sefl):
        super().__init__()

    def build(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Image(
                                    src='icons/icon-512.png',
                                    repeat=ft.ImageRepeat.NO_REPEAT,
                                    fit=ft.ImageFit.CONTAIN,
                                    width=40,
                                    height=40,
                                ),
                                ft.Text(
                                    value='Fluxo',
                                    weight=ft.FontWeight.BOLD,
                                    color=AppThemeColors.BLACK,
                                    size=25
                                ), # Text
                            ]
                        ),
                        on_click=self.on_click_container_home,
                    )
                ],
            ),
            padding=ft.padding.only(left=10, top=5, right=10, bottom=0),
        )
    
    async def on_click_container_home(self, e):
        await self.page.go_async('/')