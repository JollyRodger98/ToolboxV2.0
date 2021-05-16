from collections import OrderedDict
from typing import Union, Final

from jinja2 import Markup

from toolbox.hardware import HardwareInfo
from toolbox.models import DashboardProfiles, widget_list
from ._html import table_template, widget_card_template, table_col_head_template, table_row_head_template, \
    table_data_template, table_row_template, alert_danger_template, table_data_percentage_template


def _get_profile(profile: str, widget: str) -> DashboardProfiles:
    """Query profile settings for widget.

    :param profile: Dashboard profile name
    :param widget: Name of widget profile is queried for.
    :return: MongoEngine document with widget settings for profile.
    :rtype: DashboardProfiles
    """
    db_return = DashboardProfiles.objects(profile_name=profile).only(f"widgets.{widget}").first()
    if db_return is None:
        return DashboardProfiles.objects(profile_name="Default").only(f"widgets.{widget}").first()
    else:
        return db_return


def _widget_visible(display_setting: bool) -> str:
    """Get required CSS class for widget display settings.

    :param display_setting:
    :return: CSS visibility class
    :rtype: str
    """
    if not display_setting:
        return "visually-hidden"
    elif display_setting:
        return ""


def _percentage_bar_class(percentage: Union[int, float]) -> str:
    """Get bar color based on percentage value.

    :param percentage: Percentage bar value
    :return: CSS color class
    :rtype: str
    """
    minor_threshold = 50
    major_threshold = 75
    if minor_threshold > percentage > 0:
        return "bg-success"
    elif major_threshold > percentage > minor_threshold:
        return "bg-warning"
    elif 100 > percentage > major_threshold:
        return "bg-danger"


def _col_visible(field_name: str, display_settings: list):
    """Return required CSS class based on profile settings.

    :param field_name: Name of fields to check visibility
    :param display_settings: Setting from user profile.
    :return: CSS class for column visibility
    :rtype: str
    """
    if field_name.lower() not in display_settings:
        return "visually-hidden"
    else:
        return ""


