from toolbox import app
from toolbox.widgets import HardwareWidget
from toolbox.models import DisplaySettingsForm, widget_list
from flask import render_template, url_for, redirect


@app.route('/')
def root():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template('pages/home.html', hardware=HardwareWidget(), form=DisplaySettingsForm())
