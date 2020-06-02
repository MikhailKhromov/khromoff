from django.db import models
from django.db.models import signals
from django.dispatch import receiver

from search.scraping.utils import convert_text


class RawPage(models.Model):
    # crawler saves it's data here.
    url = models.CharField(max_length=300)
    domain = models.CharField(max_length=100)
    html = models.CharField(max_length=999999)

    # TODO: add something else so it is useful


class Page(models.Model):
    domain = models.CharField(max_length=100)
    url = models.CharField(max_length=5000)
    # TODO: add domain
    description = models.CharField(max_length=500)  # which you show near the query
    page_path = models.CharField(max_length=300)

    def __str__(self):
        return str(self.url)


@receiver(signals.post_save, sender=Page)
def add_searchwords(sender, instance, created, **kwargs):
    if created:
        for i in instance.meta.title.split():
            # save something like SAO or CS (computer since), but delete Moscow (->moscow) or Linux.
            if i == i.upper():
                word = i
            else:
                word = i.lower()

            word = convert_text(word)
            if word == '':
                return

            a = SearchWord.objects.filter(word=word)
            if not a.exists():
                instance.searchword_set.create(word=word)
            else:
                a[0].pages.add(instance)


class SearchWord(models.Model):
    pages = models.ManyToManyField(Page)
    word = models.CharField(max_length=50)
    
    def __str__(self):
        return str(self.word)
