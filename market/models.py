from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.conf import settings


# ======================================================
# VENDOR
# ======================================================

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

    # IMAGE STOCKEE SUR IMAGEKIT
    image = models.ImageField(
        upload_to='vendors/',
        null=True,
        blank=True
    )


    # ABONNEMENT

    subscription_plan = models.CharField(
        max_length=10,
        choices=PLAN_CHOICES,
        default='free'
    )

    subscription_end = models.DateField(
        null=True,
        blank=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    # PREMIUM CHECK

    def is_premium(self):

        return (

            self.subscription_plan == 'premium'
            and self.subscription_end
            and self.subscription_end >= now().date()

        )


    def product_limit(self):

        if self.subscription_plan == 'free':

            return 5

        return 100


    def __str__(self):

        return self.name



# ======================================================
# CATEGORY
# ======================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )


    class Meta:

        verbose_name_plural = "Categories"


    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


    def __str__(self):

        return self.name



# ======================================================
# PRODUCT
# ======================================================

class Product(models.Model):

    vendor = models.ForeignKey(

        Vendor,

        on_delete=models.CASCADE,

        related_name='products'

    )


    name = models.CharField(
        max_length=100
    )


    description = models.TextField()


    price = models.DecimalField(

        max_digits=10,

        decimal_places=2

    )


    # IMAGE IMAGEKIT READY

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


    is_active = models.BooleanField(

        default=True

    )


    created_at = models.DateTimeField(

        auto_now_add=True

    )



    # URL IMAGE SAFE

    @property

    def image_url(self):

        if self.image:

            return self.image.url

        return "/static/images/no-image.png"



    def __str__(self):

        return self.name