from django.db import models
import uuid

# Create your models here.
class User(models.Model):
    anki_uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name