from collections import OrderedDict
from toolbox.hardware import HardwareInfo
from toolbox.models import DashboardProfiles, widget_list
from jinja2 import Markup
from typing import Union, Final
from ._html import table_template, widget_card_template, table_col_head_template, table_row_head_template,\
    table_data_template, table_row_template


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

    def get_widget(self, widget_name: str, profile: str = "Default") -> OrderedDict:
        if widget_name.lower() not in self.widget_list:
            raise Exception(f"invalid widget for get_widget(): '{widget_name}'")
        widget_data: OrderedDict = getattr(self, f"get_{widget_name}")()
        profile: DashboardProfiles = DashboardProfiles.objects(profile_name=profile).only(f"widgets.{widget_name}").first()
        widget_data["display_fields"] = getattr(profile.widgets, widget_name).display_fields
        widget_data["display_widget"] = getattr(profile.widgets, widget_name).display_widget
        widget_data["widget_type"] = getattr(profile.widgets, widget_name).widget_type
        return widget_data

    def get_widget_html(self):
        table_body: Union[Markup, list] = list()
        table_head = self._table_row % (self._table_col_head % "#")
        for widget in self.widget_list:
            table_body.append(self._table_row % Markup(f"<td>{widget.title()}</td>"))

        table_body = Markup(''.join(table_body))
        spec_table = Markup(self._table % {"head": table_head, "body": table_body})
        widget: Markup = self._widget_card % {"card_title": "Test Card", "card_content": spec_table}

        return self._memory_widget()

    def _memory_widget(self):
        memory_specs = self.get_memory()
        table_data = list()
        table_header = self._table_row % (self._table_col_head % '' * 2)
        for data in memory_specs:
            row_content = self._table_row_head % data.title() + self._table_data % memory_specs[data]
            table_data.append(self._table_row % row_content)
        table_data = Markup("\n".join(table_data))

        table = self._table % {"head": table_header, "body": table_data}
        widget = self._widget_card % {"card_title": "Memory", "card_content": table}

        print(widget)
        return widget
