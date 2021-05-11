from toolbox import app
from toolbox.dashboard import HardwareWidget
from toolbox.models import DisplaySettingsForm
from flask import render_template, url_for, redirect


@app.route('/')
def root():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    # print(DisplaySettingsForm())
    # for field in iter(DisplaySettingsForm()):
    #     print(field)
    return render_template('pages/home.html', hardware=HardwareWidget(), form=DisplaySettingsForm())
