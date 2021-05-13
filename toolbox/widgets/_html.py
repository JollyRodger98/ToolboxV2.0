from jinja2 import Markup

table_template: Markup = Markup(
    f"<div class=\"table-responsive\">\n"
    f"    <table class=\"table table-sm\">\n"
    f"        <thead>\n"
    f"            %(head)s\n"
    f"        </thead>\n"
    f"        <tbody>\n"
    f"            %(body)s\n"
    f"        </tbody>\n"
    f"    </table>\n"
    f"</div>\n")

table_row_template: Markup = Markup("<tr class=\"%(row_class)s\">%(row_content)s</tr>")

table_col_head_template: Markup = Markup("<th scope=\"col\">%s</th>")
table_row_head_template: Markup = Markup("<th scope=\"row\">%s</th>")
table_data_template: Markup = Markup("<td>%s</td>")
widget_card_template: Markup = Markup(
    f"<div class=\"col\">\n"
    f"    <div class=\"card user-select-none h-100\">\n"
    f"        <div class=\"card-body\">\n"
    f"            <div class=\"card-subtitle text-muted mb-2\">%(card_title)s</div>\n"
    f"            <div class=\"card-text\">\n"
    f"                %(card_content)s\n"
    f"            </div>\n"
    f"        </div>\n"
    f"    </div>\n"
    f"</div>\n")
alert_danger_template = Markup(
    f"<div class=\"alert alert-danger\" role=\"alert\">\n"
    f"    <h4 class=\"alert-heading\">%(alert_title)s</h4>\n"
    f"    %(alert_body)s\n"
    f"</div>\n")
