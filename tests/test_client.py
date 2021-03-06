# flake8: noqa
import unittest
import os
from flask_mail import Message, Mail
from flask import abort
from faker import Faker
from lsfd202201.models import User, db, Article, Feedback
from lsfd202201 import create_app

fake = Faker()


class TestClient(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app("testing")
        self.mail = Mail(self.app)
        self.context = self.app.test_request_context()
        self.context.push()
        self.client = self.app.test_client()
        db.create_all()
        admin = User(name="andyzhou")
        admin.set_password("PasswordForTesting")
        db.session.add(admin)
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()
        db.session.remove()
        self.context.pop()

    def login_as_admin(self):
        data = {"name": "andyzhou", "password": "PasswordForTesting"}
        response = self.client.post("/admin/login", data=data, follow_redirects=True)
        return response

    def create_article(self):
        data = {
            "name": fake.name(),
            "password": "article-password",
            "date": fake.date_this_year(),
            "title": fake.sentence(),
            "content": fake.text(200),
        }
        response = self.client.post("/articles/new", data=data, follow_redirects=True)
        return response

    def create_feedback(self):
        data = {"name": fake.name(), "body": fake.text(100)}
        response = self.client.post("/feedback/", data=data)
        return response

    def test_app_exists(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config["TESTING"])

    def test_200(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/index/").status_code, 200)
        self.assertEqual(self.client.get("/main/").status_code, 200)
        self.assertEqual(self.client.get("/articles/").status_code, 200)
        self.assertEqual(self.client.get("/feedback/").status_code, 200)
        self.assertEqual(self.client.get("/members/").status_code, 200)
        self.assertEqual(self.client.get("/video/").status_code, 200)
        self.assertEqual(self.client.get("/about/").status_code, 200)
        self.assertEqual(self.client.get("/kzkt/").status_code, 200)

    def test_401(self):
        self.assertEqual(self.client.get("/admin").status_code, 401)

    def test_404(self):
        self.assertEqual(self.client.get("/thisDoesn'tExist").status_code, 404)

    def test_500(self):
        @self.app.route("/500")
        def internal_server_error_for_testing():
            abort(500)

        response = self.client.get("/500")
        received_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn("500 Internal Server Error", received_data)
        self.assertIn("nav", received_data)

    def test_400(self):
        @self.app.route("/400")
        def internal_server_error_for_testing():
            abort(400)

        response = self.client.get("/400")
        received_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("400 Bad Request", received_data)
        self.assertIn("nav", received_data)

    def test_add_article(self):
        article = Article(title="Test", author="Test", date="Test", content="Test")
        self.assertEqual(str(article), "<Article Test>")
        db.session.add(article)
        db.session.commit()
        self.assertIsNotNone(Article.query_by_id(1))
        self.assertEqual(self.client.get("/articles/").status_code, 200)
        article.delete()
        self.assertIsNone(Article.query_by_id(1))

    def test_post_article(self):
        data = {
            "name": fake.name(),
            "password": fake.password(),
            "date": fake.date_this_year(),
            "title": fake.sentence(),
            "content": fake.text(200),
        }
        response = self.client.post("/articles/new", data=data, follow_redirects=True)
        received_data = response.get_data(as_text=True)
        self.assertIn("Wrong Password", received_data)
        self.assertEqual(Article.query.count(), 0)
        response = self.create_article()
        received_data = response.get_data(as_text=True)
        self.assertIn("Success", received_data)
        self.assertEqual(Article.query.count(), 1)

    def test_feedback(self):
        fake_name = fake.name()
        fake_body = fake.text(100)
        data = {"name": fake_name, "body": fake_body}
        response = self.client.post("/feedback/", data=data)
        self.assertEqual(response.status_code, 200)
        received_data = response.get_data(as_text=True)
        self.assertIn(fake_body, received_data)

    def test_emails(self):
        with self.mail.record_messages() as outbox:
            msg = Message(
                recipients=self.app.config["ADMIN_EMAIL_LIST"],
                subject="LSFD202201 Project Unittest",
                body="Plain Text",
                html="<strong>HTML</strong> <em>Content</em>",
            )
            self.mail.send(msg)
            self.assertGreater(len(outbox), 0)
            self.assertEqual(outbox[0].subject, "LSFD202201 Project Unittest")

    def test_admin_basic(self):
        response = self.client.get("/admin/logout")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/admin/feedbacks")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/admin/login")
        self.assertEqual(response.status_code, 200)
        self.login_as_admin()
        response = self.client.get("/admin/login")
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        self.create_article()
        response = self.client.get("/admin/articles/edit/1")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/feedbacks")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/logout")
        self.assertEqual(response.status_code, 302)

    def test_admin_login(self):
        data = {"name": "andyzhou", "password": "WrongPassword"}
        response = self.client.post("/admin/login", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        received_data = response.get_data(as_text=True)
        self.assertIn("Invalid username", received_data)
        data["password"] = "PasswordForTest"
        response = self.login_as_admin()
        received_data = response.get_data(as_text=True)
        self.assertIn("Welcome, Administrator", received_data)

    def test_admin_delete_article(self):
        self.login_as_admin()
        self.create_article()
        response = self.client.post("/admin/articles/delete/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Article.query.all()), 0)

    def test_admin_edit_article(self):
        self.login_as_admin()
        self.create_article()
        fake_text = fake.text(200)
        data = {"content": fake_text}
        response = self.client.post("/admin/articles/edit/1", data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        received_data = response.get_data(as_text=True)
        self.assertIn("Edit Succeeded!", received_data)
        print()
        article = Article.query_by_id(1)
        self.assertEqual(article.content, fake_text)

    def test_admin_delete_feedback(self):
        self.login_as_admin()
        self.create_feedback()
        self.assertGreater(len(Feedback.query.all()), 0)
        response = self.client.post("/admin/feedback/delete/1")
        self.assertEqual(response.status_code, 200)
        received_data = response.get_data(as_text=True)
        self.assertIn("deleted", received_data)
