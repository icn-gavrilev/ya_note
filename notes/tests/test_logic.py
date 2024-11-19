from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create(username='Monika Geller')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.alien = User.objects.create(username='Sheldon Lee Cooper')
        cls.auth_alien = Client()
        cls.auth_alien.force_login(cls.alien)

        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заматка #1',
            'text': 'Текст заметки #1',
            'slug': 'note_1',
        }
        cls.urls = (
            ('notes:edit', (cls.form_data['slug'],)),
            ('notes:delete', (cls.form_data['slug'],)),
        )

    def test_user_can_create_note(self):
        """Залогиненный пользователь может
        создать заметку.
        """
        self.auth_client.post(self.url, self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_anon_cant_create_note(self):
        """Анонимный пользователь не может
        создать заметку.
        """
        self.client.post(self.url, self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_create_two_notes_with_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.auth_client.post(self.url, self.form_data)
        self.auth_client.post(self.url, self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note_without_slug(self):
        """Залогиненный пользователь может
        создать заметку без slug.
        """
        self.auth_client.post(
            self.url,
            {
                'title': 'Заматка #1',
                'text': 'Текст заметки #1'
            }
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_edit_or_delete_note(self):
        """Залогиненный пользователь может
        редактировать или удалять свою заметку.
        """
        self.auth_client.post(self.url, self.form_data)
        for name, args in self.urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_cant_edit_or_delete_alien_note(self):
        """Залогиненный пользователь не может
        редактировать или удалять чужую заметку.
        """
        self.auth_alien.post(self.url, self.form_data)
        for name, args in self.urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
