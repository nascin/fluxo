import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo.init_schedule import flows_executor
from fluxo.fluxo_core.database.flow import ModelFlow
from fluxo.fluxo_core.database.log_execution_flow import ModelLogExecutionFlow
from fluxo.fluxo_server.screens.home.status_execution import StatusExecution


class Flow(ft.UserControl):
    def __init__(self, flow: ModelFlow):
        super().__init__()
        self.flow = flow

    def build(self):
        self.row_flow = ft.Ref[ft.Row]()
        self.text_name = ft.Ref[ft.Text]()
        self.text_interval = ft.Ref[ft.Text]()

        self.container_status = ft.Ref[ft.Container]()
        self.row_executions = ft.Ref[ft.Row]()
        self.text_status = ft.Ref[ft.Text]()

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
                    ft.Container(
                        ref=self.container_status,
                        content=ft.Text(
                            ref=self.text_status,
                            weight=ft.FontWeight.BOLD,
                            color=AppThemeColors.WHITE,
                            size=10,
                        ), # Text
                        border_radius=ft.border_radius.all(5),
                        padding=ft.padding.all(5)
                    ), # Container
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

        # Status
        if self.flow.running:
            self.text_status.current.value = 'Live'
            self.container_status.current.bgcolor = AppThemeColors.GREEN
        else:
            self.text_status.current.value = 'Off'
            self.container_status.current.bgcolor = AppThemeColors.RED

        # iconbutton_start_stop_flow
        if self.flow.running:
            self.iconbutton_start_stop_flow.current.icon = ft.icons.STOP_ROUNDED
        else:
            self.iconbutton_start_stop_flow.current.icon = ft.icons.PLAY_ARROW_ROUNDED

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

    async def did_mount_async(self):
        self.task_load_attributes_flow = asyncio.create_task(self._load_attributes_flow())
        self.task_load_status_executions = asyncio.create_task(self._load_status_executions())

    async def will_unmount_async(self):
        self.task_load_attributes_flow.cancel()
        self.task_load_status_executions.cancel()