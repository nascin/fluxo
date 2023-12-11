import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.fluxo_server.screens.home.fluxo import Fluxo
from fluxo.fluxo_server.screens.app_bar import AppBar
from fluxo.fluxo_server.screens.footer import Footer
from fluxo.fluxo_core.database.fluxo import Fluxo as ModelFluxo
from fluxo.fluxo_core.database.app import App as ModelApp


class Home(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        self.column_fluxos = ft.Ref[ft.Column]()
        self.responsiverow_fluxos = ft.Ref[ft.ResponsiveRow]()
        self.text_status_schedule = ft.Ref[ft.Column]()

        return ft.Column(
            ref=self.column_fluxos,
            controls=[
                ft.Container(height=0),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                value='Fluxos',
                                weight=ft.FontWeight.BOLD,
                                color=AppThemeColors.BLACK,
                                size=25,
                                expand=True
                            ), # Text
                            ft.Tooltip(
                                message='Synchronize',
                                content=ft.IconButton(
                                    icon=ft.icons.SYNC,
                                    icon_color=AppThemeColors.PRIMARY,
                                    on_click=self.on_click_iconbutton_sync
                                ),
                                bgcolor=AppThemeColors.QUARTENARY
                            ),
                            ft.Text(
                                ref=self.text_status_schedule,
                                text_align=ft.TextAlign.END
                            ), # Text
                        ]
                    ),
                    width=700
                ), # Container
                ft.Container(
                    content=ft.ResponsiveRow(
                        ref=self.responsiverow_fluxos,
                        controls=[

                        ], # controls
                        alignment=ft.MainAxisAlignment.CENTER
                    ), # ResponsiveRow
                    alignment=ft.alignment.center,
                    width=700
                ), # Container
            ], # controls
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ) # Column
    
    async def _load_fluxos(self):
        self.responsiverow_fluxos.current.controls.clear()
        fluxos = ModelFluxo.get_all()
        if fluxos:
            for fluxo in fluxos:
                fluxo = ModelFluxo.get_by_name(fluxo.name)
                #self.column_fluxos.current.controls.append(Fluxo(fluxo=fluxo))
                self.responsiverow_fluxos.current.controls.append(Fluxo(fluxo=fluxo))
                await self.update_async()

    async def _status_schedule(self):
        app = ModelApp.get()
        if app:
            if app.active:
                self.text_status_schedule.current.value = 'Schedule ON'
                self.text_status_schedule.current.color = AppThemeColors.GREEN
            else:
                self.text_status_schedule.current.value = 'Schedule OFF'
                self.text_status_schedule.current.color = AppThemeColors.RED
        await self.update_async()

    async def on_click_iconbutton_sync(self, e):
        await self.clean_async()
        await self.did_mount_async()


    async def did_mount_async(self):
        self.task_load_fluxos = asyncio.create_task(self._load_fluxos())
        self.task_status_schedule = asyncio.create_task(self._status_schedule())

    async def will_unmount_async(self):
        self.task_load_fluxos.cancel()
        self.task_status_schedule.cancel()


def view_home():
    home = Home()

    return ft.View(
        route='/',
        controls=[
            AppBar(),
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