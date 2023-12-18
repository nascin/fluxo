import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow


class StatusExecution(ft.UserControl):
    def __init__(self, log_flow: ModelLogExecutionFlow):
        super().__init__()
        self.log_flow = log_flow

    def build(self):
        self.container_execution = ft.Ref[ft.Container]()
        self.tooltip_execution = ft.Ref[ft.Tooltip]()
    
        return ft.Tooltip(
            ref=self.tooltip_execution,
            message='Synchronize',
            content=ft.Container(
                ref=self.container_execution,
                height=23,
                width=23,
                border_radius=ft.border_radius.all(15),
                on_click=self.on_click_log_flow,
            ),
            bgcolor=AppThemeColors.QUARTENARY
        )
    
    async def on_click_log_flow(self, e):
        await self.page.go_async(f'flow-execution/{self.log_flow.id}')
    
    async def _load_status_execution(self):        
        if self.log_flow.end_time is None:
            self.container_execution.current.bgcolor = AppThemeColors.BLUE
        elif self.log_flow.end_time and self.log_flow.ids_error_task:
            self.container_execution.current.bgcolor = AppThemeColors.RED
            self.tooltip_execution.current.message = self.log_flow.end_time
        else:
            self.container_execution.current.bgcolor = AppThemeColors.GREEN
            self.tooltip_execution.current.message = self.log_flow.end_time

        await self.update_async()

    async def did_mount_async(self):
        self.flow_load_status_execution = asyncio.create_task(self._load_status_execution())

    async def will_unmount_async(self):
        self.flow_load_status_execution.cancel()