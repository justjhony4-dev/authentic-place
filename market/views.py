from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Case, When, IntegerField
from django.templatetags.static import static
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Vendor, Product, Category
from .forms import VendorForm, ProductForm, VendorUserForm

# =====================================================
# API – LISTES (JSON)
# =====================================================

def vendor_list(request):
    vendors = Vendor.objects.filter(is_verified=True)

    data = [
        {
            "id": v.pk,
            "name": v.name,
            "description": v.description,
            "subscription_plan": v.subscription_plan,
            "whatsapp_number": v.whatsapp_number,
            "image_url": request.build_absolute_uri(
                v.image.url if v.image else static('default-avatar.png')
            ),
        }
        for v in vendors
    ]

    return JsonResponse(data, safe=False)


def product_list(request):
    products = (
        Product.objects
        .filter(is_active=True)
        .select_related('vendor')
    )

    data = [
        {
            "id": p.pk,
            "name": p.name,
            "price": str(p.price),
            "description": p.description,
            "image_url": request.build_absolute_uri(
                p.image.url if p.image else static('default-product.png')
            ),
            "vendor": p.vendor.name,
            "vendor_whatsapp": p.vendor.whatsapp_number,
        }
        for p in products
    ]

    return JsonResponse(data, safe=False)


# =====================================================
# PAGE D’ACCUEIL (Premium en premier + pagination)
# =====================================================

def accueil(request):
    query = request.GET.get('q', '').strip()
    current_category = request.GET.get('category')

    # ===============================
    # 🔹 PRODUITS (requête principale)
    # ===============================
    products_qs = (
        Product.objects
        .filter(is_active=True)
        .select_related('vendor', 'category')
        .only(
            'id',
            'name',
            'price',
            'image',
            'vendor__name',
            'vendor__subscription_plan',
            'category__name',
            'category__slug',
            'created_at',
        )
        .order_by('-created_at')
    )

    # ===============================
    # 🔹 FILTRE CATÉGORIE
    # ===============================
    if current_category:
        products_qs = products_qs.filter(category__slug=current_category)

    # ===============================
    # 🔹 RECHERCHE
    # ===============================
    if query:
        products_qs = products_qs.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(vendor__name__icontains=query)
        )

    # ===============================
    # 🔹 PAGINATION PRODUITS
    # ===============================
    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    # ===============================
    # 🔹 VENDEURS (optimisés + limités)
    # ===============================
    vendors = (
        Vendor.objects
        .filter(is_verified=True)
        .only(
            'id',
            'name',
            'description',
            'image',
            'subscription_plan',
            'created_at',
        )
        .order_by(
            Case(
                When(subscription_plan='premium', then=0),
                default=1,
                output_field=IntegerField()
            ),
            '-created_at'
        )[:12]  # 🔥 limite volontaire
    )

    # ===============================
    # 🔹 CATÉGORIES (léger)
    # ===============================
    categories = (
        Category.objects
        .only('name', 'slug')
        .order_by('name')
    )

    return render(request, 'market/index.html', {
        'products': products,
        'vendors': vendors,
        'categories': categories,
        'query': query,
        'current_category': current_category,
    })


# =====================================================
# AUTHENTIFICATION VENDEUR
# =====================================================

def vendor_register(request):
    if request.method == 'POST':
        user_form = VendorUserForm(request.POST)
        vendor_form = VendorForm(request.POST, request.FILES)

        if user_form.is_valid() and vendor_form.is_valid():
            user = user_form.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor.save()
            login(request, user)
            return redirect('vendor_dashboard')
    else:
        user_form = VendorUserForm()
        vendor_form = VendorForm()

    return render(request, 'market/vendor_register.html', {
        'user_form': user_form,
        'vendor_form': vendor_form,
    })


def vendor_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('vendor_dashboard')

    return render(request, 'market/vendor_login.html', {'form': form})


def vendor_logout(request):
    logout(request)
    return redirect('vendor_login')


# =====================================================
# DASHBOARD VENDEUR (pagination)
# =====================================================

@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('vendor_register')

    vendor = request.user.vendor

    products_qs = (
        vendor.products
        .filter(is_active=True)
        .select_related('category')
        .order_by('-created_at')
    )

    paginator = Paginator(products_qs, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    active_products_count = products_qs.count()
    product_limit = vendor.product_limit()

    return render(request, 'market/vendor_dashboard.html', {
        'vendor': vendor,
        'products': products,
        'active_products_count': active_products_count,
        'product_limit': product_limit,
    })

# =====================================================
# PRODUITS (CRUD)
# =====================================================

@login_required
def add_product(request):
    vendor = get_object_or_404(Vendor, user=request.user)

    if vendor.products.filter(is_active=True).count() >= vendor.product_limit():
        messages.error(
            request,
            "Limite atteinte. Passez à l’abonnement Premium."
        )
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()
            messages.success(request, "Produit ajouté avec succès")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()

    return render(request, 'market/product_form.html', {
        'form': form,
        'title': 'Ajouter un produit',
    })


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if product.vendor.user != request.user:
        return HttpResponseForbidden("Action non autorisée")

    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product
    )

    if form.is_valid():
        form.save()
        messages.success(request, "Produit modifié avec succès")
        return redirect('vendor_dashboard')

    return render(request, 'market/product_form.html', {
        'form': form,
        'title': 'Modifier le produit',
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if product.vendor.user != request.user:
        return HttpResponseForbidden("Action non autorisée")

    product.delete()
    messages.success(request, "Produit supprimé")
    return redirect('vendor_dashboard')


# =====================================================
# PAGES DÉTAILS
# =====================================================

def product_detail(request, pk):
    product = (
        get_object_or_404(
            Product.objects.select_related('vendor', 'category'),
            pk=pk,
            is_active=True
        )
    )
    return render(request, 'market/product_detail.html', {'product': product})


def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk, is_verified=True)

    products = (
        vendor.products
        .filter(is_active=True)
        .select_related('category')
    )

    return render(request, 'market/vendor_detail.html', {
        'vendor': vendor,
        'products': products,
    })


# =====================================================
# PAGE PREMIUM
# =====================================================

@login_required
def premium_page(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('vendor_register')

    return render(request, 'market/premium.html', {
        'vendor': request.user.vendor
    })
