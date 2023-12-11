import flet as ft
import flet_fastapi
import uvicorn
from fluxo.settings import FONTS, AppThemeColors, AppSettings
from fluxo.fluxo_server.screens.home.home import view_home
from fluxo.fluxo_server.screens.task.task import view_task


class App:
    def __init__(self, page: ft.Page) -> None:
        self.page = page

    async def init(self):
        self.page.theme = ft.Theme(
            color_scheme_seed=AppThemeColors.PRIMARY,
        )
        self.page.fonts = FONTS
        self.page.title = 'Fluxo'

        async def route_change(route):
            #self.page.views.clear()
            t_route = ft.TemplateRoute(self.page.route)

            if t_route.match('/'):
                self.page.views.append(view_home())

            elif t_route.match('task/:id'):
                self.page.views.append(view_task(t_route.id))

            await self.page.update_async()

        async def view_pop(view):
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

        self.page.on_route_change = route_change
        self.page.on_view_pop = view_pop
        await self.page.go_async(self.page.route)


async def main(page: ft.Page):
    await App(page).init()

if __name__ == '__main__':
    app = flet_fastapi.app(
        session_handler=main,
        assets_dir=AppSettings.ASSETS_DIR,
        app_name='Fluxo',
        app_short_name='Fluxo',
        app_description='Simple data flow with execution in separate threads and easy scheduling configuration.'
    )
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=AppSettings.PORT
    )
