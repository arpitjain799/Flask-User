"""This module implements the EmailManager for Flask-User.
It uses Jinja2 to render email subject and email message.
It uses the EmailMailer interface to send emails.
"""

# Author: Ling Thio <ling.thio@gmail.com>
# Copyright (c) 2013 Ling Thio

from flask import render_template, url_for

from flask_user import ConfigError

# The UserManager is implemented across several source code files.
# Mixins are used to aggregate all member functions into the one UserManager class.
class EmailManager(object):
    """ Send email_templates via the configured Email Mailer ``user_manager.email_mailer``. """

    def __init__(self, app):
        """
        Args:
            app(Flask): The Flask application instance.
        """
        self.app = app
        self.user_manager = app.user_manager
        self.sender_name = app.config.get('USER_EMAIL_SENDER_NAME', None)
        self.sender_email = app.config.get('USER_EMAIL_SENDER_EMAIL', None)

    def send_email_confirmation_email(self, user, user_email):
        """Send the 'email confirmation' email."""
        
        # Verify email settings
        if not self.user_manager.USER_ENABLE_EMAIL: return
        if not self.user_manager.USER_SEND_REGISTERED_EMAIL and not self.user_manager.USER_ENABLE_CONFIRM_EMAIL: return

        # Generate confirm email link
        object_id = user_email.id if user_email else user.id
        token = self.user_manager.token_manager.generate_token(object_id)
        confirm_email_link = url_for('user.confirm_email', token=token, _external=True)

        # Retrieve email address from User or UserEmail object
        email = user_email.email if user_email else user.email
        assert(email)

        # Render subject, html message and text message
        subject, html_message, text_message = self._render_email(
                self.user_manager.USER_CONFIRM_EMAIL_TEMPLATE,
                user=user,
                app_name=self.user_manager.USER_APP_NAME,
                confirm_email_link=confirm_email_link)

        # Send email message using Flask-Mail
        self._send_email_message(email, subject, html_message, text_message)

    def send_password_has_changed_email(self, user):
        """Send the 'password has changed' notification email."""

        # Verify email settings
        if not self.user_manager.USER_ENABLE_EMAIL: return
        if not self.user_manager.USER_SEND_PASSWORD_CHANGED_EMAIL: return

        # Retrieve email address from User or UserEmail object
        user_email = self.user_manager.get_primary_user_email(user)
        assert(user_email)
        email = user_email.email
        assert(email)

        # Render subject, html message and text message
        subject, html_message, text_message = self._render_email(
                self.user_manager.USER_PASSWORD_CHANGED_EMAIL_TEMPLATE,
                user=user,
                app_name=self.user_manager.USER_APP_NAME)

        # Send email message using Flask-Mail
        self._send_email_message(email, subject, html_message, text_message)

    def send_reset_password_email(self, user, user_email):
        """Send the 'reset password' email."""

        # Verify email settings
        if not self.user_manager.USER_ENABLE_EMAIL: return
        assert self.user_manager.USER_ENABLE_FORGOT_PASSWORD

        # Generate reset password link
        token = self.user_manager.token_manager.generate_token(user.id)
        reset_password_link = url_for('user.reset_password', token=token, _external=True)

        # Retrieve email address from User or UserEmail object
        email = user_email.email if user_email else user.email
        assert (email)

        # Render subject, html message and text message
        subject, html_message, text_message = self._render_email(
            self.user_manager.USER_RESET_PASSWORD_EMAIL_TEMPLATE,
            user=user,
            app_name=self.user_manager.USER_APP_NAME,
            reset_password_link=reset_password_link)

        # Send email message using Flask-Mail
        self._send_email_message(email, subject, html_message, text_message)

    def send_user_invitation_email(self, user, user_invitation):
        """Send the 'user invitation' email."""

        # Verify email settings
        pass

        token = self.user_manager.token_manager.generate_token(user_invitation.id)
        accept_invitation_link = url_for('user.register', token=token, _external=True)

        # Render subject, html message and text message
        subject, html_message, text_message = self._render_email(
                self.user_manager.USER_INVITE_USER_EMAIL_TEMPLATE,
                user=user,
                app_name=self.user_manager.USER_APP_NAME,
                accept_invitation_link=accept_invitation_link)

        # Send email message using Flask-Mail
        self._send_email_message(user.email, subject, html_message, text_message)

    def send_user_has_registered_email(self, user, user_email, confirm_email_link):    # pragma: no cover
        """Send the 'user has registered' notification email."""

        # Verify email settings
        if not self.user_manager.USER_ENABLE_EMAIL: return
        if not self.user_manager.USER_SEND_REGISTERED_EMAIL: return

        # Retrieve email address from User or UserEmail object
        email = user_email.email if user_email else user.email
        assert(email)

        # Render subject, html message and text message
        subject, html_message, text_message = self._render_email(
                self.user_manager.USER_REGISTERED_EMAIL_TEMPLATE,
                user=user,
                app_name=self.user_manager.USER_APP_NAME,
                confirm_email_link=confirm_email_link)

        # Send email message using Flask-Mail
        self._send_email_message(email, subject, html_message, text_message)

    def send_username_has_changed_email(self, user):  # pragma: no cover
        """Send the 'username has changed' notification email."""

        # Verify email settings
        if not self.user_manager.USER_ENABLE_EMAIL: return
        if not self.user_manager.USER_SEND_USERNAME_CHANGED_EMAIL: return

        # Retrieve email address from User or UserEmail object
        user_email = self.get_primary_user_email(user)
        assert(user_email)
        email = user_email.email
        assert(email)

        # Render subject, html message and text message
        subject, html_message, text_message = self._render_email(
                self.user_manager.USER_USERNAME_CHANGED_EMAIL_TEMPLATE,
                user=user,
                app_name=self.user_manager.USER_APP_NAME)

        # Send email message using Flask-Mail
        self._send_email_message(email, subject, html_message, text_message)

    def _send_email_message(self, recipient, subject, html_message, text_message):
        """Send email via the configured email mailer ``user_manager.email_mailer``. """
        # Skip email sending when testing
        if self.app.testing: return

        # Ensure that USER_EMAIL_SENDER_EMAIL is set
        if not self.sender_email:
            raise ConfigError('Config setting USER_EMAIL_SENDER_EMAIL is missing.')
        # Simplistic email address verification
        if '@' not in self.sender_email:
            raise ConfigError('Config setting USER_EMAIL_SENDER_EMAIL is not a valid email address.')

        self.user_manager.email_mailer.send_email_message(
            recipient, subject, html_message, text_message
        )

    def _render_email(self, filename, **kwargs):
        # Render subject
        subject = render_template(filename+'_subject.txt', **kwargs)
        # Make sure that subject lines do not contain newlines
        subject = subject.replace('\n', ' ')
        subject = subject.replace('\r', ' ')
        # Render HTML message
        html_message = render_template(filename+'_message.html', **kwargs)
        # Render text message
        text_message = render_template(filename+'_message.txt', **kwargs)

        return (subject, html_message, text_message)
