import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.fluxo_core.flows_executor import FlowsExecutor
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow
from fluxo.fluxo_server.screens.home.status_execution import StatusExecution


class Flow(ft.UserControl):
    def __init__(self, flow: ModelFlow, flows_executor: FlowsExecutor):
        super().__init__()
        self.flow = flow
        self.flows_executor = flows_executor

    def build(self):
        self.row_flow = ft.Ref[ft.Row]()
        self.text_name = ft.Ref[ft.Text]()
        self.text_interval = ft.Ref[ft.Text]()

        self.row_executions = ft.Ref[ft.Row]()
        self.switch_running = ft.Ref[ft.Switch]()

        return ft.Container(
            content=ft.Row(
                ref=self.row_flow,
                controls=[
                    ft.Container(
                        content=ft.Stack(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        ref=self.text_name,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.BLACK,
                                        size=13,
                                        width=200
                                    ), # Text
                                    left=0,
                                    top=12
                                ), # Container
                                ft.Container(
                                    content=ft.Text(
                                        ref=self.text_interval,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.BLACK_SECONDARY,
                                        size=10,
                                        width=200
                                    ), # Text
                                    left=150,
                                    top=0,
                                ), # Container
                            ], # controls
                        ), # Stack
                        width=290,
                        height=45,
                    ), # Container
                    ft.Container(
                        content=ft.Row(
                            ref=self.row_executions,
                            controls=[

                            ], # controls
                            width=320,
                            height=50,
                            scroll=ft.ScrollMode.AUTO,
                            auto_scroll=True
                        ), # Row
                    ), # Container
                    ft.Container(width=50),
                    ft.Switch(
                        ref=self.switch_running,
                        label_position=ft.LabelPosition.LEFT,
                        on_change=self.on_change_switch_running
                    )
                ], # controls
                #scroll=ft.ScrollMode.AUTO
            ), # Row
            bgcolor=AppThemeColors.GREY,
            border_radius=ft.border_radius.all(10),
            width=900,
            height=60,
            padding=ft.padding.only(left=15, top=0, right=15, bottom=0)
        ) # Container
    
    async def _load_attributes_flow(self):
        # Name
        self.text_name.current.value = self.flow.name

        # Interval
        interval = self.flow.interval
        if interval.get('minutes'):
            self.text_interval.current.value = f'every {interval.get("minutes")} min(s) at {interval.get("at")[1:]}s'
        elif interval.get('hours'):
            self.text_interval.current.value = f'every {interval.get("hours")} hour(s) at {interval.get("at")[1:]}m'
        elif interval.get('days'):
            self.text_interval.current.value = f'every {interval.get("days")} day(s) at {interval.get("at")}'
        
        # switch_start_stop_flow
        if self.flow.running:
            self.switch_running.current.value = True
            self.switch_running.current.label = 'ON'
        else:
            self.switch_running.current.value = False
            self.switch_running.current.label = 'OFF'
        await self.update_async()

    async def _load_status_executions(self):
        log_flows = ModelLogExecutionFlow.get_all_by_id_flow(self.flow.id)

        if log_flows:
            # Organize task list by date
            sorted_log_flows = sorted(log_flows, key=lambda x: x.date_of_creation, reverse=False)

            for log_flow in sorted_log_flows:
                self.row_executions.current.controls.append(StatusExecution(log_flow))
                        
            if len(log_flows) < 10:
                n = 10 - len(log_flows)
                for _ in range(n):
                    self.row_executions.current.controls.insert(
                        0,
                        ft.Container(
                            bgcolor=AppThemeColors.WHITE,
                            height=23,
                            width=23,
                            border_radius=ft.border_radius.all(15),
                            tooltip=''
                        ), # Container
                    )
        else:
            for _ in range(10):
                self.row_executions.current.controls.insert(
                    0,
                    ft.Container(
                        bgcolor=AppThemeColors.WHITE,
                        height=23,
                        width=23,
                        border_radius=ft.border_radius.all(15),
                        tooltip=''
                    ), # Container
                )
        await self.update_async()

    async def on_change_switch_running(self, e):
        flow = ModelFlow.get_by_id(self.flow.id)

        if flow.running: # Stop Flow
            self.flows_executor.stop_flow_execution([flow])
            e.control.value = False
            e.control.label = 'OFF'
        else: # Start Flow
            self.flows_executor.execute_parallel_flows([flow])
            e.control.value = True
            e.control.label = 'ON'
        await self.update_async()

    async def did_mount_async(self):
        self.task_load_attributes_flow = asyncio.create_task(self._load_attributes_flow())
        self.task_load_status_executions = asyncio.create_task(self._load_status_executions())

    async def will_unmount_async(self):
        self.task_load_attributes_flow.cancel()
        self.task_load_status_executions.cancel()