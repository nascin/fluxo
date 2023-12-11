import flet as ft
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
    ft.app(target=main, 
           view=ft.AppView.WEB_BROWSER,
           port=AppSettings.PORT,
           assets_dir=AppSettings.ASSETS_DIR)