import flet as ft
import asyncio
from datetime import timedelta
from fluxo.settings import AppThemeColors
from fluxo.uttils import convert_str_to_datetime
from fluxo.fluxo_server.screens.app_bar import AppBar
from fluxo.fluxo_server.screens.footer import Footer
from fluxo.fluxo_core.database.task import ModelTask
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow


class Task(ft.UserControl):
    def __init__(self, task_id: int):
        super().__init__()
        self.task_id = task_id

    def build(self):
        self.text_name_task = ft.Ref[ft.Text]()
        self.text_name_flow = ft.Ref[ft.Text]()
        self.container_execution = ft.Ref[ft.Container]()

        self.text_start_time = ft.Ref[ft.Text]()
        self.text_end_time = ft.Ref[ft.Text]()
        self.text_duration = ft.Ref[ft.Text]()
        self.text_error = ft.Ref[ft.Text]()

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
                                        ref=self.text_name_task,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.BLACK,
                                        size=15
                                    ), # Text
                                    ft.Container(
                                        ref=self.container_execution,
                                        height=15,
                                        width=15,
                                        border_radius=ft.border_radius.all(15),
                                    ), # Container
                                ], # controls
                            ), # Row
                            ft.Container(height=10), # Container
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            ref=self.text_start_time,
                                            color=AppThemeColors.BLACK,
                                            size=15
                                        ), # Text
                                    ], # controls
                                ), # Row
                                padding=ft.padding.only(left=50)
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            ref=self.text_end_time,
                                            color=AppThemeColors.BLACK,
                                            size=15
                                        ), # Text
                                    ], # controls
                                ), # Row
                                padding=ft.padding.only(left=50)
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            ref=self.text_duration,
                                            color=AppThemeColors.BLACK,
                                            size=15
                                        ), # Text
                                    ], # controls
                                ), # Row
                                padding=ft.padding.only(left=50)
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            value='Error:',
                                            color=AppThemeColors.BLACK,
                                            size=15
                                        ), # Text
                                        ft.Container(
                                            content=ft.Column(
                                                controls=[
                                                    ft.Text(
                                                        ref=self.text_error,
                                                        color=AppThemeColors.BLACK
                                                    ), # Text
                                                ], # controls
                                                scroll=ft.ScrollMode.ALWAYS,
                                            ), # Column
                                            width=850,
                                            height=300,
                                            bgcolor=AppThemeColors.GREY,
                                            border_radius=ft.border_radius.all(15),
                                            padding=ft.padding.all(10)
                                        ), # Container
                                    ], # controls
                                ), # Row
                                padding=ft.padding.only(left=50)
                            ),
                        ], # controls
                    ), # ResponsiveRow
                    width=900
                ), # Container
                ft.Container(padding=ft.padding.all(0)), # Container
            ], # controls
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ) # Column
    
    async def _load_attributes_task(self):
        task = ModelTask.get_by_id(self.task_id)
        flow = ModelFlow.get_by_id(task.flow_id)

        self.text_name_flow.current.value = flow.name
        self.text_name_task.current.value = task.name

        if task.end_time is None:
            self.container_execution.current.bgcolor = AppThemeColors.BLUE
            self.text_start_time.current.value = f'Start time: {task.start_time}'
            self.text_end_time.current.value = f'End time: -'
            self.text_duration.current.value = f'Duration: -'

        elif task.end_time and task.error:
            data_start_time = convert_str_to_datetime(task.start_time)
            data_execution_date = convert_str_to_datetime(task.execution_date)
            diference = data_execution_date - data_start_time

            self.container_execution.current.bgcolor = AppThemeColors.RED
            self.text_start_time.current.value = f'Start time: {task.start_time}'
            self.text_end_time.current.value = f'End time: {task.end_time}'
            self.text_duration.current.value = f'Duration: {diference.total_seconds()} seconds'
            self.text_error.current.value = task.error

        else:
            data_start_time = convert_str_to_datetime(task.start_time)
            data_execution_date = convert_str_to_datetime(task.execution_date)
            diference = data_execution_date - data_start_time

            self.container_execution.current.bgcolor = AppThemeColors.GREEN
            self.text_start_time.current.value = f'Start time: {task.start_time}'
            self.text_end_time.current.value = f'End time: {task.end_time}'
            self.text_duration.current.value = f'Duration: {diference.total_seconds()} seconds'
            self.text_error.current.value = task.error

        await self.update_async()

    async def iconbutton_go_back(self, e):
        list_log_flow = ModelLogExecutionFlow.get_all()
        for log_flow in list_log_flow:
            if log_flow.ids_task:
                if int(self.task_id) in log_flow.ids_task:
                    await self.page.go_async(f'flow-execution/{log_flow.id}')
            else:
                task = ModelTask.get_by_id(int(self.task_id))
                log_flow_endtime_is_none = ModelLogExecutionFlow.get_by_idflow_and_endtime_is_none(task.flow_id)
                await self.page.go_async(f'flow-execution/{log_flow_endtime_is_none.id}')

    async def did_mount_async(self):
        self.task_load_attributes_task = asyncio.create_task(self._load_attributes_task())

    async def will_unmount_async(self):
        self.task_load_attributes_task.cancel()
    

def view_task(task_id: int):

    return ft.View(
        route='task/:id',
        controls=[
            AppBar(),
            ft.Container(
                content=Task(task_id),
                expand=True,
                padding=ft.padding.all(15)
            ),
            Footer()
        ],
        padding=ft.padding.all(0),
        bgcolor=AppThemeColors.WHITE,
    )