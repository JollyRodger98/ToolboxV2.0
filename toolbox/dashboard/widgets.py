from collections import OrderedDict
from toolbox.hardware import HardwareInfo
from toolbox.models import DashboardProfiles, widget_list


class HardwareWidget(HardwareInfo):

    def __init__(self):
        super().__init__()
        self.widget_list = widget_list()

    def get_widget(self, widget_name: str, profile: str = "Default") -> OrderedDict:
        if widget_name.lower() not in self.widget_list:
            raise Exception(f"invalid widget for get_widget(): '{widget_name}'")
        widget_data: OrderedDict = getattr(self, f"get_{widget_name}")()
        profile: DashboardProfiles = DashboardProfiles.objects(profile_name=profile).only(f"widgets.{widget_name}").first()
        widget_data["display_fields"] = getattr(profile.widgets, widget_name).display_fields
        widget_data["display_widget"] = getattr(profile.widgets, widget_name).display_widget
        widget_data["widget_type"] = getattr(profile.widgets, widget_name).widget_type
        return widget_data
