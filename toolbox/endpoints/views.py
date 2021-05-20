from toolbox import app
from toolbox.widgets import HardwareWidget, get_default_os_profile
from toolbox.models import DisplaySettingsForm
from flask import render_template, url_for, redirect


@app.route('/')
def root():
    return redirect(url_for('home'))


@app.route("/home", methods=["GET"])
def home():
    i = HardwareWidget().get_network()
    print(f"\nFunction Return:")
    print(i)
    return render_template('pages/home.html', hardware=HardwareWidget(),
                           form=DisplaySettingsForm(), std_profile=get_default_os_profile())
