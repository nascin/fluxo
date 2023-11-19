import flet as ft
import asyncio
from fluxo.settings import AppThemeColors
from fluxo_core.database.fluxo import Fluxo as ModelFluxo


class Fluxo(ft.UserControl):
    def __init__(self, fluxo: ModelFluxo):
        super().__init__()
        self.fluxo = fluxo

    def build(self):
        self.text_name = ft.Ref[ft.Text]()
        self.text_interval = ft.Ref[ft.Text]()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Stack(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        ref=self.text_name,
                                        weight=ft.FontWeight.BOLD,
                                        color=AppThemeColors.BLACK,
                                        size=14,
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
                                    left=100,
                                    top=0,
                                ), # Container
                            ], # controls
                        ), # Stack
                        width=800,
                        height=45,
                    ), # Container
                ], # controls
            ), # Row
            bgcolor=AppThemeColors.GREY,
            border_radius=ft.border_radius.all(10),
            width=800,
            height=45,
            padding=ft.padding.only(left=10, top=0, right=10, bottom=0)
        ) # Container
    
    async def _load_attributes_fluxo(self):
        self.text_name.current.value = self.fluxo.name

        interval = self.fluxo.interval
        if interval.get('minutes'):
            self.text_interval.current.value = f'every {interval.get("minutes")} min(s) at {interval.get("at")[1:]}s'
        elif interval.get('hours'):
            self.text_interval.current.value = f'every {interval.get("hours")} hour(s) at {interval.get("at")[1:]}m'
        elif interval.get('days'):
            self.text_interval.current.value = f'every {interval.get("days")} day(s) at {interval.get("at")}'
        await self.update_async()

    async def did_mount_async(self):
        self.task_load_attributes_fluxo = asyncio.create_task(self._load_attributes_fluxo())

    async def will_unmount_async(self):
        self.task_load_attributes_fluxo.cancel()