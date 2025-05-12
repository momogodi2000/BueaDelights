from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate
from backed.models import Category, Product
import os
from django.core.files import File
from django.conf import settings
import random
from django.utils import translation

class Command(BaseCommand):
    help = 'Create realistic Cameroonian food products in the database (English and French)'

    def handle(self, *args, **options):
        # Create English products
        self.stdout.write('Creating English products...')
        activate('en')
        self._create_all_products()
        
        # Create French products
        self.stdout.write('Creating French products...')
        activate('fr')
        self._create_all_products()
        
        self.stdout.write(self.style.SUCCESS('Successfully created bilingual Cameroonian products!'))

    def _create_all_products(self):
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
        self._create_meals_products(categories['other'])
        self._create_drinks_products(categories['juice'])
        self._create_snacks_products(categories['other'])

    def _create_categories(self):
        categories = {}
        category_choices = [
            ('chips', _('Chips')),
            ('juice', _('Natural Juices')),
            ('yogurt', _('Yogurts')),
            ('croquettes', _('Croquettes')),
            ('caramel', _('Caramels')),
            ('crepes', _('Crepes')),
            ('pizza', _('Pizza')),
            ('nems', _('Spring Rolls')),
            ('pile', _('Pounded Dishes')),
            ('cake', _('Cakes')),
            ('other', _('Other')),
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
        # Check if product already exists in this language
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
        # Chips products in both languages
        chips_products = [
            {
                'en': {
                    'name': 'Sweet Plantain Chips',
                    'description': 'Delicious sweet plantain chips, handmade from ripe plantains. '
                                  'A Cameroonian specialty appreciated as a sweet snack.',
                    'price': 500,  # FCFA
                    'stock_quantity': 50,
                    'ingredients': 'Ripe plantains, red palm oil, cane sugar, pinch of salt.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Chips de Plantain Sucrées',
                    'description': 'Délicieuses chips de plantain sucrées, préparées artisanalement à partir de bananes plantain mûres. '
                                  'Une spécialité camerounaise appréciée comme collation sucrée.',
                    'price': 500,
                    'stock_quantity': 50,
                    'ingredients': 'Plantains mûrs, huile de palme rouge, sucre de canne, une pincée de sel.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Unsweetened Plantain Chips',
                    'description': 'Plain plantain chips, crispy and light. Prepared according to Cameroonian tradition '
                                  'with barely ripe plantains for an authentic taste.',
                    'price': 450,
                    'stock_quantity': 75,
                    'ingredients': 'Green plantains, vegetable oil, pinch of salt.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Chips de Plantain Nature',
                    'description': 'Chips de plantain nature, croustillantes et légères. Préparées selon la tradition camerounaise '
                                  'avec des plantains à peine mûrs pour un goût authentique.',
                    'price': 450,
                    'stock_quantity': 75,
                    'ingredients': 'Plantains verts, huile végétale, une pincée de sel.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Spicy Cassava Chips',
                    'description': 'Crispy chips made from fresh cassava, lightly spiced. A popular local alternative '
                                  'to potato chips, typical of Cameroon.',
                    'price': 600,
                    'stock_quantity': 40,
                    'ingredients': 'Fresh cassava, palm oil, salt, spices.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Chips de Manioc Épicées',
                    'description': 'Chips croustillantes à base de manioc frais, légèrement épicées. Une alternative locale '
                                  'populaire aux chips de pomme de terre, typique du Cameroun.',
                    'price': 600,
                    'stock_quantity': 40,
                    'ingredients': 'Manioc frais, huile de palme, sel, épices.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Sweet Potato Chips',
                    'description': 'Delicious crispy chips made from Cameroonian sweet potatoes with a touch of cinnamon.',
                    'price': 550,
                    'stock_quantity': 35,
                    'ingredients': 'Sweet potatoes, vegetable oil, cinnamon, salt.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Chips de Patate Douce',
                    'description': 'Délicieuses chips croustillantes à base de patates douces camerounaises avec une touche de cannelle.',
                    'price': 550,
                    'stock_quantity': 35,
                    'ingredients': 'Patates douces, huile végétale, cannelle, sel.',
                    'is_featured': False
                }
            }
        ]
        
        current_language = translation.get_language()
        for product_data in chips_products:
            self._create_product(**product_data[current_language], category=category)
    
    def _create_juice_products(self, category):
        # Juice products in both languages
        juice_products = [
            {
                'en': {
                    'name': 'Fresh Ginger Juice',
                    'description': 'Spicy ginger juice prepared with fresh local ginger. A refreshing and energizing drink, traditional in Cameroon.',
                    'price': 800,
                    'stock_quantity': 30,
                    'ingredients': 'Fresh ginger, lemon, honey, filtered water, mint (optional).',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Jus de Gingembre Frais',
                    'description': 'Jus de gingembre piquant préparé avec du gingembre frais local. Une boisson rafraîchissante '
                                  'et énergisante, traditionnelle au Cameroun.',
                    'price': 800,
                    'stock_quantity': 30,
                    'ingredients': 'Gingembre frais, citron, miel, eau filtrée, menthe (optionnel).',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Baobab Juice (Bouye)',
                    'description': 'Creamy and nutritious drink made from baobab fruit. Rich in vitamins and minerals, this juice is prized for its health benefits.',
                    'price': 900,
                    'stock_quantity': 25,
                    'ingredients': 'Baobab fruit pulp, filtered water, cane sugar, condensed milk (optional).',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Jus de Baobab (Bouye)',
                    'description': 'Boisson crémeuse et nutritive à base de fruit de baobab. Riche en vitamines et minéraux, '
                                  'ce jus est prisé pour ses bienfaits sur la santé.',
                    'price': 900,
                    'stock_quantity': 25,
                    'ingredients': 'Pulpe de fruit de baobab, eau filtrée, sucre de canne, lait concentré (optionnel).',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Hibiscus Juice (Bissap)',
                    'description': 'Bright red drink prepared from dried hibiscus flowers. Refreshing with a tangy note, very popular during celebrations.',
                    'price': 750,
                    'stock_quantity': 45,
                    'ingredients': 'Dried hibiscus flowers, filtered water, sugar, pineapple juice, fresh mint.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Jus de Bissap (Hibiscus)',
                    'description': 'Boisson rouge vif préparée à partir de fleurs d\'hibiscus séchées. Rafraîchissante avec '
                                  'une note acidulée, très populaire pendant les fêtes.',
                    'price': 750,
                    'stock_quantity': 45,
                    'ingredients': 'Fleurs d\'hibiscus séchées, eau filtrée, sucre, jus d\'ananas, menthe fraîche.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Foléré Juice',
                    'description': 'Traditional version of hibiscus juice, prepared according to a recipe from Northern Cameroon, with a slightly spicy flavor.',
                    'price': 800,
                    'stock_quantity': 35,
                    'ingredients': 'Roselle flowers (folere), filtered water, sugar, cloves, ginger.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Jus de Foléré',
                    'description': 'Version traditionnelle du jus d\'hibiscus, préparée selon une recette du Nord Cameroun, '
                                  'avec une saveur légèrement épicée.',
                    'price': 800,
                    'stock_quantity': 35,
                    'ingredients': 'Fleurs de roselle (folere), eau filtrée, sucre, clous de girofle, gingembre.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Tropical Fruit Cocktail',
                    'description': 'Refreshing blend of juices extracted from fresh Cameroonian tropical fruits. An explosion of exotic flavors in every sip.',
                    'price': 1000,
                    'stock_quantity': 20,
                    'ingredients': 'Pineapple, papaya, guava, passion fruit, banana, cane sugar (as needed).',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Cocktail de Fruits Tropicaux',
                    'description': 'Mélange rafraîchissant de jus extraits de fruits tropicaux camerounais frais. '
                                  'Une explosion de saveurs exotiques dans chaque gorgée.',
                    'price': 1000,
                    'stock_quantity': 20,
                    'ingredients': 'Ananas, papaye, goyave, fruit de la passion, banane, sucre de canne (selon besoin).',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Mango Juice',
                    'description': 'Sweet and refreshing juice made from ripe Cameroonian mangoes, rich in vitamins and natural sweetness.',
                    'price': 850,
                    'stock_quantity': 30,
                    'ingredients': 'Fresh mangoes, filtered water, sugar (optional).',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Jus de Mangue',
                    'description': 'Jus sucré et rafraîchissant à base de mangues camerounaises mûres, riche en vitamines et en douceur naturelle.',
                    'price': 850,
                    'stock_quantity': 30,
                    'ingredients': 'Mangues fraîches, eau filtrée, sucre (optionnel).',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Pineapple-Ginger Juice',
                    'description': 'Energizing blend of sweet pineapple and spicy ginger, a popular combination in Cameroon for digestion and energy.',
                    'price': 900,
                    'stock_quantity': 25,
                    'ingredients': 'Fresh pineapple, ginger, filtered water, sugar, mint.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Jus Ananas-Gingembre',
                    'description': 'Mélange énergisant d\'ananas sucré et de gingembre piquant, une combinaison populaire au Cameroun pour la digestion et l\'énergie.',
                    'price': 900,
                    'stock_quantity': 25,
                    'ingredients': 'Ananas frais, gingembre, eau filtrée, sucre, menthe.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for juice in juice_products:
            self._create_product(**juice[current_language], category=category)
    
    def _create_yogurt_products(self, category):
        # Yogurt products in both languages
        yogurt_products = [
            {
                'en': {
                    'name': 'Plain Artisanal Yogurt',
                    'description': 'Creamy plain yogurt traditionally prepared, slightly tangy and smooth. Made with fresh milk from local farms.',
                    'price': 600,
                    'stock_quantity': 40,
                    'ingredients': 'Fresh whole milk, live lactic ferments.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Yaourt Nature Artisanal',
                    'description': 'Yaourt crémeux nature préparé traditionnellement, légèrement acidulé et onctueux. '
                                  'Fabriqué avec du lait frais de fermes locales.',
                    'price': 600,
                    'stock_quantity': 40,
                    'ingredients': 'Lait entier frais, ferments lactiques vivants.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Sweet Vanilla Yogurt',
                    'description': 'Soft and creamy yogurt flavored with natural vanilla. A sweetness appreciated by all dairy lovers.',
                    'price': 650,
                    'stock_quantity': 35,
                    'ingredients': 'Fresh whole milk, lactic ferments, sugar, natural vanilla extract.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Yaourt Sucré à la Vanille',
                    'description': 'Yaourt doux et crémeux parfumé à la vanille naturelle. Une douceur appréciée '
                                  'de tous les amateurs de produits laitiers.',
                    'price': 650,
                    'stock_quantity': 35,
                    'ingredients': 'Lait entier frais, ferments lactiques, sucre, extrait naturel de vanille.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Honey and Almond Yogurt',
                    'description': 'Yogurt delicately sweetened with honey from Cameroonian bees and garnished with almond pieces. A perfect blend of sweetness and crunch.',
                    'price': 750,
                    'stock_quantity': 25,
                    'ingredients': 'Fresh whole milk, lactic ferments, natural honey, crushed almonds.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Yaourt Miel et Amandes',
                    'description': 'Yaourt délicatement sucré au miel d\'abeilles camerounaises et garni d\'éclats d\'amandes. '
                                  'Un mélange parfait de douceur et de croquant.',
                    'price': 750,
                    'stock_quantity': 25,
                    'ingredients': 'Lait entier frais, ferments lactiques, miel naturel, amandes concassées.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Passion Fruit Yogurt',
                    'description': 'Creamy yogurt with pieces of passion fruit. Its exotic and tangy taste will transport you to the heart of Cameroonian flavors.',
                    'price': 700,
                    'stock_quantity': 30,
                    'ingredients': 'Fresh whole milk, lactic ferments, passion fruit, cane sugar.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Yaourt aux Fruits de la Passion',
                    'description': 'Yaourt onctueux agrémenté de morceaux de fruits de la passion. Son goût exotique '
                                  'et acidulé vous transportera au cœur des saveurs camerounaises.',
                    'price': 700,
                    'stock_quantity': 30,
                    'ingredients': 'Lait entier frais, ferments lactiques, fruits de la passion, sucre de canne.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Papaya Yogurt',
                    'description': 'Fruity yogurt with fresh papaya, soft and slightly sweet. A local specialty that celebrates one of the most cultivated fruits in Cameroon.',
                    'price': 700,
                    'stock_quantity': 30,
                    'ingredients': 'Fresh whole milk, lactic ferments, fresh papaya puree, sugar.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Yaourt à la Papaye',
                    'description': 'Yaourt fruité à la papaye fraîche, doux et légèrement sucré. Une spécialité locale '
                                  'qui célèbre l\'un des fruits les plus cultivés au Cameroun.',
                    'price': 700,
                    'stock_quantity': 30,
                    'ingredients': 'Lait entier frais, ferments lactiques, purée de papaye fraîche, sucre.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Mango Yogurt',
                    'description': 'Creamy yogurt with pieces of juicy mango. A tropical delight that will remind you of Cameroon\'s lush orchards.',
                    'price': 750,
                    'stock_quantity': 25,
                    'ingredients': 'Fresh whole milk, lactic ferments, fresh mango pieces, sugar.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Yaourt à la Mangue',
                    'description': 'Yaourt crémeux aux morceaux de mangue juteuse. Un délice tropical qui vous '
                                  'rappellera les vergers luxuriants du Cameroun.',
                    'price': 750,
                    'stock_quantity': 25,
                    'ingredients': 'Lait entier frais, ferments lactiques, morceaux de mangue fraîche, sucre.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Strawberry Yogurt',
                    'description': 'Delicious yogurt with fresh strawberry puree, a special treat made with local strawberries from the West region.',
                    'price': 800,
                    'stock_quantity': 20,
                    'ingredients': 'Fresh whole milk, lactic ferments, strawberry puree, sugar.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Yaourt à la Fraise',
                    'description': 'Délicieux yaourt à la purée de fraises fraîches, une spécialité préparée avec des fraises locales de la région de l\'Ouest.',
                    'price': 800,
                    'stock_quantity': 20,
                    'ingredients': 'Lait entier frais, ferments lactiques, purée de fraises, sucre.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for yogurt in yogurt_products:
            self._create_product(**yogurt[current_language], category=category)
    
    def _create_croquettes_products(self, category):
        # Croquettes products in both languages
        croquettes_products = [
            {
                'en': {
                    'name': 'Cassava Croquettes',
                    'description': 'Crispy croquettes made from grated cassava and local spices. A popular snack throughout Cameroon, perfect for appetizers.',
                    'price': 700,
                    'stock_quantity': 40,
                    'ingredients': 'Grated cassava, onions, bell peppers, chili, salt, frying oil.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Croquettes de Manioc',
                    'description': 'Croquettes croustillantes à base de manioc râpé et d\'épices locales. '
                                  'Un en-cas populaire dans tout le Cameroun, parfait pour l\'apéritif.',
                    'price': 700,
                    'stock_quantity': 40,
                    'ingredients': 'Manioc râpé, oignons, poivrons, piment, sel, huile pour friture.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Cameroonian-Style Fish Croquettes',
                    'description': 'Delicious croquettes prepared with fresh local fish and seasoned with traditional Cameroonian spices.',
                    'price': 850,
                    'stock_quantity': 30,
                    'ingredients': 'Fresh fish fillet, onions, garlic, parsley, chili, flour, eggs, oil.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Croquettes de Poisson à la Camerounaise',
                    'description': 'Délicieuses croquettes préparées avec du poisson local frais et assaisonnées '
                                  'avec des épices traditionnelles camerounaises.',
                    'price': 850,
                    'stock_quantity': 30,
                    'ingredients': 'Filet de poisson frais, oignons, ail, persil, piment, farine, œufs, huile.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Bean Fritters (Koki)',
                    'description': 'Cameroonian version of fritters, made with ground white beans. Crispy outside and soft inside.',
                    'price': 750,
                    'stock_quantity': 35,
                    'ingredients': 'White beans, onions, palm oil, chili, salt, natural broth.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Accras de Haricots (Koki)',
                    'description': 'Version camerounaise des accras, préparée à base de haricots blancs moulus. '
                                  'Croustillantes à l\'extérieur et moelleuses à l\'intérieur.',
                    'price': 750,
                    'stock_quantity': 35,
                    'ingredients': 'Haricots blancs, oignons, huile de palme, piment, sel, bouillon naturel.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Chicken and Vegetable Croquettes',
                    'description': 'Tasty croquettes made with minced chicken and fresh vegetables, a popular snack in Yaoundé markets.',
                    'price': 900,
                    'stock_quantity': 25,
                    'ingredients': 'Chicken, carrots, potatoes, onions, flour, eggs, spices, frying oil.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Croquettes de Poulet et Légumes',
                    'description': 'Savoureuses croquettes à base de poulet haché et de légumes frais, un en-cas populaire dans les marchés de Yaoundé.',
                    'price': 900,
                    'stock_quantity': 25,
                    'ingredients': 'Poulet, carottes, pommes de terre, oignons, farine, œufs, épices, huile de friture.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for croquette in croquettes_products:
            self._create_product(**croquette[current_language], category=category)
    
    def _create_caramel_products(self, category):
        # Caramel products in both languages
        caramel_products = [
            {
                'en': {
                    'name': 'Vanilla Caramels',
                    'description': 'Artisanal caramels flavored with natural vanilla, prepared according to a traditional Cameroonian recipe. Smooth texture and intense flavor.',
                    'price': 550,
                    'stock_quantity': 60,
                    'ingredients': 'Cane sugar, condensed milk, butter, natural vanilla extract, pinch of salt.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Caramels à la Vanille',
                    'description': 'Caramels artisanaux parfumés à la vanille naturelle, préparés selon une recette '
                                  'traditionnelle camerounaise. Texture lisse et saveur intense.',
                    'price': 550,
                    'stock_quantity': 60,
                    'ingredients': 'Sucre de canne, lait concentré, beurre, extrait naturel de vanille, une pincée de sel.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Chocolate Caramels',
                    'description': 'Rich caramels with Cameroonian cocoa, a perfect blend of sweet and bitter flavors from local ingredients.',
                    'price': 650,
                    'stock_quantity': 45,
                    'ingredients': 'Cane sugar, condensed milk, butter, Cameroonian cocoa, vanilla, salt.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Caramels au Chocolat',
                    'description': 'Caramels riches en cacao camerounais, un mélange parfait de saveurs sucrées et amères à partir d\'ingrédients locaux.',
                    'price': 650,
                    'stock_quantity': 45,
                    'ingredients': 'Sucre de canne, lait concentré, beurre, cacao camerounais, vanille, sel.',
                    'is_featured': False
                }
            }
        ]
        
        current_language = translation.get_language()
        for caramel in caramel_products:
            self._create_product(**caramel[current_language], category=category)
    
    def _create_crepes_products(self, category):
        # Crepes products in both languages
        crepes_products = [
            {
                'en': {
                    'name': 'Simple Traditional Crepe',
                    'description': 'Thin and light crepe prepared according to Cameroonian tradition. Perfect for sweet or savory fillings.',
                    'price': 400,
                    'stock_quantity': 50,
                    'ingredients': 'Wheat flour, eggs, milk, sugar, oil, pinch of salt.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Crêpe Simple Traditionnelle',
                    'description': 'Crêpe fine et légère préparée selon la tradition camerounaise. '
                                  'Parfaite pour accueillir garnitures sucrées ou salées.',
                    'price': 400,
                    'stock_quantity': 50,
                    'ingredients': 'Farine de blé, œufs, lait, sucre, huile, une pincée de sel.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Dark Chocolate Crepe',
                    'description': 'Delicious crepe filled with melted dark chocolate, prepared from cocoa beans locally grown in Cameroon\'s Southwest regions.',
                    'price': 600,
                    'stock_quantity': 40,
                    'ingredients': 'Wheat flour, eggs, milk, sugar, oil, Cameroonian dark chocolate, butter.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Crêpe au Chocolat Noir',
                    'description': 'Délicieuse crêpe garnie de chocolat noir fondu, préparé à partir de fèves de cacao '
                                  'cultivées localement dans les régions du Sud-Ouest camerounais.',
                    'price': 600,
                    'stock_quantity': 40,
                    'ingredients': 'Farine de blé, œufs, lait, sucre, huile, chocolat noir camerounais, beurre.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Tropical Fruit Crepe',
                    'description': 'Crepe filled with an assortment of fresh tropical fruits from Cameroon: banana, pineapple and papaya, drizzled with cane sugar syrup.',
                    'price': 650,
                    'stock_quantity': 35,
                    'ingredients': 'Wheat flour, eggs, milk, sugar, oil, banana, pineapple, papaya, cane sugar syrup.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Crêpe aux Fruits Tropicaux',
                    'description': 'Crêpe garnie d\'un assortiment de fruits tropicaux frais du Cameroun : banane, '
                                  'ananas et papaye, nappée de sirop de sucre de canne.',
                    'price': 650,
                    'stock_quantity': 35,
                    'ingredients': 'Farine de blé, œufs, lait, sucre, huile, banane, ananas, papaye, sirop de sucre de canne.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Chicken Spicy Crepe',
                    'description': 'Savory crepe filled with chicken prepared Cameroonian-style, with bell peppers and onions. A light but complete meal.',
                    'price': 800,
                    'stock_quantity': 25,
                    'ingredients': 'Wheat flour, eggs, milk, salt, oil, chicken, bell peppers, onions, local spices.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Crêpe Salée au Poulet',
                    'description': 'Crêpe salée garnie de poulet épicé préparé à la camerounaise, avec poivrons et oignons. '
                                  'Un repas léger mais complet.',
                    'price': 800,
                    'stock_quantity': 25,
                    'ingredients': 'Farine de blé, œufs, lait, sel, huile, poulet, poivrons, oignons, épices locales.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Honey and Lemon Crepe',
                    'description': 'Delicate thin crepe drizzled with honey from locally produced bees and a dash of fresh Cameroonian lemon juice.',
                    'price': 550,
                    'stock_quantity': 45,
                    'ingredients': 'Wheat flour, eggs, milk, sugar, oil, natural Cameroonian honey, fresh lemon.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Crêpe au Miel et Citron',
                    'description': 'Crêpe fine et délicate arrosée de miel d\'abeilles produit localement et '
                                  'relevée d\'un filet de jus de citron frais camerounais.',
                    'price': 550,
                    'stock_quantity': 45,
                    'ingredients': 'Farine de blé, œufs, lait, sucre, huile, miel naturel camerounais, citron frais.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Peanut Butter Crepe',
                    'description': 'Traditional crepe filled with rich Cameroonian peanut butter, a popular street food in the northern regions.',
                    'price': 500,
                    'stock_quantity': 40,
                    'ingredients': 'Wheat flour, eggs, milk, sugar, oil, local peanut butter, honey (optional).',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Crêpe à la Pâte d\'Arachide',
                    'description': 'Crêpe traditionnelle garnie de riche pâte d\'arachide camerounaise, un en-cas de rue populaire dans les régions du nord.',
                    'price': 500,
                    'stock_quantity': 40,
                    'ingredients': 'Farine de blé, œufs, lait, sucre, huile, pâte d\'arachide locale, miel (optionnel).',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for crepe in crepes_products:
            self._create_product(**crepe[current_language], category=category)
    
    def _create_pizza_products(self, category):
        # Pizza products in both languages
        pizza_products = [
            {
                'en': {
                    'name': 'Ndolè Pizza',
                    'description': 'Fusion pizza inspired by the Cameroonian national dish. Traditional base topped with ndolè (bitter leaves), shrimp, beef and cheese.',
                    'price': 3500,
                    'stock_quantity': 15,
                    'ingredients': 'Pizza dough, tomato sauce, ndolè, shrimp, beef, onions, garlic, mozzarella cheese.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Pizza Ndolè',
                    'description': 'Pizza fusion inspirée du plat national camerounais. Base traditionnelle garnie de ndolè '
                                  '(feuilles amères), crevettes, viande de bœuf et fromage.',
                    'price': 3500,
                    'stock_quantity': 15,
                    'ingredients': 'Pâte à pizza, sauce tomate, ndolè, crevettes, viande de bœuf, oignons, ail, fromage mozzarella.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Poulet DG Pizza',
                    'description': 'Pizza topped with chicken prepared "Directeur Général" style with fried plantains, carrots and bell peppers. A pizzaiolo reinterpretation of a Cameroonian classic.',
                    'price': 3800,
                    'stock_quantity': 12,
                    'ingredients': 'Pizza dough, tomato sauce, chicken marinated with local spices, fried plantains, carrots, bell peppers, cheese.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Pizza Poulet DG',
                    'description': 'Pizza garnie de poulet préparé façon "Directeur Général" avec des plantains frits, '
                                  'carottes et poivrons. Une réinterprétation pizzaïolo d\'un classique camerounais.',
                    'price': 3800,
                    'stock_quantity': 12,
                    'ingredients': 'Pâte à pizza, sauce tomate, poulet mariné aux épices locales, plantains frits, carottes, poivrons, fromage.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Cameroonian Tropical Pizza',
                    'description': 'Pizza with tropical flavors featuring ham, fresh local pineapple and cheese. A classic revisited with quality ingredients from Cameroon.',
                    'price': 3200,
                    'stock_quantity': 20,
                    'ingredients': 'Pizza dough, tomato sauce, ham, fresh Cameroonian pineapple, mozzarella cheese, oregano.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Pizza Tropicale Camerounaise',
                    'description': 'Pizza aux saveurs tropicales avec jambon, ananas frais local et fromage. '
                                  'Un classique revisité avec des ingrédients de qualité du Cameroun.',
                    'price': 3200,
                    'stock_quantity': 20,
                    'ingredients': 'Pâte à pizza, sauce tomate, jambon, ananas frais du Cameroun, fromage mozzarella, origan.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Suya Pizza',
                    'description': 'Pizza inspired by the popular Cameroonian "suya". Topped with thin slices of beef marinated in suya spices, grilled onions and bell peppers.',
                    'price': 3600,
                    'stock_quantity': 15,
                    'ingredients': 'Pizza dough, tomato sauce, beef marinated in suya spices, onions, bell peppers, cheese.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Pizza Suya',
                    'description': 'Pizza inspirée du populaire "suya" camerounais. Garnie de fines tranches de bœuf '
                                  'marinées aux épices suya, oignons et poivrons grillés.',
                    'price': 3600,
                    'stock_quantity': 15,
                    'ingredients': 'Pâte à pizza, sauce tomate, bœuf mariné aux épices suya, oignons, poivrons, fromage.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Market Vegetarian Pizza',
                    'description': 'Pizza topped with fresh vegetables from local markets: eggplants, bell peppers, mushrooms, tomatoes and onions, with a blend of Cameroonian aromatic herbs.',
                    'price': 3000,
                    'stock_quantity': 18,
                    'ingredients': 'Pizza dough, tomato sauce, eggplants, bell peppers, mushrooms, fresh tomatoes, onions, local herbs, cheese.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Pizza Végétarienne du Marché',
                    'description': 'Pizza garnie de légumes frais des marchés locaux : aubergines, poivrons, champignons, '
                                  'tomates et oignons, avec un mélange d\'herbes aromatiques camerounaises.',
                    'price': 3000,
                    'stock_quantity': 18,
                    'ingredients': 'Pâte à pizza, sauce tomate, aubergines, poivrons, champignons, tomates fraîches, oignons, herbes locales, fromage.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Seafood Pizza',
                    'description': 'Delicious pizza with fresh seafood from the Cameroonian coast: shrimp, squid and fish, with a special sauce.',
                    'price': 4000,
                    'stock_quantity': 12,
                    'ingredients': 'Pizza dough, tomato sauce, shrimp, squid, fish fillet, onions, garlic, parsley, cheese.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Pizza aux Fruits de Mer',
                    'description': 'Délicieuse pizza aux fruits de mer frais de la côte camerounaise : crevettes, calmar et poisson, avec une sauce spéciale.',
                    'price': 4000,
                    'stock_quantity': 12,
                    'ingredients': 'Pâte à pizza, sauce tomate, crevettes, calmar, filet de poisson, oignons, ail, persil, fromage.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for pizza in pizza_products:
            self._create_product(**pizza[current_language], category=category)
    
    def _create_nems_products(self, category):
        # Spring rolls products in both languages
        nems_products = [
            {
                'en': {
                    'name': 'Chicken Spring Rolls',
                    'description': 'Crispy spring rolls stuffed with minced chicken and vegetables, prepared according to a fusion recipe that incorporates traditional Cameroonian spices.',
                    'price': 1500,
                    'stock_quantity': 30,
                    'ingredients': 'Rice paper, minced chicken, carrots, rice vermicelli, black mushrooms, green onions, Cameroonian spices.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Nems au Poulet',
                    'description': 'Nems croustillants farcis de poulet émincé et légumes, préparés selon une recette '
                                  'fusion qui intègre des épices camerounaises traditionnelles.',
                    'price': 1500,
                    'stock_quantity': 30,
                    'ingredients': 'Galettes de riz, poulet émincé, carottes, vermicelles de riz, champignons noirs, oignons verts, épices camerounaises.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Shrimp Spring Rolls',
                    'description': 'Delicate spring rolls stuffed with fresh shrimp from the Cameroonian coast, with crunchy vegetables and aromatic herbs. A very appreciated fusion specialty.',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Rice paper, fresh shrimp, carrots, mushrooms, white cabbage, green onions, garlic, ginger.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Nems aux Crevettes',
                    'description': 'Nems délicats garnis de crevettes fraîches de la côte camerounaise, avec légumes '
                                  'croquants et herbes aromatiques. Une spécialité fusion très appréciée.',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Galettes de riz, crevettes fraîches, carottes, champignons, chou blanc, oignons verts, ail, gingembre.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Vegetable Spring Rolls with Local Vegetables',
                    'description': 'Vegetarian version of spring rolls, prepared with an assortment of fresh vegetables from Cameroon. Light and flavorful, with a spicy dipping sauce.',
                    'price': 1300,
                    'stock_quantity': 35,
                    'ingredients': 'Rice paper, carrots, white cabbage, mushrooms, rice vermicelli, green onions, ginger, local spices.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Nems Végétariens aux Légumes Locaux',
                    'description': 'Version végétarienne des nems, préparée avec un assortiment de légumes frais '
                                  'du Cameroun. Légers et savoureux, avec une sauce d\'accompagnement épicée.',
                    'price': 1300,
                    'stock_quantity': 35,
                    'ingredients': 'Galettes de riz, carottes, chou blanc, champignons, vermicelles de riz, oignons verts, gingembre, épices locales.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Beef and Mushroom Spring Rolls',
                    'description': 'Rich spring rolls filled with tender beef and local mushrooms, a specialty from the West region of Cameroon.',
                    'price': 1700,
                    'stock_quantity': 20,
                    'ingredients': 'Rice paper, beef, mushrooms, carrots, onions, garlic, soy sauce, spices.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Nems au Bœuf et Champignons',
                    'description': 'Nems riches garnis de bœuf tendre et de champignons locaux, une spécialité de la région de l\'Ouest du Cameroun.',
                    'price': 1700,
                    'stock_quantity': 20,
                    'ingredients': 'Galettes de riz, bœuf, champignons, carottes, oignons, ail, sauce soja, épices.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for nem in nems_products:
            self._create_product(**nem[current_language], category=category)
    
    def _create_pile_products(self, category):
        # Traditional dishes in both languages
        traditional_dishes = [
            {
                'en': {
                    'name': 'Achu (Pounded Taro)',
                    'description': 'Iconic dish from the West and Northwest regions, consisting of pounded taro served with a yellow palm oil sauce and various meats.',
                    'price': 2500,
                    'stock_quantity': 20,
                    'ingredients': 'Taro, palm oil, beef, tripe, smoked fish, bitter vegetables (njama-njama), spices, chili.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Achu (Taro Pilé)',
                    'description': 'Plat emblématique de la région de l\'Ouest et Nord-Ouest, composé de taro pilé '
                                  'servi avec une sauce jaune à l\'huile de palme et viandes variées.',
                    'price': 2500,
                    'stock_quantity': 20,
                    'ingredients': 'Taro, huile de palme, viande de bœuf, tripes, poisson fumé, légumes amers (njama-njama), épices, piment.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Eru (Waterleaf and Okok)',
                    'description': 'Specialty from the Southwest region, this stew combines finely chopped okok leaves and waterleaf, accompanied by smoked meats and fish.',
                    'price': 2300,
                    'stock_quantity': 25,
                    'ingredients': 'Okok (Gnetum africanum), waterleaf, palm oil, smoked meat, smoked fish, dried shrimp, chili.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Eru (Waterleaf et Okok)',
                    'description': 'Spécialité de la région du Sud-Ouest, ce ragoût associe les feuilles d\'okok finement '
                                  'coupées et le waterleaf, accompagnés de viandes et poissons fumés.',
                    'price': 2300,
                    'stock_quantity': 25,
                    'ingredients': 'Okok (Gnetum africanum), waterleaf, huile de palme, viande fumée, poisson fumé, crevettes séchées, piment.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Koki (Bean Cake)',
                    'description': 'Traditional preparation made from ground beans, steamed in banana leaves. A typical dish from western regions of Cameroon.',
                    'price': 1500,
                    'stock_quantity': 30,
                    'ingredients': 'White beans, palm oil, onions, chili, salt, banana leaves for cooking.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Koki (Gâteau de Haricots)',
                    'description': 'Préparation traditionnelle à base de haricots moulus, cuits à la vapeur dans des '
                                  'feuilles de bananier. Un plat typique des régions occidentales du Cameroun.',
                    'price': 1500,
                    'stock_quantity': 30,
                    'ingredients': 'Haricots blancs, huile de palme, oignons, piment, sel, feuilles de bananier pour la cuisson.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Fufu Corn and Njama-Njama',
                    'description': 'Typical combination from Northwest cuisine: corn fufu (thick maize flour paste) served with a stew of bitter leafy vegetables (njama-njama).',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Corn flour, huckleberry (njama-njama), palm oil, onions, tomatoes, chili, salt, spices.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Fufu de Maïs et Njama-Njama',
                    'description': 'Association typique de la cuisine du Nord-Ouest : fufu de maïs (pâte épaisse de farine '
                                  'de maïs) servi avec un ragoût de légumes-feuilles amers (njama-njama).',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Farine de maïs, huckleberry (njama-njama), huile de palme, oignons, tomates, piment, sel, épices.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Ndolè with Beef and Shrimp',
                    'description': 'Cameroonian national stew made with pounded bitter leaves, enhanced with beef and shrimp. An essential specialty from the coastal region.',
                    'price': 2800,
                    'stock_quantity': 18,
                    'ingredients': 'Pounded ndolè leaves, beef, fresh shrimp, palm oil, onions, garlic, chili, crushed roasted peanuts.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Ndolè au Bœuf et Crevettes',
                    'description': 'Ragoût national camerounais à base de feuilles amères pilées, agrémenté de bœuf '
                                  'et crevettes. Une spécialité incontournable de la côte littoral.',
                    'price': 2800,
                    'stock_quantity': 18,
                    'ingredients': 'Feuilles de ndolè pilées, viande de bœuf, crevettes fraîches, huile de palme, oignons, ail, piment, arachides grillées pilées.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Pounded Plantain with Peanut Sauce',
                    'description': 'Thick puree of pounded plantains, served with a creamy peanut sauce. A comforting dish from the forest regions of the West and South.',
                    'price': 2000,
                    'stock_quantity': 22,
                    'ingredients': 'Ripe plantains, peanut paste, tomatoes, onions, palm oil, local spices, chili.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Pilé de Banane Plantain et Sauce Arachide',
                    'description': 'Purée épaisse de bananes plantain pilées, servie avec une sauce onctueuse aux arachides. '
                                  'Un plat réconfortant des régions forestières de l\'Ouest et du Sud.',
                    'price': 2000,
                    'stock_quantity': 22,
                    'ingredients': 'Bananes plantain mûres, pâte d\'arachide, tomates, oignons, huile de palme, épices locales, piment.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Kontchaf (Corn and Beans)',
                    'description': 'Traditional Bamiléké dish made from fresh corn and beans, cooked for a long time with spices and palm oil. A nourishing and flavorful dish.',
                    'price': 1600,
                    'stock_quantity': 28,
                    'ingredients': 'Fresh corn, red beans, palm oil, onions, tomatoes, salt, chili.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Kontchaf (Maïs et Haricots)',
                    'description': 'Plat traditionnel bamiléké à base de maïs frais et haricots, cuits longuement '
                                  'avec des épices et de l\'huile de palme. Un mets nourrissant et savoureux.',
                    'price': 1600,
                    'stock_quantity': 28,
                    'ingredients': 'Maïs frais, haricots rouges, huile de palme, oignons, tomates, sel, piment.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Mbongo Tchobi',
                    'description': 'Spicy black stew, emblematic of Cameroonian coastal cuisine. Prepared with carbonized spices that give it its characteristic color.',
                    'price': 2400,
                    'stock_quantity': 20,
                    'ingredients': 'Fresh fish or meat, mbongo (carbonized spices), okok leaves, palm oil, chili, garlic, ginger.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Mbongo Tchobi',
                    'description': 'Ragoût noir épicé, emblématique de la cuisine du littoral camerounais. Préparé '
                                  'avec des épices carbonisées qui lui donnent sa couleur caractéristique.',
                    'price': 2400,
                    'stock_quantity': 20,
                    'ingredients': 'Poisson frais ou viande, mbongo (épices carbonisées), feuilles d\'okok, huile de palme, piment, ail, gingembre.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Kondre (Plantain and Meat)',
                    'description': 'Traditional stew combining plantains and various meats, simmered in a sauce based on palm oil and local spices.',
                    'price': 2200,
                    'stock_quantity': 22,
                    'ingredients': 'Green plantains, beef, smoked fish, palm oil, tomatoes, onions, garlic, chili.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Kondre (Banane-Plantain et Viande)',
                    'description': 'Ragoût traditionnel associant bananes plantain et viandes variées, mijotés dans '
                                  'une sauce à base d\'huile de palme et d\'épices locales.',
                    'price': 2200,
                    'stock_quantity': 22,
                    'ingredients': 'Bananes plantain vertes, viande de bœuf, poisson fumé, huile de palme, tomates, oignons, ail, piment.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Kwacoco Bible',
                    'description': 'Specialty from the coastal Southwest region, this tuber cake (cassava and taro) is steamed in banana leaves with an herb sauce.',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Grated cassava, taro, palm oil, local herbs, smoked fish, dried shrimp, chili, banana leaves.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Kwacoco Bible',
                    'description': 'Spécialité de la région côtière du Sud-Ouest, ce gâteau de tubercules (manioc et taro) '
                                  'est cuit à la vapeur dans des feuilles de bananier avec une sauce aux herbes.',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Manioc râpé, taro, huile de palme, herbes locales, poisson fumé, crevettes séchées, piment, feuilles de bananier.',
                    'is_featured': False
                }
            }
        ]
        
        current_language = translation.get_language()
        for dish in traditional_dishes:
            self._create_product(**dish[current_language], category=category)
    
    def _create_cake_products(self, category):
        # Cake products in both languages
        cake_products = [
            {
                'en': {
                    'name': 'Yogurt and Tropical Fruit Cake',
                    'description': 'Soft cake prepared with Cameroonian artisanal yogurt and garnished with fresh tropical fruits. Light and fragrant, ideal for dessert.',
                    'price': 5000,
                    'stock_quantity': 10,
                    'ingredients': 'Flour, plain artisanal yogurt, eggs, sugar, oil, yeast, tropical fruits (pineapple, mango, passion fruit).',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Gâteau au Yaourt et Fruits Tropicaux',
                    'description': 'Gâteau moelleux préparé avec du yaourt artisanal camerounais et garni de fruits '
                                  'tropicaux frais. Léger et parfumé, idéal pour le dessert.',
                    'price': 5000,
                    'stock_quantity': 10,
                    'ingredients': 'Farine, yaourt nature artisanal, œufs, sucre, huile, levure, fruits tropicaux (ananas, mangue, fruit de la passion).',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Cameroonian Dark Chocolate Cake',
                    'description': 'Rich and melting cake prepared with fine cocoa of Cameroonian origin. A delight for lovers of intense chocolate.',
                    'price': 5500,
                    'stock_quantity': 8,
                    'ingredients': 'Flour, eggs, sugar, butter, Cameroonian dark chocolate (70% cocoa), baking powder.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Gâteau au Chocolat Noir du Cameroun',
                    'description': 'Gâteau riche et fondant préparé avec du cacao fin d\'origine camerounaise. '
                                  'Un délice pour les amateurs de chocolat intense.',
                    'price': 5500,
                    'stock_quantity': 8,
                    'ingredients': 'Farine, œufs, sucre, beurre, chocolat noir du Cameroun (70% cacao), levure chimique.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Plantain Banana Cake',
                    'description': 'Soft and fragrant cake, prepared with very ripe plantain bananas. A local reinterpretation of banana bread, with caramelized notes.',
                    'price': 4500,
                    'stock_quantity': 12,
                    'ingredients': 'Flour, eggs, sugar, oil, ripe plantains, yeast, cinnamon, nutmeg.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Cake aux Bananes Plantain',
                    'description': 'Cake moelleux et parfumé, préparé avec des bananes plantain bien mûres. '
                                  'Une réinterprétation locale du banana bread, avec des notes caramélisées.',
                    'price': 4500,
                    'stock_quantity': 12,
                    'ingredients': 'Farine, œufs, sucre, huile, bananes plantain mûres, levure, cannelle, muscade.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Traditional Wedding Cake',
                    'description': 'Festive multi-tiered cake, elegantly decorated. Flavored with vanilla and rum, it\'s the essential dessert for Cameroonian weddings.',
                    'price': 12000,
                    'stock_quantity': 5,
                    'ingredients': 'Flour, eggs, sugar, butter, vanilla, rum, candied fruits, buttercream.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Gâteau de Mariage Traditionnel',
                    'description': 'Gâteau festif à plusieurs étages, décoré avec élégance. Parfumé à la vanille '
                                  'et au rhum, c\'est le dessert incontournable des mariages camerounais.',
                    'price': 12000,
                    'stock_quantity': 5,
                    'ingredients': 'Farine, œufs, sucre, beurre, vanille, rhum, fruits confits, crème au beurre.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Honey and Peanut Cake',
                    'description': 'Soft cake prepared with honey from Cameroonian bees and garnished with pieces of roasted peanuts. An irresistible sweet-salty mix.',
                    'price': 5000,
                    'stock_quantity': 10,
                    'ingredients': 'Flour, eggs, sugar, honey, butter, roasted peanuts, yeast.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Gâteau au Miel et Arachides',
                    'description': 'Gâteau moelleux préparé avec du miel d\'abeilles camerounaises et garni d\'éclats '
                                  'd\'arachides grillées. Un mélange sucré-salé irrésistible.',
                    'price': 5000,
                    'stock_quantity': 10,
                    'ingredients': 'Farine, œufs, sucre, miel, beurre, arachides grillées, levure.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Coconut Cake',
                    'description': 'Light and airy cake prepared with grated coconut. Perfect for lovers of exotic flavors and sweet treats.',
                    'price': 4800,
                    'stock_quantity': 15,
                    'ingredients': 'Flour, eggs, sugar, coconut milk, grated coconut, yeast.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Gâteau à la Noix de Coco',
                    'description': 'Gâteau léger et aérien préparé avec de la noix de coco râpée. Parfait pour les amateurs '
                                  'de saveurs exotiques et de douceurs sucrées.',
                    'price': 4800,
                    'stock_quantity': 15,
                    'ingredients': 'Farine, œufs, sucre, lait de coco, noix de coco râpée, levure.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Curdled Milk Cake',
                    'description': 'Traditional cake prepared with curdled milk, offering a unique texture and a slightly tangy taste. Perfect for snack time.',
                    'price': 5200,
                    'stock_quantity': 10,
                    'ingredients': 'Flour, eggs, sugar, curdled milk, yeast, vanilla.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Gâteau au Lait de Caillé',
                    'description': 'Gâteau traditionnel préparé avec du lait de caillé, offrant une texture unique '
                                  'et un goût légèrement acidulé. Parfait pour le goûter.',
                    'price': 5200,
                    'stock_quantity': 10,
                    'ingredients': 'Farine, œufs, sucre, lait de caillé, levure, vanille.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'African Spice Cake',
                    'description': 'Cake flavored with African spices (cinnamon, nutmeg, ginger) and garnished with dried fruits. A comforting delight for lovers of spicy flavors.',
                    'price': 5500,
                    'stock_quantity': 8,
                    'ingredients': 'Flour, eggs, sugar, butter, African spices, dried fruits (raisins, apricots).',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Gâteau aux Épices Africaines',
                    'description': 'Gâteau parfumé aux épices africaines (cannelle, muscade, gingembre) et garni de fruits '
                                  'secs. Un délice réconfortant pour les amateurs de saveurs épicées.',
                    'price': 5500,
                    'stock_quantity': 8,
                    'ingredients': 'Farine, œufs, sucre, beurre, épices africaines, fruits secs (raisins, abricots).',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Cameroonian Coffee Cake',
                    'description': 'Soft cake prepared with Cameroonian arabica coffee. A delight for coffee lovers, with a local touch.',
                    'price': 5300,
                    'stock_quantity': 9,
                    'ingredients': 'Flour, eggs, sugar, butter, Cameroonian arabica coffee, yeast, coffee cream.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Gâteau au Café du Cameroun',
                    'description': 'Gâteau moelleux préparé avec du café arabica camerounais. Un délice pour '
                                  'les amateurs de café, avec une touche locale.',
                    'price': 5300,
                    'stock_quantity': 9,
                    'ingredients': 'Farine, œufs, sucre, beurre, café arabica du Cameroun, levure, crème au café.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Almond and Lemon Cake',
                    'description': 'Refined almond cake with a touch of fresh Cameroonian lemon. Soft texture and slightly crispy crust.',
                    'price': 5800,
                    'stock_quantity': 7,
                    'ingredients': 'Flour, eggs, sugar, butter, ground almonds, lemon zest, lemon juice, yeast.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Gâteau aux Amandes et Citron',
                    'description': 'Gâteau raffiné aux amandes avec une touche de citron frais camerounais. '
                                  'Texture moelleuse et croûte légèrement croustillante.',
                    'price': 5800,
                    'stock_quantity': 7,
                    'ingredients': 'Farine, œufs, sucre, beurre, amandes en poudre, zeste de citron, jus de citron, levure.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Caramelized Pineapple Cake',
                    'description': 'Moist cake with caramelized local pineapple, a specialty from the coastal region.',
                    'price': 5200,
                    'stock_quantity': 10,
                    'ingredients': 'Flour, eggs, sugar, butter, fresh pineapple, caramel, yeast.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Gâteau à l\'Ananas Caramélisé',
                    'description': 'Gâteau moelleux à l\'ananas local caramélisé, une spécialité de la région côtière.',
                    'price': 5200,
                    'stock_quantity': 10,
                    'ingredients': 'Farine, œufs, sucre, beurre, ananas frais, caramel, levure.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Red Velvet Cake with Hibiscus',
                    'description': 'Classic red velvet cake with a Cameroonian twist using hibiscus for natural coloring and flavor.',
                    'price': 6000,
                    'stock_quantity': 6,
                    'ingredients': 'Flour, eggs, sugar, butter, cocoa, hibiscus extract, buttermilk, cream cheese.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Gâteau Red Velvet à l\'Hibiscus',
                    'description': 'Gâteau red velvet classique avec une touche camerounaise utilisant l\'hibiscus pour la coloration et la saveur naturelles.',
                    'price': 6000,
                    'stock_quantity': 6,
                    'ingredients': 'Farine, œufs, sucre, beurre, cacao, extrait d\'hibiscus, babeurre, fromage à la crème.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for cake in cake_products:
            self._create_product(**cake[current_language], category=category)
    
    def _create_other_products(self, category):
        # Other products in both languages
        other_products = [
            {
                'en': {
                    'name': 'Bean Fritters (Akara)',
                    'description': 'Soft fritters made from bean puree, fried in oil. A popular specialty throughout Cameroon, often consumed for breakfast.',
                    'price': 300,
                    'stock_quantity': 50,
                    'ingredients': 'White beans, onions, chili, salt, frying oil.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Beignets de Haricots (Akara)',
                    'description': 'Beignets moelleux à base de purée de haricots, frits à l\'huile. '
                                  'Une spécialité populaire dans tout le Cameroun, souvent consommée au petit-déjeuner.',
                    'price': 300,
                    'stock_quantity': 50,
                    'ingredients': 'Haricots blancs, oignons, piment, sel, huile de friture.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Traditional Puff-Puff',
                    'description': 'Spherical and soft doughnuts, slightly sweet. A very popular street pastry in Cameroon, ideal for snack time.',
                    'price': 250,
                    'stock_quantity': 60,
                    'ingredients': 'Flour, sugar, yeast, water, salt, frying oil, nutmeg.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Puff-Puff Traditionnel',
                    'description': 'Beignets sphériques et moelleux, légèrement sucrés. Une pâtisserie de rue '
                                  'très populaire au Cameroun, idéale pour le goûter.',
                    'price': 250,
                    'stock_quantity': 60,
                    'ingredients': 'Farine, sucre, levure, eau, sel, huile de friture, noix de muscade.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Monkey Bread (Coconut Ball)',
                    'description': 'Traditional confectionery made from grated coconut and caramelized sugar. A crunchy sweetness much appreciated by children and adults.',
                    'price': 400,
                    'stock_quantity': 45,
                    'ingredients': 'Grated coconut, sugar, water, vanilla.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Pain de Singe (Boule de Noix de Coco)',
                    'description': 'Confiserie traditionnelle à base de noix de coco râpée et de sucre caramélisé. '
                                  'Une douceur croquante très appréciée des enfants et adultes.',
                    'price': 400,
                    'stock_quantity': 45,
                    'ingredients': 'Noix de coco râpée, sucre, eau, vanille.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Grilled Cassava Sticks',
                    'description': 'Fresh cassava cut into sticks and grilled on charcoal. A healthy and energizing snack typical of Cameroonian streets.',
                    'price': 350,
                    'stock_quantity': 55,
                    'ingredients': 'Fresh cassava, salt (optional).',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Bâtonnets de Manioc Grillés',
                    'description': 'Manioc frais coupé en bâtonnets et grillé au charbon de bois. '
                                  'Une collation saine et énergétique typique des rues camerounaises.',
                    'price': 350,
                    'stock_quantity': 55,
                    'ingredients': 'Manioc frais, sel (optionnel).',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Natural Oku Honey',
                    'description': 'Pure and natural honey harvested in the Oku mountains, Northwest region of Cameroon. An exceptional product with multiple benefits.',
                    'price': 3500,
                    'stock_quantity': 15,
                    'ingredients': '100% pure honey.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Miel Naturel d\'Oku',
                    'description': 'Miel pur et naturel récolté dans les montagnes d\'Oku, région du Nord-Ouest '
                                  'du Cameroun. Un produit d\'exception aux multiples bienfaits.',
                    'price': 3500,
                    'stock_quantity': 15,
                    'ingredients': 'Miel 100% pur.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for product in other_products:
            self._create_product(**product[current_language], category=category)
    
    def _create_meals_products(self, category):
        # Meal products in both languages
        meal_products = [
            {
                'en': {
                    'name': 'Poulet DG',
                    'description': 'Famous Cameroonian dish with chicken, plantains and vegetables cooked in a rich sauce. A festive meal for special occasions.',
                    'price': 3500,
                    'stock_quantity': 15,
                    'ingredients': 'Chicken, ripe plantains, carrots, bell peppers, onions, garlic, spices, palm oil.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Poulet DG',
                    'description': 'Plat camerounais célèbre à base de poulet, plantains et légumes cuits dans une sauce riche. Un repas festif pour les occasions spéciales.',
                    'price': 3500,
                    'stock_quantity': 15,
                    'ingredients': 'Poulet, plantains mûrs, carottes, poivrons, oignons, ail, épices, huile de palme.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Sanga',
                    'description': 'Traditional dish from the West region made with smoked fish, huckleberry leaves and red oil, served with corn fufu.',
                    'price': 2800,
                    'stock_quantity': 20,
                    'ingredients': 'Smoked fish, njama-njama leaves, palm oil, onions, spices, corn fufu.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Sanga',
                    'description': 'Plat traditionnel de la région de l\'Ouest à base de poisson fumé, feuilles de njama-njama et huile rouge, servi avec du fufu de maïs.',
                    'price': 2800,
                    'stock_quantity': 20,
                    'ingredients': 'Poisson fumé, feuilles de njama-njama, huile de palme, oignons, épices, fufu de maïs.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Nkui',
                    'description': 'Traditional Bamileke soup made with snails, smoked fish and aromatic herbs, thickened with egusi seeds.',
                    'price': 3000,
                    'stock_quantity': 12,
                    'ingredients': 'Snails, smoked fish, egusi seeds, bitter leaves, spices, palm oil.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Nkui',
                    'description': 'Soupe traditionnelle bamiléké à base d\'escargots, poisson fumé et herbes aromatiques, épaissie avec des graines d\'egusi.',
                    'price': 3000,
                    'stock_quantity': 12,
                    'ingredients': 'Escargots, poisson fumé, graines d\'egusi, feuilles amères, épices, huile de palme.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Koki Corn',
                    'description': 'Steamed corn and bean pudding wrapped in banana leaves, a staple food in the West region.',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Corn, black-eyed peas, palm oil, spices, banana leaves.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Koki de Maïs',
                    'description': 'Pudding de maïs et haricots cuit à la vapeur dans des feuilles de bananier, un aliment de base dans la région de l\'Ouest.',
                    'price': 1800,
                    'stock_quantity': 25,
                    'ingredients': 'Maïs, haricots à œil noir, huile de palme, épices, feuilles de bananier.',
                    'is_featured': False
                }
            }
        ]
        
        current_language = translation.get_language()
        for meal in meal_products:
            self._create_product(**meal[current_language], category=category)
    
    def _create_drinks_products(self, category):
        # Drink products in both languages
        drink_products = [
            {
                'en': {
                    'name': 'Palm Wine',
                    'description': 'Traditional alcoholic beverage tapped from palm trees, naturally fermented. A popular drink in village gatherings.',
                    'price': 1500,
                    'stock_quantity': 20,
                    'ingredients': 'Fresh palm sap.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Vin de Palme',
                    'description': 'Boisson alcoolisée traditionnelle extraite des palmiers, fermentée naturellement. Une boisson populaire dans les rassemblements villageois.',
                    'price': 1500,
                    'stock_quantity': 20,
                    'ingredients': 'Sève fraîche de palmier.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Ginger Beer',
                    'description': 'Non-alcoholic fermented drink made from ginger, very refreshing with a spicy kick.',
                    'price': 1000,
                    'stock_quantity': 30,
                    'ingredients': 'Ginger, sugar, water, lemon, yeast.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Gingembre Beer',
                    'description': 'Boisson fermentée non alcoolisée à base de gingembre, très rafraîchissante avec une touche épicée.',
                    'price': 1000,
                    'stock_quantity': 30,
                    'ingredients': 'Gingembre, sucre, eau, citron, levure.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'African Coffee',
                    'description': 'Strong and aromatic coffee made from locally grown arabica beans in the Western Highlands.',
                    'price': 1200,
                    'stock_quantity': 25,
                    'ingredients': 'Cameroonian arabica coffee beans.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Café Africain',
                    'description': 'Café fort et aromatique à base de grains d\'arabica cultivés localement dans les Hautes Terres de l\'Ouest.',
                    'price': 1200,
                    'stock_quantity': 25,
                    'ingredients': 'Grains de café arabica camerounais.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Lemongrass Tea',
                    'description': 'Soothing herbal tea made from fresh lemongrass, known for its digestive properties.',
                    'price': 800,
                    'stock_quantity': 40,
                    'ingredients': 'Fresh lemongrass, water, honey (optional).',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Thé à la Citronnelle',
                    'description': 'Infusion apaisante à base de citronnelle fraîche, connue pour ses propriétés digestives.',
                    'price': 800,
                    'stock_quantity': 40,
                    'ingredients': 'Citronnelle fraîche, eau, miel (optionnel).',
                    'is_featured': False
                }
            }
        ]
        
        current_language = translation.get_language()
        for drink in drink_products:
            self._create_product(**drink[current_language], category=category)
    
    def _create_snacks_products(self, category):
        # Snack products in both languages
        snack_products = [
            {
                'en': {
                    'name': 'Roasted Corn',
                    'description': 'Fresh corn roasted on charcoal, a popular street snack often seasoned with chili and salt.',
                    'price': 300,
                    'stock_quantity': 50,
                    'ingredients': 'Fresh corn, salt, chili (optional).',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Maïs Grillé',
                    'description': 'Maïs frais grillé au charbon de bois, un en-cas de rue populaire souvent assaisonné de piment et de sel.',
                    'price': 300,
                    'stock_quantity': 50,
                    'ingredients': 'Maïs frais, sel, piment (optionnel).',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Fried Plantains',
                    'description': 'Ripe plantains fried to perfection, a sweet and satisfying snack found throughout Cameroon.',
                    'price': 500,
                    'stock_quantity': 40,
                    'ingredients': 'Ripe plantains, palm oil.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Plantains Frits',
                    'description': 'Plantains mûrs frits à la perfection, une collation sucrée et satisfaisante que l\'on trouve dans tout le Cameroun.',
                    'price': 500,
                    'stock_quantity': 40,
                    'ingredients': 'Plantains mûrs, huile de palme.',
                    'is_featured': True
                }
            },
            {
                'en': {
                    'name': 'Peanut Brittle',
                    'description': 'Crunchy candy made with local peanuts and caramelized sugar, a favorite among children.',
                    'price': 400,
                    'stock_quantity': 35,
                    'ingredients': 'Peanuts, sugar, water.',
                    'is_featured': False
                },
                'fr': {
                    'name': 'Croquants d\'Arachides',
                    'description': 'Bonbon croquant à base d\'arachides locales et de sucre caramélisé, un favori parmi les enfants.',
                    'price': 400,
                    'stock_quantity': 35,
                    'ingredients': 'Arachides, sucre, eau.',
                    'is_featured': False
                }
            },
            {
                'en': {
                    'name': 'Grilled Fish',
                    'description': 'Fresh fish marinated with local spices and grilled over charcoal, served with spicy sauce.',
                    'price': 2500,
                    'stock_quantity': 15,
                    'ingredients': 'Fresh fish, onions, garlic, ginger, chili, spices.',
                    'is_featured': True
                },
                'fr': {
                    'name': 'Poisson Grillée',
                    'description': 'Poisson frais mariné avec des épices locales et grillé au charbon de bois, servi avec une sauce épicée.',
                    'price': 2500,
                    'stock_quantity': 15,
                    'ingredients': 'Poisson frais, oignons, ail, gingembre, piment, épices.',
                    'is_featured': True
                }
            }
        ]
        
        current_language = translation.get_language()
        for snack in snack_products:
            self._create_product(**snack[current_language], category=category)