from .mongodb import DashboardProfiles
from toolbox.hardware import HardwareInfo
from typing import Union
from collections import OrderedDict
from wtforms import BooleanField


def display_settings_form_data() -> dict:
    profile: DashboardProfiles = DashboardProfiles.objects(profile_name="Default").only("widgets").first()
    return_list: dict = {}
    display_fields: list = []
    all_fields: Union[list, OrderedDict] = []

    for widget in profile.widgets:
        display_fields = getattr(profile.widgets, widget,).display_fields
        all_fields = getattr(HardwareInfo(), f"get_{widget}")()

        if "partitions" in all_fields.keys():
            all_fields = list(all_fields["partitions"][0].keys())
        else:
            all_fields = list(all_fields.keys())
        widget_dict = {}

        for field in all_fields:
            if field in display_fields:
                # widget_dict[field] = True
                widget_dict[field] = BooleanField(default="checked", render_kw={"data-widget": widget})
            else:
                # widget_dict[field] = False
                widget_dict[field] = BooleanField(render_kw={"data-widget": widget})

        return_list[widget] = widget_dict

    return return_list


def widget_list() -> list:
    profile: DashboardProfiles = DashboardProfiles.objects(profile_name="Default").only("widgets").first()
    widgets: list = [key.lower() for key in profile.widgets]
    return widgets
