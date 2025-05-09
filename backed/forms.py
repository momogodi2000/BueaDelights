from django import forms
from .models import ContactMessage, NewsletterSubscriber
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, ProductImage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address'
            }),
        }


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class ProductForm(forms.ModelForm):
    # Champ pour les catégories existantes
    category = CategoryChoiceField(
        queryset=Category.objects.all(),
        label=_('Catégorie'),
        required=False,
        empty_label=_("Sélectionnez une catégorie")
    )
    
    # Champ pour créer une nouvelle catégorie
    new_category = forms.CharField(
        label=_('Nouvelle catégorie'),
        required=False,
        max_length=100,
        help_text=_("Laissez vide si vous sélectionnez une catégorie existante")
    )
    
    # Champ pour le type de catégorie (utilisé pour les nouvelles catégories)
    category_type = forms.ChoiceField(
        label=_('Type de catégorie'),
        choices=Category.CATEGORY_CHOICES,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'stock_quantity', 
            'ingredients', 'image', 'is_available', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on édite un produit existant, pré-remplir la catégorie
        if self.instance and self.instance.pk:
            self.fields['category'].initial = self.instance.category
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')
        
        # Vérifier qu'une catégorie est spécifiée (soit existante, soit nouvelle)
        if not category and not new_category:
            raise forms.ValidationError(
                _("Vous devez sélectionner une catégorie existante ou créer une nouvelle catégorie")
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Traiter la catégorie
        new_category_name = self.cleaned_data.get('new_category')
        category = self.cleaned_data.get('category')
        
        # Si une nouvelle catégorie est spécifiée, la créer
        if new_category_name:
            category_type = self.cleaned_data.get('category_type') or 'other'
            category, created = Category.objects.get_or_create(
                name=new_category_name,
                defaults={'category_type': category_type}
            )
        
        # Assigner la catégorie (existante ou nouvelle) au produit
        instance.category = category
        
        if commit:
            instance.save()
        return instance


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_main', 'alt_text']


# Formset pour gérer plusieurs images
ProductImageFormSet = forms.inlineformset_factory(
    Product, 
    ProductImage,
    form=ProductImageForm,
    extra=3,   # Nombre de formulaires vides à afficher
    max_num=5  # Nombre maximum d'images autorisées
)


