from flask.ext.wtf import Form, SelectField, Required, HiddenField
from flask.ext.wtf.html5 import EmailField
import pytz

class RegistrationForm(Form):
    email = EmailField(validators=[Required()])
    timezone = SelectField(
        choices=[(tz, tz) for tz in pytz.common_timezones],
        validators=[Required()]
    )


class EmailValidationForm(Form):
    token = HiddenField(validators=[Required()])
