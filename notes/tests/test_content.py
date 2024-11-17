from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user1 = User.objects.create(username='Ross Geller')
        cls.auth_client1 = Client()
        cls.auth_client1.force_login(cls.user1)
        cls.notes1 = Note.objects.create(
            title='Заметка #1',
            text='Текст заметки #1',
            slug='note_1',
            author=cls.user1
        )

        cls.user2 = User.objects.create(username='Chendler Bing')
        cls.auth_client2 = Client()
        cls.auth_client2.force_login(cls.user2)

    def test_is_note_list(self):
        """Отдельная заметка передаётся на страницу
        со списком заметок в списке object_list
        в словаре context.
        """
        url = reverse('notes:list')
        response = self.auth_client1.get(url)
        object_list = response.context['object_list']
        all_slugs = [note.slug for note in object_list]
        self.assertIn(self.notes1.slug, all_slugs)

    def test_in_the_list_no_other_notes(self):
        """В список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        url = reverse('notes:list')
        response = self.auth_client2.get(url)
        object_list = response.context['object_list']
        all_slugs = [note.slug for note in object_list]
        self.assertNotIn(self.notes1.slug, all_slugs)

    def test_forms_on_pages(self):
        """На страницы создания и редактирования заметки
        передаются формы.
        """
        urls_pages = (
            ('notes:add', None),
            ('notes:edit', (self.notes1.slug,))
        )
        for url_name, args in urls_pages:
            url = reverse(url_name, args=args)
            response = self.auth_client1.get(url)
            self.assertIsInstance(response.context['form'], NoteForm)
