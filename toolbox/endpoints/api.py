from toolbox import app
import json
from flask import request
from toolbox.widgets import WidgetDataAPI


@app.route("/tb-api", methods=["POST", "GET"])
def tb_api():
    request_prop: str = request.args["prop"]
    return_data: dict
    if request_prop == "cpu-percent":
        return_data = {"cpu-percent": WidgetDataAPI.get_cpu_usage()}
    elif request_prop == "memory-percent":
        return_data = {"memory-percent": WidgetDataAPI.get_memory_usage()}
    elif request_prop == "cpu-by-core-percent":
        return_data = {"cpu-by-core-percent": WidgetDataAPI.get_cpu_usage_by_core()}
    else:
        return_data = {"Property not found": "Property not found"}

    return json.dumps(return_data)
