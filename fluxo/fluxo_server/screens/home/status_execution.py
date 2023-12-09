import flet as ft
import asyncio
from datetime import timedelta
from fluxo.settings import AppThemeColors
from fluxo.fluxo_core.database.fluxo import Fluxo as ModelFluxo
from fluxo.fluxo_core.database.task import Task as ModelTask
from fluxo.uttils import convert_str_to_datetime


class StatusExecution(ft.UserControl):
    def __init__(self, fluxo: ModelFluxo, task: ModelTask):
        super().__init__()
        self.fluxo = fluxo
        self.task = task

    def build(self):
        self.container_execution = ft.Ref[ft.Container]()

        return ft.Container(
            ref=self.container_execution,
            height=23,
            width=23,
            border_radius=ft.border_radius.all(15),
            on_click=self.on_click_task,
        )
    
    async def on_click_task(self, e):
        await self.page.go_async(f'task/{self.task.id}')
    
    async def _load_status_execution(self):
        data_start_time = convert_str_to_datetime(self.task.start_time)
        data_execution_date = convert_str_to_datetime(self.task.execution_date)
        
        if self.task.execution_date is None:
            self.container_execution.current.bgcolor = AppThemeColors.BLUE
            self.container_execution.current.tooltip = self.task.execution_date

        elif self.task.execution_date and self.task.error:
            self.container_execution.current.bgcolor = AppThemeColors.RED
            self.container_execution.current.tooltip = self.task.execution_date

        elif self.fluxo.interval.get('minutes'):
            diference = data_execution_date - data_start_time
            if diference <= timedelta(minutes=self.fluxo.interval.get('minutes')):
                self.container_execution.current.bgcolor = AppThemeColors.GREEN
                self.container_execution.current.tooltip = self.task.execution_date

        elif self.fluxo.interval.get('hours'):
            diference = data_execution_date - data_start_time
            if diference <= timedelta(hours=self.fluxo.interval.get('hours')):
                self.container_execution.current.bgcolor = AppThemeColors.GREEN
                self.container_execution.current.tooltip = self.task.execution_date

        elif self.fluxo.interval.get('days'):
            diference = data_execution_date - data_start_time
            if diference <= timedelta(days=self.fluxo.interval.get('days')):
                self.container_execution.current.bgcolor = AppThemeColors.GREEN
                self.container_execution.current.tooltip = self.task.execution_date

        await self.update_async()

    async def did_mount_async(self):
        self.task_load_status_execution = asyncio.create_task(self._load_status_execution())

    async def will_unmount_async(self):
        self.task_load_status_execution.cancel()