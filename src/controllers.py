from flask import render_template, redirect, url_for, request
from flask_wtf import Form
from flask_login import LoginManager, login_required, login_user, logout_user
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, length
from src.models import User
from src import app

'''
Setup
'''

# this class managers user login and session
login_manager = LoginManager(app)
# set the portal page as default login go-to page
login_manager.login_view = '/portal'


@login_manager.user_loader
def load_user(user_id):
    """
    User by the login manager
    Load the user object from user id stored in session
    """
    return User.get_by_id(user_id)


'''
Routes
'''


@app.route('/', methods=['GET', 'POST'])
@app.route('/portal', methods=['GET', 'POST'])
def portal():
    form = SignUpLoginForm()
    if form.validate_on_submit():
        secret_key, account_id = request.form.get('secret_key'), request.form.get('account_id')

        # whether enrolling or login in: we need to check if account with current info already exists
        user = User.query.filter(User.secret_key == secret_key, User.account_id == account_id).first()

        if request.form.get('submit') == 'Login':
            if not user:
                return render_template('portal.html', form=form, errors=["User does not exist. Please sign up first."])
        elif request.form.get('submit') == 'Enroll':
            if user:
                return render_template('portal.html', form=form, errors=["Account exists, you may just Login"])
            user = User.create(secret_key=secret_key, account_id=account_id)

        # whether login or enroll, login the user eventually
        login_user(user)
        return redirect(url_for('profile'))

    return render_template('portal.html', form=form, errors=form.get_error_msgs())


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('portal'))


'''
Forms
'''


class SignUpLoginForm(Form):
    """
    One form that process enrollment and login (since these two forms have the same fields)
    """
    account_id = StringField('Account ID',
                             validators=[DataRequired(), length(min=6, max=6, message='Must be 6 characters long')])
    secret_key = PasswordField('Secret Key', validators=[DataRequired()])

    def get_error_msgs(self):
        return ["%s: %s" % (getattr(self, f).label.text, e[0]) for f, e in self.errors.items()]
