from django.db import models
from django.contrib.auth.models import User
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.base import ContentFile

# Create your models here.

class ImagePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    tags = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='blog_image/%Y/%m/%d/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
    # Check if image exists
        if not self.image:
            super().save(*args, **kwargs)
            return
        # Save the original image
        super().save(*args, **kwargs)
        # Resize the image if needed
        img_path = self.image.path
        img = PILImage.open(img_path)
        max_size = (1024, 1024)
        if img.size[0] > 1024 or img.size[1] > 1024:
            img.thumbnail(max_size, PILImage.Resampling.LANCZOS)
            # Save resized image
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            self.image.save(self.image.name, ContentFile(buffer.getvalue()), save=False)