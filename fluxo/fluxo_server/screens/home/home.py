import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.fluxo_server.screens.home.flow import Flow
from fluxo.fluxo_server.screens.app_bar import AppBar
from fluxo.fluxo_server.screens.footer import Footer
from fluxo.fluxo_core.flows_executor import FlowsExecutor
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.app import ModelApp


class Home(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.flows_executor = FlowsExecutor()

    def build(self):
        self.column_flows = ft.Ref[ft.Column]()
        self.responsiverow_flows = ft.Ref[ft.ResponsiveRow]()

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
                                message='Update new Flow',
                                content=ft.FloatingActionButton(
                                    content=ft.Text(
                                        value='Update new Flow', 
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.WHITE
                                    ),
                                    bgcolor=AppThemeColors.PRIMARY,
                                    width=140,
                                    height=27,
                                    on_click=self.on_click_floatingactionbutton_update_new_flow
                                ),
                                bgcolor=AppThemeColors.QUARTENARY
                            ),
                            ft.Tooltip(
                                message='Synchronize',
                                content=ft.FloatingActionButton(
                                    content=ft.Icon(
                                        name=ft.icons.SYNC,
                                        color=AppThemeColors.WHITE
                                    ),
                                    bgcolor=AppThemeColors.PRIMARY,
                                    width=50,
                                    height=27,
                                    on_click=self.on_click_floatingactionbutton_sync
                                ),
                                bgcolor=AppThemeColors.QUARTENARY
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
                self.responsiverow_flows.current.controls.append(Flow(flow=flow, flows_executor=self.flows_executor))
                await self.update_async()

    async def on_click_floatingactionbutton_update_new_flow(self, e):
        self.flows_executor.update_new_flow_in_python_files()

        await self.clean_async()
        await self._load_flows()

    async def on_click_floatingactionbutton_sync(self, e):
        await self.clean_async()
        await self.did_mount_async()

    async def did_mount_async(self):
        self.task_load_flows = asyncio.create_task(self._load_flows())

    async def will_unmount_async(self):
        self.task_load_flows.cancel()


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