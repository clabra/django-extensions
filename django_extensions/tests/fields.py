# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.db import models
from django.utils import unittest

from django_extensions.db.fields import AutoSlugField


class SluggedTestModel(models.Model):
    title = models.CharField(max_length=42)
    slug = AutoSlugField(populate_from='title')


class ChildSluggedTestModel(SluggedTestModel):
    pass


class AutoSlugFieldTest(unittest.TestCase):
    def setUp(self):
        self.old_installed_apps = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
        settings.INSTALLED_APPS.append('django_extensions.tests')
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0)

    def tearDown(self):
        SluggedTestModel.objects.all().delete()
        settings.INSTALLED_APPS = self.old_installed_apps

    def testAutoCreateSlug(self):
        m = SluggedTestModel(title='foo')
        m.save()
        self.assertEqual(m.slug, 'foo')

    def testAutoCreateNextSlug(self):
        m = SluggedTestModel(title='foo')
        m.save()

        m = SluggedTestModel(title='foo')
        m.save()
        self.assertEqual(m.slug, 'foo-2')

    def testAutoCreateSlugWithNumber(self):
        m = SluggedTestModel(title='foo 2012')
        m.save()
        self.assertEqual(m.slug, 'foo-2012')

    def testAutoUpdateSlugWithNumber(self):
        m = SluggedTestModel(title='foo 2012')
        m.save()
        m.save()
        self.assertEqual(m.slug, 'foo-2012')

    def testUpdateSlug(self):
        m = SluggedTestModel(title='foo')
        m.save()

        # update m instance without using `save'
        SluggedTestModel.objects.filter(pk=m.pk).update(slug='foo-2012')
        # update m instance with new data from the db
        m = SluggedTestModel.objects.get(pk=m.pk)

        self.assertEqual(m.slug, 'foo-2012')

        m.save()
        self.assertEqual(m.slug, 'foo-2012')

    def testSimpleSlugSource(self):
        m = SluggedTestModel(title='-foo')
        m.save()
        self.assertEqual(m.slug, 'foo')

        n = SluggedTestModel(title='-foo')
        n.save()
        self.assertEqual(n.slug, 'foo-2')

        n.save()
        self.assertEqual(n.slug, 'foo-2')

    def testEmptySlugSource(self):
        # regression test

        m = SluggedTestModel(title='')
        m.save()
        self.assertEqual(m.slug, '-2')

        n = SluggedTestModel(title='')
        n.save()
        self.assertEqual(n.slug, '-3')

        n.save()
        self.assertEqual(n.slug, '-3')

    def testInheritanceCreatesNextSlug(self):
        m = SluggedTestModel(title='foo')
        m.save()

        n = ChildSluggedTestModel(title='foo')
        n.save()
        self.assertEqual(n.slug, 'foo-2')

        o = SluggedTestModel(title='foo')
        o.save()
        self.assertEqual(o.slug, 'foo-3')

    def testUnicodeSlug(self): 
        """Using https://pypi.python.org/pypi/awesome-slugify 
        to manage unicode
        
        See doc to manage translations: 
        
        Eg.
        slugify_de = Slugify(pretranslate=GERMAN)
        'ÜBER Über slugify' -> UEBER-Ueber-slugify
        slugify = Slugify()
        'ÜBER Über slugify' -> UBER-Uber-slugify
        
        """
        txt = 'C\'est déjà l\'été.'
        m = SluggedTestModel(title=txt)
        m.save()
        self.assertEqual(m.slug, "cest-deja-lete")

        txt = 'Nín hǎo. Wǒ shì zhōng guó rén'
        m = SluggedTestModel(title=txt)
        m.save()
        self.assertEqual(m.slug, "nin-hao-wo-shi-zhong-guo-ren")

        txt = 'Компьютер'
        m = SluggedTestModel(title=txt)
        m.save()
        self.assertEqual(m.slug, "kompiuter")

        txt = 'jaja---lol-méméméoo--a'
        m = SluggedTestModel(title=txt)
        m.save()
        self.assertEqual(m.slug, "jaja-lol-mememeoo-a")

        txt = 'Cañón chiquitín'
        m = SluggedTestModel(title=txt)
        m.save()
        self.assertEqual(m.slug, "canon-chiquitin")

        txt = 'Я ♥ борщ'
        m = SluggedTestModel(title=txt)
        m.save()
        self.assertEqual(m.slug, "ia-borshch")  # standard translation (see https://pypi.python.org/pypi/awesome-slugify for alternative translations)

        txt = 'ÜBER Über slugify'               
        m = SluggedTestModel(title=txt)
        m.save()
        self.assertEqual(m.slug, "uber-uber-slugify")
