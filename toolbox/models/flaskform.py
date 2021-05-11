from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FormField, Form
from wtforms.validators import required
from .util import display_settings_form_data, widget_list


class DisplaySettingsForm(FlaskForm):
    submit = SubmitField(render_kw={"class": "btn btn-primary"})


# for widget in widget_list():
#     setattr(DisplaySettingsForm, widget, StringField(render_kw={"class": "form-control"}))

widget_fields_list = display_settings_form_data()

for widget in widget_fields_list:
    for field in widget_fields_list[widget]:
        setattr(DisplaySettingsForm, field, widget_fields_list[widget][field])
