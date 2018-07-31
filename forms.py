from flask_security import RegisterForm, current_user
from flask_uploads import UploadSet, AUDIO
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import PasswordField, SubmitField, SelectField,\
    BooleanField, TextAreaField
from wtforms import widgets
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired, ValidationError, Length
from wtforms_alchemy import model_form_factory
from flask_babel import lazy_gettext
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from models import db, User, Album

BaseModelForm = model_form_factory(Form)

sounds = UploadSet('sounds', AUDIO)


class PasswordFieldNotHidden(StringField):
    """
    Original source: https://github.com/wtforms/wtforms/blob/2.0.2/wtforms/fields/simple.py#L35-L42  # noqa: E501

    A StringField, except renders an ``<input type="password">``.
    Also, whatever value is accepted by this field is not rendered back
    to the browser like normal fields.
    """
    widget = widgets.PasswordInput(hide_value=False)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session


class ExtendedRegisterForm(RegisterForm):
    name = StringField('Name', [DataRequired()])

    def validate_name(form, field):
        if len(field.data) <= 0:
            raise ValidationError(lazy_gettext("Username required"))

        u = User.query.filter(User.name == field.data).first()
        if u:
            raise ValidationError(lazy_gettext("Username already taken"))


class UserProfileForm(ModelForm):
    class Meta:
        model = User

    password = PasswordField(lazy_gettext('Password'), [Length(max=255)])
    name = StringField(lazy_gettext('Name'), [Length(max=255)])
    email = StringField(lazy_gettext('Email'), [Length(max=255)])
    firstname = StringField(lazy_gettext('Firstname'), [Length(max=32)])
    lastname = StringField(lazy_gettext('Lastname'), [Length(max=32)])
    timezone = SelectField(coerce=str, label=lazy_gettext('Timezone'),
                           default='UTC')
    locale = SelectField(lazy_gettext('Locale'), default="en",
                         choices=[['en', 'English'], ['fr', 'French']])
    submit = SubmitField(lazy_gettext('Update profile'))


class ConfigForm(Form):
    app_name = StringField(lazy_gettext('App Name'), [DataRequired(),
                                                      Length(max=255)])

    submit = SubmitField(lazy_gettext('Update config'))


def get_albums():
    return Album.query.filter(Album.user_id == current_user.id).all()


class SoundUploadForm(Form):
    title = StringField(lazy_gettext('Title'), [Length(max=255)])
    sound = FileField(lazy_gettext('File'), [FileRequired(),
                                             FileAllowed(AUDIO)])
    private = BooleanField(lazy_gettext('Private'), default=False)
    album = QuerySelectField(query_factory=get_albums,
                             allow_blank=True,
                             label=lazy_gettext('Album'),
                             get_label='title')

    def validate_private(form, field):
        if field.data is True and form.album.data.private is False:
            raise ValidationError(
                lazy_gettext("Cannot put private sound in public album"))

    submit = SubmitField(lazy_gettext('Upload'))


class SoundEditForm(Form):
    title = StringField(lazy_gettext('Title'), [Length(max=255)])
    private = BooleanField(lazy_gettext('Private'), default=False)
    description = TextAreaField(lazy_gettext('Description'))
    album = QuerySelectField(query_factory=get_albums,
                             allow_blank=True,
                             label=lazy_gettext('Album'),
                             get_label='title')

    def validate_private(form, field):
        if field.data is True and form.album.data.private is False:
            raise ValidationError(
                lazy_gettext("Cannot put private sound in public album"))

    submit = SubmitField(lazy_gettext('Edit sound'))


class AlbumForm(Form):
    title = StringField(lazy_gettext('Title'), [Length(max=255),
                                                DataRequired()])
    description = TextAreaField(lazy_gettext('Description'))
    private = BooleanField(lazy_gettext('Private'), default=False)

    submit = SubmitField(lazy_gettext('Save'))