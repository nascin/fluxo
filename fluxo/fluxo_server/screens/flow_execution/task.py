import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.fluxo_server.screens.app_bar import AppBar
from fluxo.fluxo_server.screens.footer import Footer
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.task import ModelTask
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow


class Task(ft.UserControl):
    def __init__(self, log_flow: ModelLogExecutionFlow, name_task: str):
        super().__init__()
        self.log_flow = log_flow
        self.name_task = name_task

    def build(self):
        self.container_task = ft.Ref[ft.Container]()
        self.container_status_execution = ft.Ref[ft.Container]()
        self.text_name_task = ft.Ref[ft.Text]()
        self.text_start_end_execution = ft.Ref[ft.Text]()

        return ft.Container(
            ref=self.container_task,
            content=ft.Row(
                controls=[
                    ft.Container(
                        ref=self.container_status_execution,
                        height=15,
                        width=15,
                        border_radius=ft.border_radius.all(15),
                    ), # Container
                    ft.Text(
                        ref=self.text_name_task,
                        color=AppThemeColors.BLACK,
                        size=15,
                        expand=True
                    ),
                    ft.Text(
                        ref=self.text_start_end_execution,
                        color=AppThemeColors.BLACK,
                        size=10,
                    )
                ]
            ),
            padding=ft.padding.all(15),
            bgcolor=AppThemeColors.GREY,
            border_radius=ft.border_radius.all(10),
            height=50
        )
    
    async def _load_task(self):
        tasks_flow = ModelTask.get_all_by_fluxo_id(self.log_flow.id_flow)
        for task in tasks_flow:
            if self.log_flow.ids_task:
                if task.name == self.name_task and task.id in self.log_flow.ids_task:
                    await self._load_container_status_execution(task)
                    self.container_task.current.on_click = self._on_click_task
                    self.text_name_task.current.value = task.name
                    self.text_start_end_execution.current.value = f'({task.start_time} - {task.end_time})'
                    self.task_id = task.id
                else:
                    if task.name == self.name_task and task.end_time is None:
                        await self._load_container_status_execution(task)
                        self.container_task.current.on_click = self._on_click_task
                        self.text_name_task.current.value = task.name
                        self.text_start_end_execution.current.value = f'({task.start_time} - {task.end_time})'
                        self.task_id = task.id
            else:
                if task.end_time is None and task.name == self.name_task:
                    await self._load_container_status_execution(task)
                    self.container_task.current.on_click = self._on_click_task
                    self.text_name_task.current.value = task.name
                    self.text_start_end_execution.current.value = f'({task.start_time} - {task.end_time})'
                    self.task_id = task.id
                else:
                    self.container_task.current.on_click = None
                    self.container_status_execution.current.bgcolor = AppThemeColors.WHITE
                    self.text_name_task.current.value = self.name_task
                    self.text_start_end_execution.current.value = 'Execution not yet started'

            await self.update_async()

    async def _load_container_status_execution(self, task):
        if task.end_time is None:
            self.container_status_execution.current.bgcolor = AppThemeColors.BLUE
        elif task.end_time and task.error:
            self.container_status_execution.current.bgcolor = AppThemeColors.RED
        else:
            self.container_status_execution.current.bgcolor = AppThemeColors.GREEN

    async def _on_click_task(self, e):
        await self.page.go_async(f'task/{self.task_id}')

    async def did_mount_async(self):
        self.task_load_log_flow = asyncio.create_task(self._load_task())

    async def will_unmount_async(self):
        self.task_load_log_flow.cancel()