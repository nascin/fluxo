import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.screens.home.fluxo import Fluxo
from fluxo.screens.footer import Footer
from fluxo_core.database.fluxo import Fluxo as ModelFluxo


class Home(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        self.column_fluxos = ft.Ref[ft.Column]()

        return ft.Column(
            ref=self.column_fluxos,
            controls=[
                ft.Container(height=10), # Container
                ft.Container(
                    content=ft.Text(
                        value='Fluxos',
                        weight=ft.FontWeight.BOLD,
                        color=AppThemeColors.BLACK,
                        size=25
                    ), # Text
                    width=700
                ), # Container
            ], # controls
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ) # Column
    
    async def _load_fluxos(self):
        fluxos = ModelFluxo.get_all()
        if fluxos:
            for fluxo in fluxos:
                fluxo = ModelFluxo.get_by_name(fluxo.name)
                self.column_fluxos.current.controls.append(Fluxo(fluxo=fluxo))
                await self.update_async()
        
    
    async def did_mount_async(self):
        self.task_load_fluxos = asyncio.create_task(self._load_fluxos())

    async def will_unmount_async(self):
        self.task_load_fluxos.cancel()


def view_home():
    home = Home()

    return ft.View(
        route='/',
        controls=[
            ft.Container(
                content=home,
                expand=True,
                padding=ft.padding.all(15)
            ),
            Footer()
        ],
        padding=ft.padding.all(0),
        bgcolor=AppThemeColors.WHITE,
    )