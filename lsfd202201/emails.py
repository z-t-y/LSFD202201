from threading import Thread
from flask_mail import Message
from flask import render_template, Flask, current_app
from lsfd202201.extensions import mail


def _send_async_email(app: Flask, msg) -> int:
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.exception(e)
        else:
            current_app.logger.info("Email Success")


def send_email(recipents: list, **kwargs) -> Thread:
    msg = Message(
        subject="A new article was added just now",
        recipients=recipents
    )
    msg.body = render_template("admin_notifactions.txt", **kwargs)
    msg.html = render_template("admin_notifactions.html", **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_email, args=[app, msg])
    thr.start()
    return thr