class HardwareWidget(HardwareInfo):

    def __init__(self):
        """Generate hardware specification widgets.

        Uses HardwareInfo class to query local hardware specs. Generates Markup string with widget and spec table.
        """
        super().__init__()
        self.widget_list: list = widget_list()
        self._table: Final[Markup] = table_template
        self._widget_card: Final[Markup] = widget_card_template
        self._table_row_head: Final[Markup] = table_row_head_template
        self._table_col_head: Final[Markup] = table_col_head_template
        self._table_data: Final[Markup] = table_data_template
        self._table_row: Final[Markup] = table_row_template
        self._alert: Final[Markup] = alert_danger_template
        self._table_data_percentage: Final[Markup] = table_data_percentage_template
        self._std_table_header: Final[Markup] = \
            self._table_row % {"row_class": "",
                               "row_content": (self._table_col_head % {"head_class": "", "head_content": ""} * 2)}

    def get_widget(self, widget_name: str, profile: str = "Default") -> Markup:
        """Get widget HTML Markup string with name and profile.

        :param widget_name: Name of the widget.
        :param profile: Name of the dashboard profile.
        :return: Markup string with entire widget card
        :rtype: Markup
        """
        if widget_name.lower() == "memory":
            widget = self._memory_widget(profile)
        elif widget_name.lower() == "system":
            widget = self._system_widget(profile)
        elif widget_name.lower() == "cpu":
            widget = self._cpu_widget(profile)
        elif widget_name.lower() == "partitions":
            widget = self._partitions_widget(profile)
        else:
            li_widget_list = [f"<li>{i}</li>" for i in self.widget_list]
            ul_widget_list = Markup("<ul>%s</ul>") % Markup(''.join(li_widget_list))
            alert_content = Markup(f"<p>Available widgets are:<p>\n{ul_widget_list}")
            card_content = self._alert % {"alert_title": f"Widget '{widget_name}' not found.",
                                          "alert_body": alert_content}
            widget = self._widget_card % {"card_title": "ERROR", "card_content": card_content, "card_classes": ""}

        return widget

    def _partitions_widget(self, profile: str) -> Markup:
        table_data: list = list()
        # noinspection PyPep8Naming
        WIDGET = "partitions"
        user_profile = _get_profile(profile, WIDGET)
        card_classes = [_widget_visible(user_profile.widgets.partitions.display_widget)]
        partition_data_list = self.get_partitions()["data_list"]

        for partition in partition_data_list:
            row_content = []
            for data in partition.items():
                if data[0].lower() == "used space percent":
                    percent = float(data[1].replace("%", ""))
                    percentage_class = _percentage_bar_class(percent)
                    row_content.append(self._table_data_percentage % {"percentage": percent,
                                                                      "bar_class": percentage_class})
                else:
                    col_visibility = _col_visible(data[0], user_profile.widgets.partitions.display_fields)
                    row_content.append(self._table_data % {"cell_class": col_visibility, "cell_content": data[1]})
            table_data.append(
                self._table_row % {"row_class": "text-nowrap", "row_content": Markup("".join(row_content))}
            )
        table_header = []
        for head_name in partition_data_list[0].items():
            col_visibility = _col_visible(head_name[0], user_profile.widgets.partitions.display_fields)
            table_header.append(self._table_col_head % {"head_class": col_visibility,
                                                        "head_content": head_name[0].title()})

        table_header = self._table_row % {"row_class": "text-nowrap", "row_content": Markup("".join(table_header))}

        return self._generate_std_widget(WIDGET.title(), table_data, card_classes, table_header)

    def _memory_widget(self, profile: str) -> Markup:
        """Generate memory widget Markup string from hardware data.

        :return: HTML Markup string with widget
        :rtype: Markup
        """
        table_data: list = list()
        # noinspection PyPep8Naming
        WIDGET = "memory"
        user_profile = _get_profile(profile, WIDGET)
        card_classes = [_widget_visible(user_profile.widgets.memory.display_widget)]

        for data in self.get_memory().items():
            if data[0].lower() == "percent":
                row_content = self._generate_percentage_row(data[0].title(), data[1])
            else:
                row_content = self._table_row_head % {"head_class": "", "head_content": data[0].title()} + \
                              self._table_data % {"cell_class": "", "cell_content": data[1]}

            table_data.append(
                self._generate_table_row(data[0], user_profile.widgets.memory.display_fields, row_content))

        return self._generate_std_widget(WIDGET.title(), table_data, card_classes)

    def _system_widget(self, profile: str) -> Markup:
        table_data: list = list()
        # noinspection PyPep8Naming
        WIDGET = "system"
        user_profile = _get_profile(profile, WIDGET)
        card_classes = [_widget_visible(user_profile.widgets.system.display_widget)]

        for data in self.get_system().items():
            row_content = self._table_row_head % {"head_class": "", "head_content": data[0].title()} + \
                          self._table_data % {"cell_class": "", "cell_content": data[1]}
            table_data.append(
                self._generate_table_row(data[0], user_profile.widgets.system.display_fields, row_content))

        return self._generate_std_widget(WIDGET.title(), table_data, card_classes)

    def _cpu_widget(self, profile: str) -> Markup:
        table_data: list = list()
        # noinspection PyPep8Naming
        WIDGET = "cpu"
        user_profile = _get_profile(profile, WIDGET)
        card_classes = [_widget_visible(user_profile.widgets.cpu.display_widget)]

        for data in self.get_cpu().items():
            field_name = data[0].title().replace("Cpu", "CPU") if "cpu" in data[0].lower() else data[0].title()
            alignment = ""

            if data[0].lower() == "cpu usage by core":
                cores = []
                for index, field in enumerate(data[1]):
                    percentage = int(float(data[1][field].replace('%', '')))
                    cores.append(f"<span class=\"text-nowrap\">"
                                 f"<strong>{field + 1:02d}</strong>:{percentage:02d}%;"
                                 f"</span>")
                    if (index + 1) % 4 == 0:
                        cores.append(" ")

                row_data = Markup("".join(cores))
                alignment = "align-middle"
                row_content = self._table_row_head % {"head_class": "", "head_content": field_name} + \
                    self._table_data % {"cell_class": "font-TBMonospace h6", "cell_content": row_data}
            elif data[0].lower() == "cpu usage total":
                row_content = self._generate_percentage_row(field_name, data[1])
            else:
                row_content = self._table_row_head % {"head_class": "", "head_content": data[0].title()} + \
                              self._table_data % {"cell_class": "", "cell_content": data[1]}

            table_data.append(
                self._generate_table_row(data[0], user_profile.widgets.cpu.display_fields, row_content, [alignment]))

        return self._generate_std_widget(WIDGET.upper(), table_data, card_classes)

    def _generate_percentage_row(self, key: str, value: str) -> Markup:
        """Generate table row content with percentage-bar

        :param key: Field name
        :param value: Field value (percentage)
        :return: Table row content (th & td)
        """
        percentage = float(value.replace('%', ''))
        percentage_class = _percentage_bar_class(percentage)
        row_head = self._table_row_head % {"head_class": "", "head_content": key}
        row_data = self._table_data_percentage % {"percentage": percentage, "bar_class": percentage_class}
        return row_head + row_data

    def _generate_std_widget(self, card_title: str, table_data: list, card_classes: list,
                             table_head: Markup = None) -> Markup:
        """Takes Markup strings and generates a full widget.

        Table data and card classes are joined to string.

        :param card_title: Title to be displayed at the top of the card.
        :param table_data: Content of specs table as list.
        :param card_classes: Classes to be applied to the entire card.
        :param table_head: Markup string of table header, optional
        :return: Widget as Markup string
        """
        if table_head is None:
            table_head = self._std_table_header

        card_classes = " ".join(card_classes)
        table_data = Markup("\n".join(table_data))
        table = self._table % {"head": table_head, "body": table_data}
        return self._widget_card % {"card_title": card_title, "card_content": table, "card_classes": card_classes}

    def _generate_table_row(self, field_name: str, display_settings: list,
                            content: Markup, classes: list = None) -> Markup:
        """Used in loop to generate a table row

        :param field_name: Name of the current table row data.
        :param display_settings: Profile field display settings.
        :param content: Row content.
        :param classes: Classes to be applied to table row.
        :return: Markup table row string.
        :rtype: Markup
        """
        if classes is None:
            classes = []

        if field_name.lower() not in display_settings:
            classes.append("visually-hidden")

        row_classes = " ".join(classes)
        return self._table_row % {"row_class": row_classes, "row_content": content}
