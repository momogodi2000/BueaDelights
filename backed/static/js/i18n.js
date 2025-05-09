document.addEventListener('DOMContentLoaded', function() {
    // Check for saved language preference or use browser language
    const savedLang = localStorage.getItem('preferredLang') || navigator.language.slice(0, 2);
    const currentLang = ['fr', 'en'].includes(savedLang) ? savedLang : 'fr';
    
    // Set initial language
    setLanguage(currentLang);
    
    // Language switcher event listeners
    document.querySelectorAll('.language-switcher').forEach(switcher => {
        switcher.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.getAttribute('data-lang');
            setLanguage(lang);
            localStorage.setItem('preferredLang', lang);
        });
    });
    
    // Translation dictionary
    const translations = {
        'fr': {
            // General terms
            'dashboard': 'Tableau de bord',
            'products': 'Produits',
            'orders': 'Commandes',
            'customers': 'Clients',
            'settings': 'Paramètres',
            'logout': 'Déconnexion',
            'search': 'Rechercher...',
            'view_all': 'Voir tout',
            'notifications': 'Notifications',
            'profile': 'Profil',
            'switch_language': 'Changer de langue',
            
            // Product management terms
            'product_management': 'Gestion des Produits',
            'add_product': 'Ajouter un Produit',
            'edit_product': 'Modifier le Produit',
            'delete_product': 'Supprimer le Produit',
            'back_to_products': 'Retour aux produits',
            'product_name': 'Nom du Produit',
            'category': 'Catégorie',
            'select_category': 'Sélectionnez une catégorie',
            'price': 'Prix',
            'stock_quantity': 'Quantité en Stock',
            'availability': 'Disponibilité',
            'available': 'Disponible',
            'unavailable': 'Indisponible',
            'featured_product': 'Produit Phare',
            'mark_as_featured': 'Marquer comme produit phare',
            'product_image': 'Image du Produit',
            'image_requirements': 'Format JPEG ou PNG. Taille maximale 2MB.',
            'description': 'Description',
            'ingredients': 'Ingrédients',
            'reset': 'Réinitialiser',
            'save_product': 'Enregistrer le Produit',
            'update_product': 'Mettre à jour le Produit',
            'confirm_deletion': 'Confirmation de suppression',
            'delete_warning': 'Êtes-vous sûr de vouloir supprimer ce produit ? Cette action est irréversible.',
            'cancel': 'Annuler',
            'confirm_delete': 'Confirmer la suppression',
            'image': 'Image',
            'name': 'Nom',
            'stock': 'Stock',
            'status': 'Statut',
            'actions': 'Actions',
            'all_categories': 'Toutes les catégories',
            'filter': 'Filtrer',
            'showing': 'Affichage de',
            'to': 'à',
            'of': 'sur',
            'results': 'résultats',
            'previous': 'Précédent',
            'next': 'Suivant',
            'units': 'unités',
            'date_created': 'Date de création',
            'last_updated': 'Dernière mise à jour',
            'featured': 'Produit phare',
            'regular': 'Produit régulier'
        },
        'en': {
            // General terms
            'dashboard': 'Dashboard',
            'products': 'Products',
            'orders': 'Orders',
            'customers': 'Customers',
            'settings': 'Settings',
            'logout': 'Logout',
            'search': 'Search...',
            'view_all': 'View all',
            'notifications': 'Notifications',
            'profile': 'Profile',
            'switch_language': 'Switch language',
            
            // Product management terms
            'product_management': 'Product Management',
            'add_product': 'Add Product',
            'edit_product': 'Edit Product',
            'delete_product': 'Delete Product',
            'back_to_products': 'Back to products',
            'product_name': 'Product Name',
            'category': 'Category',
            'select_category': 'Select a category',
            'price': 'Price',
            'stock_quantity': 'Stock Quantity',
            'availability': 'Availability',
            'available': 'Available',
            'unavailable': 'Unavailable',
            'featured_product': 'Featured Product',
            'mark_as_featured': 'Mark as featured',
            'product_image': 'Product Image',
            'image_requirements': 'JPEG or PNG format. Max size 2MB.',
            'description': 'Description',
            'ingredients': 'Ingredients',
            'reset': 'Reset',
            'save_product': 'Save Product',
            'update_product': 'Update Product',
            'confirm_deletion': 'Confirm Deletion',
            'delete_warning': 'Are you sure you want to delete this product? This action cannot be undone.',
            'cancel': 'Cancel',
            'confirm_delete': 'Confirm Delete',
            'image': 'Image',
            'name': 'Name',
            'stock': 'Stock',
            'status': 'Status',
            'actions': 'Actions',
            'all_categories': 'All categories',
            'filter': 'Filter',
            'showing': 'Showing',
            'to': 'to',
            'of': 'of',
            'results': 'results',
            'previous': 'Previous',
            'next': 'Next',
            'units': 'units',
            'date_created': 'Date created',
            'last_updated': 'Last updated',
            'featured': 'Featured',
            'regular': 'Regular'
        }
    };
    
    // Function to set language
    function setLanguage(lang) {
        document.documentElement.lang = lang;
        
        // Update all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                element.textContent = translations[lang][key];
            }
        });
        
        // Update active language switcher
        document.querySelectorAll('.language-switcher').forEach(switcher => {
            if (switcher.getAttribute('data-lang') === lang) {
                switcher.classList.add('active');
            } else {
                switcher.classList.remove('active');
            }
        });
    }
    
    // Expose function to global scope for manual language switching
    window.setLanguage = setLanguage;
});