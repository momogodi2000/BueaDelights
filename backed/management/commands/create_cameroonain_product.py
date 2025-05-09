from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from backed.models import Category, Product
import os
from django.core.files import File
from django.conf import settings
import random

class Command(BaseCommand):
    help = 'Create realistic Cameroonian food products in the database'

    def handle(self, *args, **options):
        self.stdout.write('Creating categories and products...')
        
        # Create or get categories
        categories = self._create_categories()
        
        # Create products by category
        self._create_chips_products(categories['chips'])
        self._create_juice_products(categories['juice'])
        self._create_yogurt_products(categories['yogurt'])
        self._create_croquettes_products(categories['croquettes'])
        self._create_caramel_products(categories['caramel'])
        self._create_crepes_products(categories['crepes'])
        self._create_pizza_products(categories['pizza'])
        self._create_nems_products(categories['nems'])
        self._create_pile_products(categories['pile'])
        self._create_cake_products(categories['cake'])
        self._create_other_products(categories['other'])
        
        self.stdout.write(self.style.SUCCESS('Successfully created Cameroonian products!'))

    def _create_categories(self):
        categories = {}
        category_choices = [
            ('chips', _('Chips')),
            ('juice', _('Jus naturels')),
            ('yogurt', _('Yaourts')),
            ('croquettes', _('Croquettes')),
            ('caramel', _('Caramels')),
            ('crepes', _('Crêpes')),
            ('pizza', _('Pizza')),
            ('nems', _('Nems')),
            ('pile', _('Pilé (plat traditionnel)')),
            ('cake', _('Gâteaux')),
            ('other', _('Autre')),
        ]
        
        for category_type, category_name in category_choices:
            category, created = Category.objects.get_or_create(
                category_type=category_type,
                defaults={'name': category_name}
            )
            categories[category_type] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Using existing category: {category.name}')
                
        return categories
    
    def _create_product(self, name, description, category, price, stock_quantity, ingredients, is_featured=False):
        # Check if product already exists
        if Product.objects.filter(name=name, category=category).exists():
            self.stdout.write(f'Product already exists: {name}')
            return

        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            price=price,
            stock_quantity=stock_quantity,
            ingredients=ingredients,
            is_featured=is_featured
        )
        
        self.stdout.write(f'Created product: {product.name}')
        return product
    
    def _create_chips_products(self, category):
        # Chips - 3 types (sweet, unsweetened, and salty)
        sweet_plantain_chips = {
            'name': 'Chips De Plantain Sucrées',
            'description': 'Délicieuses chips de plantain sucrées, préparées artisanalement à partir de bananes plantain mûres. '
                          'Une spécialité camerounaise appréciée comme collation sucrée.',
            'price': 500,  # FCFA
            'stock_quantity': 50,
            'ingredients': 'Plantains mûrs, huile de palme rouge, sucre de canne, une pincée de sel.',
            'is_featured': True
        }
        
        unsweetened_plantain_chips = {
            'name': 'Chips De Plantain Nature',
            'description': 'Chips de plantain nature, croustillantes et légères. Préparées selon la tradition camerounaise '
                          'avec des plantains à peine mûrs pour un goût authentique.',
            'price': 450,
            'stock_quantity': 75,
            'ingredients': 'Plantains verts, huile végétale, une pincée de sel.',
            'is_featured': False
        }
        
        salty_cassava_chips = {
            'name': 'Chips De Manioc Salées',
            'description': 'Chips croustillantes à base de manioc frais, légèrement salées. Une alternative locale '
                          'populaire aux chips de pomme de terre, typique du Cameroun.',
            'price': 600,
            'stock_quantity': 40,
            'ingredients': 'Manioc frais, huile de palme, sel, épices.',
            'is_featured': False
        }
        
        self._create_product(**sweet_plantain_chips, category=category)
        self._create_product(**unsweetened_plantain_chips, category=category)
        self._create_product(**salty_cassava_chips, category=category)
    
    def _create_juice_products(self, category):
        # 5 types of natural juices
        juices = [
            {
                'name': 'Jus de Gingembre Frais',
                'description': 'Jus de gingembre piquant préparé avec du gingembre frais local. Une boisson rafraîchissante '
                              'et énergisante, traditionnelle au Cameroun.',
                'price': 800,
                'stock_quantity': 30,
                'ingredients': 'Gingembre frais, citron, miel, eau filtrée, menthe (optionnel).',
                'is_featured': True
            },
            {
                'name': 'Jus de Baobab (Bouye)',
                'description': 'Boisson crémeuse et nutritive à base de fruit de baobab. Riche en vitamines et minéraux, '
                              'ce jus est prisé pour ses bienfaits sur la santé.',
                'price': 900,
                'stock_quantity': 25,
                'ingredients': 'Pulpe de fruit de baobab, eau filtrée, sucre de canne, lait concentré (optionnel).',
                'is_featured': False
            },
            {
                'name': 'Jus de Bissap (Hibiscus)',
                'description': 'Boisson rouge vif préparée à partir de fleurs d\'hibiscus séchées. Rafraîchissante avec '
                              'une note acidulée, très populaire pendant les fêtes.',
                'price': 750,
                'stock_quantity': 45,
                'ingredients': 'Fleurs d\'hibiscus séchées, eau filtrée, sucre, jus d\'ananas, menthe fraîche.',
                'is_featured': True
            },
            {
                'name': 'Jus de Foléré',
                'description': 'Version traditionnelle du jus d\'hibiscus, préparée selon une recette du Nord Cameroun, '
                              'avec une saveur légèrement épicée.',
                'price': 800,
                'stock_quantity': 35,
                'ingredients': 'Fleurs de roselle (folere), eau filtrée, sucre, clous de girofle, gingembre.',
                'is_featured': False
            },
            {
                'name': 'Cocktail de Fruits Tropicaux',
                'description': 'Mélange rafraîchissant de jus extraits de fruits tropicaux camerounais frais. '
                              'Une explosion de saveurs exotiques dans chaque gorgée.',
                'price': 1000,
                'stock_quantity': 20,
                'ingredients': 'Ananas, papaye, goyave, fruit de la passion, banane, sucre de canne (selon besoin).',
                'is_featured': True
            }
        ]
        
        for juice in juices:
            self._create_product(**juice, category=category)
    
    def _create_yogurt_products(self, category):
        # 3 types of yogurts + 3 with fruits
        yogurts = [
            {
                'name': 'Yaourt Nature Artisanal',
                'description': 'Yaourt crémeux nature préparé traditionnellement, légèrement acidulé et onctueux. '
                              'Fabriqué avec du lait frais de fermes locales.',
                'price': 600,
                'stock_quantity': 40,
                'ingredients': 'Lait entier frais, ferments lactiques vivants.',
                'is_featured': False
            },
            {
                'name': 'Yaourt Sucré à la Vanille',
                'description': 'Yaourt doux et crémeux parfumé à la vanille naturelle. Une douceur appréciée '
                              'de tous les amateurs de produits laitiers.',
                'price': 650,
                'stock_quantity': 35,
                'ingredients': 'Lait entier frais, ferments lactiques, sucre, extrait naturel de vanille.',
                'is_featured': True
            },
            {
                'name': 'Yaourt Miel et Amandes',
                'description': 'Yaourt délicatement sucré au miel d\'abeilles camerounaises et garni d\'éclats d\'amandes. '
                              'Un mélange parfait de douceur et de croquant.',
                'price': 750,
                'stock_quantity': 25,
                'ingredients': 'Lait entier frais, ferments lactiques, miel naturel, amandes concassées.',
                'is_featured': False
            },
            {
                'name': 'Yaourt aux Fruits de la Passion',
                'description': 'Yaourt onctueux agrémenté de morceaux de fruits de la passion. Son goût exotique '
                              'et acidulé vous transportera au cœur des saveurs camerounaises.',
                'price': 700,
                'stock_quantity': 30,
                'ingredients': 'Lait entier frais, ferments lactiques, fruits de la passion, sucre de canne.',
                'is_featured': True
            },
            {
                'name': 'Yaourt à la Papaye',
                'description': 'Yaourt fruité à la papaye fraîche, doux et légèrement sucré. Une spécialité locale '
                              'qui célèbre l\'un des fruits les plus cultivés au Cameroun.',
                'price': 700,
                'stock_quantity': 30,
                'ingredients': 'Lait entier frais, ferments lactiques, purée de papaye fraîche, sucre.',
                'is_featured': False
            },
            {
                'name': 'Yaourt à la Mangue',
                'description': 'Yaourt crémeux aux morceaux de mangue juteuse. Un délice tropical qui vous '
                              'rappellera les vergers luxuriants du Cameroun.',
                'price': 750,
                'stock_quantity': 25,
                'ingredients': 'Lait entier frais, ferments lactiques, morceaux de mangue fraîche, sucre.',
                'is_featured': False
            }
        ]
        
        for yogurt in yogurts:
            self._create_product(**yogurt, category=category)
    
    def _create_croquettes_products(self, category):
        # 3 types of croquettes
        croquettes = [
            {
                'name': 'Croquettes de Manioc',
                'description': 'Croquettes croustillantes à base de manioc râpé et d\'épices locales. '
                              'Un en-cas populaire dans tout le Cameroun, parfait pour l\'apéritif.',
                'price': 700,
                'stock_quantity': 40,
                'ingredients': 'Manioc râpé, oignons, poivrons, piment, sel, huile pour friture.',
                'is_featured': True
            },
            {
                'name': 'Croquettes de Poisson à la Camerounaise',
                'description': 'Délicieuses croquettes préparées avec du poisson local frais et assaisonnées '
                              'avec des épices traditionnelles camerounaises.',
                'price': 850,
                'stock_quantity': 30,
                'ingredients': 'Filet de poisson frais, oignons, ail, persil, piment, farine, œufs, huile.',
                'is_featured': False
            },
            {
                'name': 'Accras de Haricots (Koki)',
                'description': 'Version camerounaise des accras, préparée à base de haricots blancs moulus. '
                              'Croustillantes à l\'extérieur et moelleuses à l\'intérieur.',
                'price': 750,
                'stock_quantity': 35,
                'ingredients': 'Haricots blancs, oignons, huile de palme, piment, sel, bouillon naturel.',
                'is_featured': False
            }
        ]
        
        for croquette in croquettes:
            self._create_product(**croquette, category=category)
    
    def _create_caramel_products(self, category):
        # Caramel products
        caramel = {
            'name': 'Caramels à la Vanille',
            'description': 'Caramels artisanaux parfumés à la vanille naturelle, préparés selon une recette '
                          'traditionnelle camerounaise. Texture lisse et saveur intense.',
            'price': 550,
            'stock_quantity': 60,
            'ingredients': 'Sucre de canne, lait concentré, beurre, extrait naturel de vanille, une pincée de sel.',
            'is_featured': True
        }
        
        self._create_product(**caramel, category=category)
    
    def _create_crepes_products(self, category):
        # 5 types of crepes
        crepes = [
            {
                'name': 'Crêpe Simple Traditionnelle',
                'description': 'Crêpe fine et légère préparée selon la tradition camerounaise. '
                              'Parfaite pour accueillir garnitures sucrées ou salées.',
                'price': 400,
                'stock_quantity': 50,
                'ingredients': 'Farine de blé, œufs, lait, sucre, huile, une pincée de sel.',
                'is_featured': False
            },
            {
                'name': 'Crêpe au Chocolat Noir',
                'description': 'Délicieuse crêpe garnie de chocolat noir fondu, préparé à partir de fèves de cacao '
                              'cultivées localement dans les régions du Sud-Ouest camerounais.',
                'price': 600,
                'stock_quantity': 40,
                'ingredients': 'Farine de blé, œufs, lait, sucre, huile, chocolat noir camerounais, beurre.',
                'is_featured': True
            },
            {
                'name': 'Crêpe aux Fruits Tropicaux',
                'description': 'Crêpe garnie d\'un assortiment de fruits tropicaux frais du Cameroun : banane, '
                              'ananas et papaye, nappée de sirop de sucre de canne.',
                'price': 650,
                'stock_quantity': 35,
                'ingredients': 'Farine de blé, œufs, lait, sucre, huile, banane, ananas, papaye, sirop de sucre de canne.',
                'is_featured': False
            },
            {
                'name': 'Crêpe Salée au Poulet',
                'description': 'Crêpe salée garnie de poulet épicé préparé à la camerounaise, avec poivrons et oignons. '
                              'Un repas léger mais complet.',
                'price': 800,
                'stock_quantity': 25,
                'ingredients': 'Farine de blé, œufs, lait, sel, huile, poulet, poivrons, oignons, épices locales.',
                'is_featured': True
            },
            {
                'name': 'Crêpe au Miel et Citron',
                'description': 'Crêpe fine et délicate arrosée de miel d\'abeilles produit localement et '
                              'relevée d\'un filet de jus de citron frais camerounais.',
                'price': 550,
                'stock_quantity': 45,
                'ingredients': 'Farine de blé, œufs, lait, sucre, huile, miel naturel camerounais, citron frais.',
                'is_featured': False
            }
        ]
        
        for crepe in crepes:
            self._create_product(**crepe, category=category)
    
    def _create_pizza_products(self, category):
        # 5 types of pizzas
        pizzas = [
            {
                'name': 'Pizza Ndolè',
                'description': 'Pizza fusion inspirée du plat national camerounais. Base traditionnelle garnie de ndolè '
                              '(feuilles amères), crevettes, viande de bœuf et fromage.',
                'price': 3500,
                'stock_quantity': 15,
                'ingredients': 'Pâte à pizza, sauce tomate, ndolè, crevettes, viande de bœuf, oignons, ail, fromage mozzarella.',
                'is_featured': True
            },
            {
                'name': 'Pizza Poulet DG',
                'description': 'Pizza garnie de poulet préparé façon "Directeur Général" avec des plantains frits, '
                              'carottes et poivrons. Une réinterprétation pizzaïolo d\'un classique camerounais.',
                'price': 3800,
                'stock_quantity': 12,
                'ingredients': 'Pâte à pizza, sauce tomate, poulet mariné aux épices locales, plantains frits, carottes, poivrons, fromage.',
                'is_featured': True
            },
            {
                'name': 'Pizza Tropicale Camerounaise',
                'description': 'Pizza aux saveurs tropicales avec jambon, ananas frais local et fromage. '
                              'Un classique revisité avec des ingrédients de qualité du Cameroun.',
                'price': 3200,
                'stock_quantity': 20,
                'ingredients': 'Pâte à pizza, sauce tomate, jambon, ananas frais du Cameroun, fromage mozzarella, origan.',
                'is_featured': False
            },
            {
                'name': 'Pizza Suya',
                'description': 'Pizza inspirée du populaire "suya" camerounais. Garnie de fines tranches de bœuf '
                              'marinées aux épices suya, oignons et poivrons grillés.',
                'price': 3600,
                'stock_quantity': 15,
                'ingredients': 'Pâte à pizza, sauce tomate, bœuf mariné aux épices suya, oignons, poivrons, fromage.',
                'is_featured': False
            },
            {
                'name': 'Pizza Végétarienne du Marché',
                'description': 'Pizza garnie de légumes frais des marchés locaux : aubergines, poivrons, champignons, '
                              'tomates et oignons, avec un mélange d\'herbes aromatiques camerounaises.',
                'price': 3000,
                'stock_quantity': 18,
                'ingredients': 'Pâte à pizza, sauce tomate, aubergines, poivrons, champignons, tomates fraîches, oignons, herbes locales, fromage.',
                'is_featured': False
            }
        ]
        
        for pizza in pizzas:
            self._create_product(**pizza, category=category)
    
    def _create_nems_products(self, category):
        # 3 types of nems
        nems = [
            {
                'name': 'Nems au Poulet',
                'description': 'Nems croustillants farcis de poulet émincé et légumes, préparés selon une recette '
                              'fusion qui intègre des épices camerounaises traditionnelles.',
                'price': 1500,
                'stock_quantity': 30,
                'ingredients': 'Galettes de riz, poulet émincé, carottes, vermicelles de riz, champignons noirs, oignons verts, épices camerounaises.',
                'is_featured': True
            },
            {
                'name': 'Nems aux Crevettes',
                'description': 'Nems délicats garnis de crevettes fraîches de la côte camerounaise, avec légumes '
                              'croquants et herbes aromatiques. Une spécialité fusion très appréciée.',
                'price': 1800,
                'stock_quantity': 25,
                'ingredients': 'Galettes de riz, crevettes fraîches, carottes, champignons, chou blanc, oignons verts, ail, gingembre.',
                'is_featured': False
            },
            {
                'name': 'Nems Végétariens aux Légumes Locaux',
                'description': 'Version végétarienne des nems, préparée avec un assortiment de légumes frais '
                              'du Cameroun. Légers et savoureux, avec une sauce d\'accompagnement épicée.',
                'price': 1300,
                'stock_quantity': 35,
                'ingredients': 'Galettes de riz, carottes, chou blanc, champignons, vermicelles de riz, oignons verts, gingembre, épices locales.',
                'is_featured': False
            }
        ]
        
        for nem in nems:
            self._create_product(**nem, category=category)
    
    def _create_pile_products(self, category):
        # 10 traditional dishes from west and anglophone regions
        traditional_dishes = [
            {
                'name': 'Achu (Taro Pilé)',
                'description': 'Plat emblématique de la région de l\'Ouest et Nord-Ouest, composé de taro pilé '
                              'servi avec une sauce jaune à l\'huile de palme et viandes variées.',
                'price': 2500,
                'stock_quantity': 20,
                'ingredients': 'Taro, huile de palme, viande de bœuf, tripes, poisson fumé, légumes amers (njama-njama), épices, piment.',
                'is_featured': True
            },
            {
                'name': 'Eru (Waterleaf et Okok)',
                'description': 'Spécialité de la région du Sud-Ouest, ce ragoût associe les feuilles d\'okok finement '
                              'coupées et le waterleaf, accompagnés de viandes et poissons fumés.',
                'price': 2300,
                'stock_quantity': 25,
                'ingredients': 'Okok (Gnetum africanum), waterleaf, huile de palme, viande fumée, poisson fumé, crevettes séchées, piment.',
                'is_featured': True
            },
            {
                'name': 'Koki (Gâteau de Haricots)',
                'description': 'Préparation traditionnelle à base de haricots moulus, cuits à la vapeur dans des '
                              'feuilles de bananier. Un plat typique des régions occidentales du Cameroun.',
                'price': 1500,
                'stock_quantity': 30,
                'ingredients': 'Haricots blancs, huile de palme, oignons, piment, sel, feuilles de bananier pour la cuisson.',
                'is_featured': False
            },
            {
                'name': 'Fufu Corn and Njama-Njama',
                'description': 'Association typique de la cuisine du Nord-Ouest : fufu de maïs (pâte épaisse de farine '
                              'de maïs) servi avec un ragoût de légumes-feuilles amers (njama-njama).',
                'price': 1800,
                'stock_quantity': 25,
                'ingredients': 'Farine de maïs, huckleberry (njama-njama), huile de palme, oignons, tomates, piment, sel, épices.',
                'is_featured': False
            },
            {
                'name': 'Ndolè au Bœuf et Crevettes',
                'description': 'Ragoût national camerounais à base de feuilles amères pilées, agrémenté de bœuf '
                              'et crevettes. Une spécialité incontournable de la côte littoral.',
                'price': 2800,
                'stock_quantity': 18,
                'ingredients': 'Feuilles de ndolè pilées, viande de bœuf, crevettes fraîches, huile de palme, oignons, ail, piment, arachides grillées pilées.',
                'is_featured': True
            },
            {
                'name': 'Pilé de Banane Plantain et Sauce Arachide',
                'description': 'Purée épaisse de bananes plantain pilées, servie avec une sauce onctueuse aux arachides. '
                              'Un plat réconfortant des régions forestières de l\'Ouest et du Sud.',
                'price': 2000,
                'stock_quantity': 22,
                'ingredients': 'Bananes plantain mûres, pâte d\'arachide, tomates, oignons, huile de palme, épices locales, piment.',
                'is_featured': False
            },
            {
                'name': 'Kontchaf (Maïs et Haricots)',
                'description': 'Plat traditionnel bamiléké à base de maïs frais et haricots, cuits longuement '
                              'avec des épices et de l\'huile de palme. Un mets nourrissant et savoureux.',
                'price': 1600,
                'stock_quantity': 28,
                'ingredients': 'Maïs frais, haricots rouges, huile de palme, oignons, tomates, sel, piment.',
                'is_featured': False
            },
            {
                'name': 'Mbongo Tchobi',
                'description': 'Ragoût noir épicé, emblématique de la cuisine du littoral camerounais. Préparé '
                              'avec des épices carbonisées qui lui donnent sa couleur caractéristique.',
                'price': 2400,
                'stock_quantity': 20,
                'ingredients': 'Poisson frais ou viande, mbongo (épices carbonisées), feuilles d\'okok, huile de palme, piment, ail, gingembre.',
                'is_featured': True
            },
            {
                'name': 'Kondre (Banane-Plantain et Viande)',
                'description': 'Ragoût traditionnel associant bananes plantain et viandes variées, mijotés dans '
                              'une sauce à base d\'huile de palme et d\'épices locales.',
                'price': 2200,
                'stock_quantity': 22,
                'ingredients': 'Bananes plantain vertes, viande de bœuf, poisson fumé, huile de palme, tomates, oignons, ail, piment.',
                'is_featured': False
            },
            {
                'name': 'Kwacoco Bible',
                'description': 'Spécialité de la région côtière du Sud-Ouest, ce gâteau de tubercules (manioc et taro) '
                              'est cuit à la vapeur dans des feuilles de bananier avec une sauce aux herbes.',
                'price': 1800,
                'stock_quantity': 25,
                'ingredients': 'Manioc râpé, taro, huile de palme, herbes locales, poisson fumé, crevettes séchées, piment, feuilles de bananier.',
                'is_featured': False
            }
        ]
        
        for dish in traditional_dishes:
            self._create_product(**dish, category=category)
    
    def _create_cake_products(self, category):
        # 10 types of cakes
        cakes = [
            {
                'name': 'Gâteau au Yaourt et Fruits Tropicaux',
                'description': 'Gâteau moelleux préparé avec du yaourt artisanal camerounais et garni de fruits '
                              'tropicaux frais. Léger et parfumé, idéal pour le dessert.',
                'price': 5000,
                'stock_quantity': 10,
                'ingredients': 'Farine, yaourt nature artisanal, œufs, sucre, huile, levure, fruits tropicaux (ananas, mangue, fruit de la passion).',
                'is_featured': True
            },
            {
                'name': 'Gâteau au Chocolat Noir du Cameroun',
                'description': 'Gâteau riche et fondant préparé avec du cacao fin d\'origine camerounaise. '
                              'Un délice pour les amateurs de chocolat intense.',
                'price': 5500,
                'stock_quantity': 8,
                'ingredients': 'Farine, œufs, sucre, beurre, chocolat noir du Cameroun (70% cacao), levure chimique.',
                'is_featured': True
            },
            {
                'name': 'Cake aux Bananes Plantain',
                'description': 'Cake moelleux et parfumé, préparé avec des bananes plantain bien mûres. '
                              'Une réinterprétation locale du banana bread, avec des notes caramélisées.',
                'price': 4500,
                'stock_quantity': 12,
                'ingredients': 'Farine, œufs, sucre, huile, bananes plantain mûres, levure, cannelle, muscade.',
                'is_featured': False
            },
            {
                'name': 'Gâteau de Mariage Traditionnel',
                'description': 'Gâteau festif à plusieurs étages, décoré avec élégance. Parfumé à la vanille '
                              'et au rhum, c\'est le dessert incontournable des mariages camerounais.',
                'price': 12000,
                'stock_quantity': 5,
                'ingredients': 'Farine, œufs, sucre, beurre, vanille, rhum, fruits confits, crème au beurre.',
                'is_featured': True
            },
            {
                'name': 'Gâteau au Miel et Arachides',
                'description': 'Gâteau moelleux préparé avec du miel d\'abeilles camerounaises et garni d\'éclats '
                              'd\'arachides grillées. Un mélange sucré-salé irrésistible.',
                'price': 5000,
                'stock_quantity': 10,
                'ingredients': 'Farine, œufs, sucre, miel, beurre, arachides grillées, levure.',
                'is_featured': False
            },
            {
                'name': 'Gâteau à la Noix de Coco',
                'description': 'Gâteau léger et aérien préparé avec de la noix de coco râpée. Parfait pour les amateurs '
                              'de saveurs exotiques et de douceurs sucrées.',
                'price': 4800,
                'stock_quantity': 15,
                'ingredients': 'Farine, œufs, sucre, lait de coco, noix de coco râpée, levure.',
                'is_featured': False
            },
            {
                'name': 'Gâteau au Lait de Caillé',
                'description': 'Gâteau traditionnel préparé avec du lait de caillé, offrant une texture unique '
                              'et un goût légèrement acidulé. Parfait pour le goûter.',
                'price': 5200,
                'stock_quantity': 10,
                'ingredients': 'Farine, œufs, sucre, lait de caillé, levure, vanille.',
                'is_featured': False
            },
            {
                'name': 'Gâteau aux Épices Africaines',
                'description': 'Gâteau parfumé aux épices africaines (cannelle, muscade, gingembre) et garni de fruits '
                              'secs. Un délice réconfortant pour les amateurs de saveurs épicées.',
                'price': 5500,
                'stock_quantity': 8,
                'ingredients': 'Farine, œufs, sucre, beurre, épices africaines, fruits secs (raisins, abricots).',
                'is_featured': True
            },
            {
                'name': 'Gâteau au Café du Cameroun',
                'description': 'Gâteau moelleux préparé avec du café arabica camerounais. Un délice pour '
                              'les amateurs de café, avec une touche locale.',
                               'price': 5300,
                'stock_quantity': 9,
                'ingredients': 'Farine, œufs, sucre, beurre, café arabica du Cameroun, levure, crème au café.',
                'is_featured': False
            },
            {
                'name': 'Gâteau aux Amandes et Citron',
                'description': 'Gâteau raffiné aux amandes avec une touche de citron frais camerounais. '
                              'Texture moelleuse et croûte légèrement croustillante.',
                'price': 5800,
                'stock_quantity': 7,
                'ingredients': 'Farine, œufs, sucre, beurre, amandes en poudre, zeste de citron, jus de citron, levure.',
                'is_featured': True
            }
        ]
        
        for cake in cakes:
            self._create_product(**cake, category=category)
    
    def _create_other_products(self, category):
        # 5 other types of products following the theme
        other_products = [
            {
                'name': 'Beignets de Haricots (Akara)',
                'description': 'Beignets moelleux à base de purée de haricots, frits à l\'huile. '
                              'Une spécialité populaire dans tout le Cameroun, souvent consommée au petit-déjeuner.',
                'price': 300,
                'stock_quantity': 50,
                'ingredients': 'Haricots blancs, oignons, piment, sel, huile de friture.',
                'is_featured': True
            },
            {
                'name': 'Puff-Puff Traditionnel',
                'description': 'Beignets sphériques et moelleux, légèrement sucrés. Une pâtisserie de rue '
                              'très populaire au Cameroun, idéale pour le goûter.',
                'price': 250,
                'stock_quantity': 60,
                'ingredients': 'Farine, sucre, levure, eau, sel, huile de friture, noix de muscade.',
                'is_featured': False
            },
            {
                'name': 'Pain de Singe (Boule de Noix de Coco)',
                'description': 'Confiserie traditionnelle à base de noix de coco râpée et de sucre caramélisé. '
                              'Une douceur croquante très appréciée des enfants et adultes.',
                'price': 400,
                'stock_quantity': 45,
                'ingredients': 'Noix de coco râpée, sucre, eau, vanille.',
                'is_featured': False
            },
            {
                'name': 'Bâtonnets de Manioc Grillés',
                'description': 'Manioc frais coupé en bâtonnets et grillé au charbon de bois. '
                              'Une collation saine et énergétique typique des rues camerounaises.',
                'price': 350,
                'stock_quantity': 55,
                'ingredients': 'Manioc frais, sel (optionnel).',
                'is_featured': False
            },
            {
                'name': 'Miel Naturel d\'Oku',
                'description': 'Miel pur et naturel récolté dans les montagnes d\'Oku, région du Nord-Ouest '
                              'du Cameroun. Un produit d\'exception aux multiples bienfaits.',
                'price': 3500,
                'stock_quantity': 15,
                'ingredients': 'Miel 100% pur.',
                'is_featured': True
            }
        ]
        
        for product in other_products:
            self._create_product(**product, category=category)