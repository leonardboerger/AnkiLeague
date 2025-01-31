from django.db import models
from user_manager.models import User

# Create your models here.
class Data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Benutzer")
    date = models.DateField()
    reviews = models.PositiveIntegerField()
    time = models.PositiveIntegerField()
    streak = models.PositiveIntegerField()  # in Sekunden
    retention = models.FloatField(verbose_name="Retention (%)", help_text="Erfolgsquote in Prozent")

    class Meta:
        unique_together = ('user', 'date')