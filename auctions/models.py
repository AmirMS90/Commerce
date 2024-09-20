from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    image_link = models.CharField(max_length=128, null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="listings",
        null=True,
        blank=True,
    )
    current = models.FloatField(default=0.01)
    starting_bid = models.FloatField(default=0.01)
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings"
    )
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listing", default=None, null=True
    )

    def __str__(self):
        return self.title


class User(AbstractUser):
    watchList = models.ManyToManyField(
        Listing, related_name="watchers", null=True, default=None
    )


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.FloatField()

    def __str__(self):
        return f"{self.user.username}: {self.price}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
