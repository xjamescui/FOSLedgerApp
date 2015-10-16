from flask import render_template, redirect, url_for, request
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email, length
from src import app
from src.models import User

'''
Routes
'''


@app.route('/', methods=['GET', 'POST'])
@app.route('/portal', methods=['GET', 'POST'])
def portal():
    form = EnrollLoginForm()
    if form.validate_on_submit():
        email, account_id = request.form.get('email'), request.form.get('account_id')

        # whether enrolling or login in: we need to check if account with current info already exists
        user = User.query.filter(User.email == email, User.account_id == account_id).first()

        # user has requested to login
        if request.form.get('submit') == 'Login':
            if user is None:
                return render_template('portal.html', form=form, errors=["User does not exist. Please enroll first."])

            # TODO authenticate user

        # user has requested to enroll
        elif request.form.get('submit') == 'Enroll':
            if user:
                return render_template('portal.html', form=form, errors=["Membership exists, you may just Login"])

            # TODO create user
        return redirect(url_for('profile'))
    return render_template('portal.html', form=form, errors=form.get_error_msgs())


@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')


'''
Forms
'''


class EnrollLoginForm(Form):
    """
    One form that process enrollment and login (since these two forms have the same fields)
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    account_id = StringField('Account ID',
                             validators=[DataRequired(), length(min=6, max=6, message='Must be 6 characters long')])

    def get_error_msgs(self):
        return ["%s: %s" % (getattr(self, f).label.text, e[0]) for f, e in self.errors.items()]
