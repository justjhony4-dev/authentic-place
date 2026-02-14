from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re

from .models import Vendor, Product


# =========================
# STYLES UNIFIÉS
# =========================

text_input_class = (
    'w-full p-3 border border-slate-300 rounded-lg '
    'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition'
)

password_input_class = text_input_class


# =========================
# FORM UTILISATEUR VENDEUR
# =========================

class VendorUserForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': text_input_class,
            'placeholder': 'adresse@email.com'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

        widgets = {
            'username': forms.TextInput(attrs={
                'class': text_input_class,
                'placeholder': 'Nom d’utilisateur'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': password_input_class,
            'placeholder': 'Mot de passe sécurisé'
        })

        self.fields['password2'].widget.attrs.update({
            'class': password_input_class,
            'placeholder': 'Confirmez le mot de passe'
        })


# =========================
# FORM PROFIL VENDEUR
# =========================

class VendorForm(forms.ModelForm):

    class Meta:
        model = Vendor
        fields = ['name', 'description', 'whatsapp_number', 'image']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': text_input_class,
                'placeholder': 'Nom de votre boutique'
            }),
            'description': forms.Textarea(attrs={
                'class': text_input_class,
                'rows': 4,
                'placeholder': 'Présentez votre activité et vos produits'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': text_input_class,
                'placeholder': '+509XXXXXXXX'
            }),
            'image': forms.FileInput(attrs={
                'class': 'sr-only',
                'id': 'image-upload'
            }),
        }

    def clean_whatsapp_number(self):
        number = self.cleaned_data.get('whatsapp_number')

        pattern = r'^\+\d{8,15}$'
        if not re.match(pattern, number):
            raise ValidationError(
                "Numéro WhatsApp invalide. Exemple : +509XXXXXXXX"
            )

        return number

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        if len(name) < 3:
            raise ValidationError(
                "Le nom de la boutique doit contenir au moins 3 caractères."
            )
        return name


# =========================
# FORM PRODUIT
# =========================

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': text_input_class,
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': text_input_class,
                'rows': 4,
                'placeholder': 'Description détaillée du produit'
            }),
            'price': forms.NumberInput(attrs={
                'class': text_input_class,
                'placeholder': 'Prix en HTG',
                'min': 1
            }),
            'image': forms.FileInput(attrs={
                'class': 'sr-only',
                'id': 'image-upload'
            }),
            'category': forms.Select(attrs={
                'class': text_input_class
            }),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is None or price <= 0:
            raise ValidationError("Le prix doit être supérieur à 0.")

        if price > 1_000_000:
            raise ValidationError("Prix trop élevé.")

        return price
