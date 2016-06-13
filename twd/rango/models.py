from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_pictures', blank=True)

    def get_picture_url(self):
        return "<a href='{}'>Click here</a>".format(self.picture.url)
    get_picture_url.allow_tags = True
    get_picture_url.short_description = 'Profile picture'

    def __unicode__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def number_of_pages(self):
        return self.page_set.count()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title
