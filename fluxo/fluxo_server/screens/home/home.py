import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.fluxo_server.screens.home.flow import Flow
from fluxo.fluxo_server.screens.app_bar import AppBar
from fluxo.fluxo_server.screens.footer import Footer
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.app import ModelApp


class Home(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        self.column_flows = ft.Ref[ft.Column]()
        self.responsiverow_flows = ft.Ref[ft.ResponsiveRow]()
        self.text_status_schedule = ft.Ref[ft.Column]()

        return ft.Column(
            ref=self.column_flows,
            controls=[
                ft.Container(height=0),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                value='Flows',
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
                            ft.Container(
                                content=ft.Text(
                                    ref=self.text_status_schedule,
                                    text_align=ft.TextAlign.END,
                                    size=12
                                ), # Text
                                bgcolor=AppThemeColors.GREY,
                                border_radius=ft.border_radius.all(10),
                                padding=ft.padding.only(left=5, top=3, right=5, bottom=3)
                            ),
                        ]
                    ),
                    width=900
                ), # Container
                ft.Container(
                    content=ft.ResponsiveRow(
                        ref=self.responsiverow_flows,
                        controls=[

                        ], # controls
                        alignment=ft.MainAxisAlignment.CENTER
                    ), # ResponsiveRow
                    alignment=ft.alignment.center,
                    width=900
                ), # Container
            ], # controls
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ) # Column
    
    async def _load_flows(self):
        self.responsiverow_flows.current.controls.clear()
        flows = ModelFlow.get_all()
        if flows:
            for flow in flows:
                flow = ModelFlow.get_by_name(flow.name)
                self.responsiverow_flows.current.controls.append(Flow(flow=flow))
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
        flows = ModelFlow.get_all()
        running = []
        for flow in flows:
            running.append(flow.running)
        if not True in running:
            app = ModelApp.get()
            app.active = False
            app.update(app.id, False)

        await self.clean_async()
        await self.did_mount_async()

    async def did_mount_async(self):
        self.task_load_flows = asyncio.create_task(self._load_flows())
        self.task_status_schedule = asyncio.create_task(self._status_schedule())

    async def will_unmount_async(self):
        self.task_load_flows.cancel()
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