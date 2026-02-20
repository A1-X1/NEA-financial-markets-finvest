from nicegui import ui
from modules.globalSettings import globalSettings
import yfinance as yf
from datetime import datetime

class NewsPage:
    def __init__(self):
        self.__settings = globalSettings
        self.__news_container = None

    def __fetch_news(self) -> list[dict]:
        # fetch recent financial headlines via yfinance — no api key needed
        try:
            ticker = yf.Ticker('^GSPC')
            items = ticker.news or []
            results = []
            for item in items:
                # get the publish time (unix timestamp) and headline
                pub_time = item.get('providerPublishTime') or item.get('publishedAt')
                title = (
                    item.get('title')
                    or item.get('content', {}).get('title', '')
                )
                if pub_time and title:
                    dt = datetime.fromtimestamp(pub_time)
                    results.append({'time': dt.strftime('%H:%M'), 'headline': title})
            return results
        except Exception as e:
            print(f'News fetch error: {e}')
            return []

    def __render_news_rows(self):
        # clear and re-render the news list
        self.__news_container.clear()
        news = self.__fetch_news()

        with self.__news_container:
            theme = self.__settings.theme

            if not news:
                ui.label('No news available at the moment.') \
                    .classes('italic p-4').style(f'color: {theme.text_secondary}')
                return

            for i, item in enumerate(news):
                # each row: time column + headline column, with a bottom border divider
                border = f'border-color: {theme.text_secondary}22;' if i < len(news) - 1 else 'border: none;'
                with ui.row().classes('w-full items-start py-3 border-b gap-4').style(border):
                    ui.label(item['time']) \
                        .classes('w-14 shrink-0 font-mono text-sm') \
                        .style(f'color: {theme.text_secondary}')
                    ui.label(item['headline']) \
                        .classes('flex-grow text-sm') \
                        .style(f'color: {theme.text_primary}')

    def render(self):
        colours = self.__settings.theme

        with ui.element('div').classes('w-full flex flex-col p-8 gap-6'):
            ui.label('News').style(f'color: {colours.text_primary}; font-size: 200%; font-weight: bold')

            # card container that matches the mockup
            with ui.card().classes('w-full max-w-5xl p-0 overflow-hidden shadow-sm border border-gray-100/10') \
                    .style(f'background-color: {colours.surface}'):
                
                # header row
                with ui.row().classes('w-full px-6 py-3 border-b gap-4') \
                        .style(f'border-color: {colours.text_secondary}22'):
                    ui.label('Time').classes('w-14 shrink-0 font-semibold text-sm') \
                        .style(f'color: {colours.text_secondary}')
                    ui.label('News').classes('flex-grow font-semibold text-sm') \
                        .style(f'color: {colours.text_secondary}')

                # scrollable news body
                with ui.scroll_area().classes('w-full').style('max-height: 500px;'):
                    self.__news_container = ui.element('div').classes('w-full px-6 pb-4')
                    with self.__news_container:
                        # placeholder while loading
                        ui.spinner(size='md', color=colours.accent).classes('m-4')

            # fetch news after the UI is rendered (avoids blocking the page load)
            ui.timer(0.1, self.__render_news_rows, once=True)