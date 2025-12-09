from django.db import models
from django.contrib.auth.models import User

CONTENT_RATING_CHOICES = [
    ('G', 'G'),
    ('PG', 'PG'),
    ('PG-13', 'PG-13'),
    ('R', 'R'),
]

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    content_rating = models.CharField(
        max_length=5,
        choices=CONTENT_RATING_CHOICES,
        default='R',
    )
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    def average_rating(self):
        ratings = self.ratings.all()
        return round(sum(r.value for r in ratings) / ratings.count(), 1) if ratings.exists() else 0

    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported = models.BooleanField(default=False)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1–5 stars
    movie = models.ForeignKey(Movie, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('movie', 'user')  # user can rate a movie only once
    
    def __str__(self):
        return f"{self.movie.name} - {self.value} stars by {self.user.username}"