from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils.timezone import now
from PIL import Image
from django.conf import settings
import os

class Vendor(models.Model):

    PLAN_CHOICES = (
        ('free', 'Gratuit'),
        ('premium', 'Premium'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    whatsapp_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{8,15}$',
                message="Numéro WhatsApp invalide"
            )
        ]
    )

    image = models.ImageField(upload_to='vendors/', null=True, blank=True)

    # 🔐 Abonnement
    subscription_plan = models.CharField(
        max_length=10,
        choices=PLAN_CHOICES,
        default='free'
    )

    subscription_end = models.DateField(null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_premium(self):
        return (
            self.subscription_plan == 'premium'
            and self.subscription_end
            and self.subscription_end >= now().date()
        )

    def product_limit(self):
        return 5 if self.subscription_plan == 'free' else 100

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=100)
    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔧 PARAMÈTRES IMAGE
    IMAGE_MAX_SIZE = (800, 800)
    IMAGE_QUALITY = 85

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            image_path = self.image.path

            try:
                img = Image.open(image_path)

                # Convertir en RGB si nécessaire
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Redimensionner si trop grande
                if img.width > 800 or img.height > 800:
                    img.thumbnail(self.IMAGE_MAX_SIZE)

                # Sauvegarde optimisée
                img.save(
                    image_path,
                    format="JPEG",
                    quality=self.IMAGE_QUALITY,
                    optimize=True
                )

            except Exception as e:
                print("Erreur redimensionnement image:", e)

    def __str__(self):
        return self.name
