import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.fluxo_server.screens.app_bar import AppBar
from fluxo.fluxo_server.screens.footer import Footer
from fluxo.fluxo_server.screens.flow_execution.task import Task
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.task import ModelTask
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow


class FlowExecution(ft.UserControl):
    def __init__(self, log_flow_id):
        super().__init__()
        self.log_flow_id = log_flow_id

    def build(self):
        self.text_name_flow = ft.Ref[ft.Text]()
        self.text_start_end_execution = ft.Ref[ft.Text]()
        self.container_status_execution = ft.Ref[ft.Container]()
        self.responsiverow_tasks = ft.Ref[ft.ResponsiveRow]()

        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.ResponsiveRow(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_BACK_ROUNDED,
                                        on_click=self.iconbutton_go_back,
                                        icon_color=AppThemeColors.BLACK,
                                        icon_size=30
                                    ),
                                    ft.Text(
                                        ref=self.text_name_flow,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.BLACK,
                                        size=20
                                    ), # Text
                                    ft.Text(' > ', size=20, color=AppThemeColors.BLACK_SECONDARY), # Text
                                    ft.Text(
                                        ref=self.text_start_end_execution,
                                        color=AppThemeColors.BLACK,
                                        size=15
                                    ), # Text
                                    ft.Container(
                                        ref=self.container_status_execution,
                                        height=15,
                                        width=15,
                                        border_radius=ft.border_radius.all(15),
                                    ), # Container
                                ], # controls
                            ), # Row
                            ft.Container(
                                content=ft.ResponsiveRow(
                                    ref=self.responsiverow_tasks,
                                    controls=[
                                        
                                    ]
                                ),
                                padding=ft.padding.only(left=50, top=15, right=20, bottom=15)
                            ), # Container
                        ], # controls
                    ), # ResponsiveRow
                    width=900
                ), # Container
                ft.Container(height=0, padding=ft.padding.all(0)),
            ], # controls
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        )
    
    async def iconbutton_go_back(self, e):
        await self.page.go_async('/')

    async def _load_log_flow(self):
        log_flow = ModelLogExecutionFlow.get_by_id(self.log_flow_id)

        # Update name and date execution
        self.text_name_flow.current.value = log_flow.name
        self.text_start_end_execution.current.value = f'({log_flow.date_of_creation} - {log_flow.end_time})'
        
        # Update color status
        if log_flow.end_time is None:
            self.container_status_execution.current.bgcolor = AppThemeColors.BLUE
        elif log_flow.end_time and log_flow.ids_error_task:
            self.container_status_execution.current.bgcolor = AppThemeColors.RED
        else:
            self.container_status_execution.current.bgcolor = AppThemeColors.GREEN

        # Update tasks
        flow = ModelFlow.get_by_id(log_flow.id_flow)
        name_tasks_flow = flow.list_names_tasks

        for name_task in name_tasks_flow:
            self.responsiverow_tasks.current.controls.append(
                Task(log_flow, name_task)
            )
            await self.update_async()

        self.page.session.set('log_flow_id', self.log_flow_id)

    async def did_mount_async(self):
        self.task_load_log_flow = asyncio.create_task(self._load_log_flow())

    async def will_unmount_async(self):
        self.task_load_log_flow.cancel()


def view_flow_execution(log_flow_id: int):

    return ft.View(
        route='flow-execution/:id',
        controls=[
            AppBar(),
            ft.Container(
                content=FlowExecution(log_flow_id),
                expand=True,
                padding=ft.padding.only(left=15, top=0, right=15, bottom=15)
            ),
            Footer()
        ],
        padding=ft.padding.all(0),
        bgcolor=AppThemeColors.WHITE,
    )