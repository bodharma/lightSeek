import pprint
from requests_html import HTMLSession
from aws_lambda_powertools import Logger

logger = Logger()


class LOE:
    def __init__(self):
        self.session = HTMLSession()
        self.url = "https://poweroff.loe.lviv.ua/"
        logger.info("Starting session")
        self.r = self.session.get(self.url)
        self._get_csrf_token()

    def _get_csrf_token(self):
        logger.info("Getting csrf token")
        self.csrf = self.r.html.find('[name="csrfmiddlewaretoken"]', first=True).attrs['value']

    def _get_list_of_streets(self):
        logger.info("Getting list of streets")
        resp = self.session.get('https://poweroff.loe.lviv.ua/search_off?',
                                params={
                                    'csrfmiddlewaretoken': self.csrf,
                                    'city': '',
                                    'street': '',
                                    'otg': 'Львівська',
                                    'q': 'Пошук'
                                })
        return resp

    def _get_street_data(self, list_of_streets, street="Лемківська"):
        logger.info(f"Getting street data for {street}")
        otg_result_line = list_of_streets.html.xpath(f'//td[contains(text(), "{street}")]/parent::*', first=True)
        otg_result_data = otg_result_line.find('td')
        column_keys = ['otg', 'city', 'street', 'house#', 'power_off_type', 'power_off_reason', 'power_off_time',
                       'power_on_time']
        colum_values = [td.text for td in otg_result_data]
        otg_result = dict(zip(column_keys, colum_values))
        logger.info(f"Got street data for {street}: {otg_result}")
        return otg_result

    def light_status(self):
        list_of_streets = self._get_list_of_streets()
        light_status = self._get_street_data(list_of_streets)
        return light_status

    def pretty_message(self):
        light_status = self.light_status()
        messsage = f"""
        💡Світло на вулиці💡 \n
        🏠{light_status['street']}-{light_status['house#']}\n
        🖤вимкнено о {light_status['power_off_time']}🖤\n 
        ❤️‍🔥очікується включення о {light_status['power_on_time']}❤️‍🔥\n
        ⁉️Причина: {light_status['power_off_reason']}⁉️\n
        ⚜️Тип вимикання: {light_status['power_off_type']}⚜"""
        pprint.pprint(messsage)
        return messsage


def message(context):
    loe = LOE()
    light_status = loe.pretty_message()
    context.message.reply_text(text=light_status)
    logger.info(f"Sent message: {light_status}")


if __name__ == "__main__":
    loe = LOE()
    loe.pretty_message()

