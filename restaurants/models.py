from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Location(models.Model):
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.district}, {self.city}"

    class Meta:
        unique_together = ['city', 'district']


class Restaurant(models.Model):
    PRICE_CHOICES = [
        ('€', 'Budget'),
        ('€€', 'Mid-Range'),
        ('€€€', 'Fine Dining'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    price_range = models.CharField(max_length=3, choices=PRICE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    def __str__(self):
        return self.name


class OpeningHours(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='opening_hours')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        unique_together = ['restaurant', 'day_of_week']
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.restaurant.name} - {self.get_day_of_week_display()}"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"


class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['restaurant', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.restaurant.name} - {self.rating}"


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user.username}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'restaurant']

    def __str__(self):
        return f"{self.user.username} - {self.restaurant.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
