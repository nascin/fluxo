import flet as ft
import asyncio
from datetime import timedelta
from fluxo.settings import AppThemeColors
from fluxo.uttils import convert_str_to_datetime
from fluxo.fluxo_server.screens.footer import Footer
from fluxo.fluxo_core.database.task import Task as ModelTask
from fluxo.fluxo_core.database.fluxo import Fluxo as ModelFluxo


class Task(ft.UserControl):
    def __init__(self, task_id: int):
        super().__init__()
        self.task_id = task_id

    def build(self):
        self.text_name_task = ft.Ref[ft.Text]()
        self.text_name_fluxo = ft.Ref[ft.Text]()
        self.container_execution = ft.Ref[ft.Container]()

        self.text_start_time = ft.Ref[ft.Text]()
        self.text_end_time = ft.Ref[ft.Text]()
        self.text_duration = ft.Ref[ft.Text]()
        self.text_error = ft.Ref[ft.Text]()

        return ft.Column(
            controls=[
                ft.Container(height=10), # Container
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
                                        ref=self.text_name_fluxo,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.BLACK,
                                        size=25
                                    ), # Text
                                    ft.Text('>'), # Text
                                    ft.Text(
                                        ref=self.text_name_task,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.BLACK,
                                        size=18
                                    ), # Text
                                    ft.Container(
                                        ref=self.container_execution,
                                        height=20,
                                        width=20,
                                        border_radius=ft.border_radius.all(15),
                                    ), # Container
                                ], # controls
                            ), # Row
                            ft.Container(height=10), # Container
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        ref=self.text_start_time,
                                        color=AppThemeColors.BLACK,
                                        size=15
                                    ), # Text
                                ], # controls
                            ), # Row
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        ref=self.text_end_time,
                                        color=AppThemeColors.BLACK,
                                        size=15
                                    ), # Text
                                ], # controls
                            ), # Row
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        ref=self.text_duration,
                                        color=AppThemeColors.BLACK,
                                        size=15
                                    ), # Text
                                ], # controls
                            ), # Row
                            ft.Row(
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
                                        width=650,
                                        height=300,
                                        bgcolor=AppThemeColors.GREY,
                                        border_radius=ft.border_radius.all(15),
                                        padding=ft.padding.all(10)
                                    ), # Container
                                ], # controls
                            ), # Row
                        ], # controls
                    ), # ResponsiveRow
                    width=700
                ), # Container
            ], # controls
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ) # Column
    
    async def _load_attributes_task(self):
        task = ModelTask.get_by_id(self.task_id)
        fluxo = ModelFluxo.get_by_id(task.fluxo_id)

        self.text_name_fluxo.current.value = fluxo.name
        self.text_name_task.current.value = task.name

        if task.execution_date is None:
            self.container_execution.current.bgcolor = AppThemeColors.BLUE
            self.text_start_time.current.value = f'Start time: {task.start_time}'
            self.text_end_time.current.value = f'End time: -'
            self.text_duration.current.value = f'Duration: -'

        elif task.execution_date and task.error:
            data_start_time = convert_str_to_datetime(task.start_time)
            data_execution_date = convert_str_to_datetime(task.execution_date)
            diference = data_execution_date - data_start_time

            self.container_execution.current.bgcolor = AppThemeColors.RED
            self.text_start_time.current.value = f'Start time: {task.start_time}'
            self.text_end_time.current.value = f'End time: {task.end_time}'
            self.text_duration.current.value = f'Duration: {diference.total_seconds()} seconds'
            self.text_error.current.value = task.error

        elif fluxo.interval.get('minutes'):
            data_start_time = convert_str_to_datetime(task.start_time)
            data_execution_date = convert_str_to_datetime(task.execution_date)
            diference = data_execution_date - data_start_time

            if diference <= timedelta(minutes=fluxo.interval.get('minutes')):
                self.container_execution.current.bgcolor = AppThemeColors.GREEN
                self.text_start_time.current.value = f'Start time: {task.start_time}'
                self.text_end_time.current.value = f'End time: {task.end_time}'
                self.text_duration.current.value = f'Duration: {diference.total_seconds()} seconds'
                self.text_error.current.value = task.error

        elif fluxo.interval.get('hours'):
            data_start_time = convert_str_to_datetime(task.start_time)
            data_execution_date = convert_str_to_datetime(task.execution_date)
            diference = data_execution_date - data_start_time

            if diference <= timedelta(hours=fluxo.interval.get('hours')):
                self.container_execution.current.bgcolor = AppThemeColors.GREEN
                self.text_start_time.current.value = f'Start time: {task.start_time}'
                self.text_end_time.current.value = f'End time: {task.end_time}'
                self.text_duration.current.value = f'Duration: {diference.total_seconds()} seconds'
                self.text_error.current.value = task.error

        elif fluxo.interval.get('days'):
            data_start_time = convert_str_to_datetime(task.start_time)
            data_execution_date = convert_str_to_datetime(task.execution_date)
            diference = data_execution_date - data_start_time

            if diference <= timedelta(days=fluxo.interval.get('days')):
                self.container_execution.current.bgcolor = AppThemeColors.GREEN
                self.text_start_time.current.value = f'Start time: {task.start_time}'
                self.text_end_time.current.value = f'End time: {task.end_time}'
                self.text_duration.current.value = f'Duration: {diference.total_seconds()} seconds'
                self.text_error.current.value = task.error

        await self.update_async()

    async def iconbutton_go_back(self, e):
        self.page.views.pop()
        top_view = self.page.views[-1]
        await self.page.go_async(top_view.route)

    async def did_mount_async(self):
        self.task__load_attributes_task = asyncio.create_task(self._load_attributes_task())

    async def will_unmount_async(self):
        self.task__load_attributes_task.cancel()
    

def view_task(task_id: int):

    return ft.View(
        route='task/:id',
        controls=[
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