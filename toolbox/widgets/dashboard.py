from collections import OrderedDict
from toolbox.hardware import HardwareInfo
from toolbox.models import DashboardProfiles, widget_list
from jinja2 import Markup
from typing import Union, Final
from ._html import table_template, widget_card_template, table_col_head_template, table_row_head_template,\
    table_data_template, table_row_template, alert_danger_template


class HardwareWidget(HardwareInfo):

    def __init__(self):
        super().__init__()
        self.widget_list: list = widget_list()
        self._table: Final[Markup] = table_template
        self._widget_card: Final[Markup] = widget_card_template
        self._table_row_head: Final[Markup] = table_row_head_template
        self._table_col_head: Final[Markup] = table_col_head_template
        self._table_data: Final[Markup] = table_data_template
        self._table_row: Final[Markup] = table_row_template
        self._alert: Final[Markup] = alert_danger_template

    def get_widget(self, widget_name: str, profile: str = "Default") -> OrderedDict:
        if widget_name.lower() not in self.widget_list:
            raise Exception(f"invalid widget for get_widget(): '{widget_name}'")
        widget_data: OrderedDict = getattr(self, f"get_{widget_name}")()
        profile: DashboardProfiles = DashboardProfiles.objects(profile_name=profile).only(f"widgets.{widget_name}").first()
        widget_data["display_fields"] = getattr(profile.widgets, widget_name).display_fields
        widget_data["display_widget"] = getattr(profile.widgets, widget_name).display_widget
        widget_data["widget_type"] = getattr(profile.widgets, widget_name).widget_type
        return widget_data

    def get_widget_html(self, widget_name: str, profile: str = "Default") -> Markup:
        widget: Markup

        if widget_name.lower() == "memory":
            widget = self._memory_widget()
        else:
            li_widget_list = [f"<li>{i}</li>" for i in self.widget_list]
            ul_widget_list = Markup("<ul>%s</ul>") % Markup(''.join(li_widget_list))
            alert_content = Markup(f"<p>Available widgets are:<p>\n{ul_widget_list}")
            card_content = self._alert % {"alert_title": f"Widget '{widget_name}' not found.",
                                          "alert_body": alert_content}
            widget = self._widget_card % {"card_title": "ERROR", "card_content": card_content}

        return widget

    def _memory_widget(self) -> Markup:
        """Generate memory widget and return HTML Markup string.

        :return: HTML Markup string with widget
        :rtype: Markup
        """
        table_data: list = list()
        table_header = self._table_row % (self._table_col_head % '' * 2)

        for data in self.get_memory().items():
            row_content = self._table_row_head % data[0].title() + self._table_data % data[1]
            table_data.append(self._table_row % row_content)
        table_data = Markup("\n".join(table_data))

        table = self._table % {"head": table_header, "body": table_data}
        widget = self._widget_card % {"card_title": "Memory", "card_content": table}

        return widget
