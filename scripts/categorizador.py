"""
Adivina la categoría de un producto buscando palabras clave en el
nombre y la marca.

Las categorías no las inventamos nosotros: son las mismas que usa
el dataset SEPA / Precios Claros (https://www.preciosclaros.gob.ar):

    Alimentos Congelados
    Almacén
    Bebés
    Bebidas con Alcohol
    Bebidas sin Alcohol
    Frescos
    Limpieza
    Mascotas
    Perfumería y Cuidado Personal
    Electrodomésticos y Equipamiento para el Hogar
    Materiales para la Construcción

Ojo que esto no es una clasificación oficial, es puramente buscar
palabras conocidas en el texto del producto. Funciona bastante bien
pero seguro se equivoca en algún caso raro, y a los productos con
nombres poco descriptivos directamente no los va a poder clasificar.
Las reglas se prueban en orden y gana la primera que matchea, así
que las más específicas van primero: si "Almacén" estuviera al
principio se comería casi todo (es el cajón de sastre de la
despensa).
"""

import re
import unicodedata


def _normalizar(texto):
    texto = str(texto or "").lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def _regex(palabras):
    patron = "|".join(re.escape(p) for p in palabras)
    return re.compile(rf"\b(?:{patron})\b")


# Cada regla: (categoria_1, categoria_2, categoria_3, [palabras clave])
# categoria_3 puede ser None cuando no se puede afinar tanto.
_REGLAS_CRUDAS = [
    # ---------------------------------------------------------
    # Mascotas
    # ---------------------------------------------------------
    ("Mascotas", "Alimentos", None,
        ["alimento perro", "alimento gato", "balanceado perro",
         "balanceado gato", "purina", "dog chow", "cat chow",
         "pedigree", "whiskas", "gatos", "perros", "cachorro",
         "cachorros", "felino", "canino"]),
    ("Mascotas", "Accesorios e Higiene", None,
        ["arena sanitaria", "arena para gatos", "correa mascota",
         "collar mascota", "piedras sanitarias"]),

    # ---------------------------------------------------------
    # Bebés
    # ---------------------------------------------------------
    ("Bebés", "Higiene", None,
        ["pañal", "panal", "pañales", "panales", "pampers",
         "huggies", "toallitas humedas bebe", "toallitas humedas bebé"]),
    ("Bebés", "Alimentación", None,
        ["papilla", "cereal infantil", "leche infantil",
         "leche de formula", "nutrilon", "formula infantil"]),

    # ---------------------------------------------------------
    # Bebidas con alcohol
    # ---------------------------------------------------------
    ("Bebidas con Alcohol", "Cervezas", None,
        ["cerveza", "cervezas", "porron", "ipa", "stout", "ale"]),
    ("Bebidas con Alcohol", "Espumantes", None,
        ["espumante", "champagne", "champaña", "sidra", "brut"]),
    ("Bebidas con Alcohol", "Licores y Aperitivos", None,
        ["licor", "whisky", "whiskey", "vodka", "gin", "ron",
         "fernet", "aperitivo", "amargo"]),
    ("Bebidas con Alcohol", "Vinos", None,
        ["vino", "vinos", "malbec", "cabernet", "sauvignon",
         "chardonnay", "syrah", "torrontes", "merlot", "bonarda",
         "pinot", "blend de vino", "vino tinto", "vino blanco",
         "vino rosado"]),

    # ---------------------------------------------------------
    # Bebidas sin alcohol
    # ---------------------------------------------------------
    ("Bebidas sin Alcohol", "Gaseosas", None,
        ["gaseosa", "gaseosas", "cola", "soda"]),
    ("Bebidas sin Alcohol", "Jugos", None,
        ["jugo", "jugos", "nectar", "bebible"]),
    ("Bebidas sin Alcohol", "Aguas", None,
        ["agua mineral", "agua saborizada", "soda de mesa"]),

    # ---------------------------------------------------------
    # Limpieza
    # ---------------------------------------------------------
    ("Limpieza", "Ropa", None,
        ["jabon en polvo", "jabon polvo", "jabon liquido para ropa",
         "jabon liquido ropa", "jabon para ropa", "jabon ropa",
         "detergente para ropa", "suavizante para ropa",
         "suavizante de ropa", "lavandina", "quitamanchas",
         "vivere", "confort", "downy"]),
    ("Limpieza", "Cocina y Baño", None,
        ["detergente", "limpiador", "desinfectante", "esponja",
         "lavavajilla", "lavavajillas", "abrillantador"]),
    ("Limpieza", "Pisos y Superficies", None,
        ["limpiador de pisos", "cera para pisos", "lustramuebles",
         "trapo de piso", "rejilla", "escobillon", "multiuso",
         "secador de pisos", "cepillo de pisos", "pisos"]),
    ("Limpieza", "Aromatizantes e Insecticidas", None,
        ["aromatizante", "insecticida", "glade", "poett",
         "repelente"]),
    ("Limpieza", "Descartables", None,
        ["papel higienico", "rollo de cocina", "servilletas",
         "bolsas de residuo", "bolsas para residuos", "bolsas se residuo",
         "bolsas de residuos", "bolsas para consorcio",
         "bolsas de consorcio", "bolsas hermeticas", "bolsas verdes"]),
    ("Limpieza", "Cocina y Baño", None,
        ["limpia metales", "limpiametales", "brasso"]),

    # ---------------------------------------------------------
    # Perfumería y Cuidado Personal
    # ---------------------------------------------------------
    ("Perfumería y Cuidado Personal", "Cuidado Capilar", None,
        ["shampoo", "champu", "acondicionador", "tintura",
         "coloracion", "tratamiento capilar", "capilar", "gel para el cabello",
         "fijador"]),
    ("Perfumería y Cuidado Personal", "Cuidado Bucal", None,
        ["pasta dental", "crema dental", "cepillo de dientes",
         "cepillo dental", "cepillo ortodoncia", "enjuague bucal",
         "hilo dental"]),
    ("Perfumería y Cuidado Personal", "Higiene Femenina", None,
        ["toallitas femeninas", "toalla femenina", "protector diario",
         "tampones"]),
    ("Perfumería y Cuidado Personal", "Afeitado", None,
        ["afeitar", "afeitado", "maquina de afeitar", "espuma de afeitar"]),
    ("Perfumería y Cuidado Personal", "Cuidado de la Piel", None,
        ["protector solar", "crema corporal", "locion", "colonia",
         "perfume", "fragancia", "maquillaje", "esmalte", "labial",
         "antitranspirante", "desodorante", "jabon de tocador",
         "jabon tocador", "humectante", "alcohol en gel", "jabon"]),

    # Esto va antes que la regla de huevos de Frescos: si no, los
    # huevos de pascua y las pastas al huevo terminan clasificados
    # como huevos de verdad.
    ("Almacén", "Snacks y Golosinas", None,
        ["huevo de pascua", "huevo kinder", "huevo sorpresa",
         "huevos de pascua", "kinder sorpresa", "huevo de chocolate",
         "huevos de chocolate"]),
    ("Almacén", "Harinas y Pastas", None,
        ["tallarines", "tallarin", "sorrentinos", "capelettis",
         "canelones", "fideos", "noquis", "ñoquis", "ravioles",
         "al huevo"]),

    # ---------------------------------------------------------
    # Alimentos Congelados
    # ---------------------------------------------------------
    ("Alimentos Congelados", "Helados", None,
        ["helado", "helados", "paleta helada", "polo helado"]),
    ("Alimentos Congelados", "Vegetales Congelados", None,
        ["vegetales congelados", "papas congeladas",
         "papas prefritas", "arvejas congeladas", "choclo congelado"]),
    ("Alimentos Congelados", "Rebozados y Prefritos", None,
        ["rebozadas", "rebozado", "nuggets", "medallon de pollo",
         "medallones de pollo", "hamburguesa congelada",
         "hamburguesas congeladas", "rabas", "milanesa de soja"]),
    ("Alimentos Congelados", "Pizzas y Tartas Congeladas", None,
        ["pizza congelada", "tarta congelada"]),

    # ---------------------------------------------------------
    # Frescos
    # ---------------------------------------------------------
    ("Frescos", "Lácteos", None,
        ["leche", "yogur", "yogurt", "queso", "manteca",
         "crema de leche", "crema para batir", "postre lacteo",
         "danonino", "ricota"]),
    ("Frescos", "Huevos", None,
        ["huevo", "huevos"]),
    ("Frescos", "Carnicería", None,
        ["pollo", "pechuga", "carne", "cerdo", "bife", "asado",
         "matambre", "chorizo", "jamon", "mortadela", "panceta",
         "morcilla", "vacio", "cuadril", "nalga", "lomo", "ternera",
         "novillo", "novillito", "salame", "salamin", "bondiola",
         "milanesa", "salchicha", "salchichas", "mondongo",
         "roast beef", "rost beef"]),
    ("Frescos", "Pescadería", None,
        ["merluza", "salmon", "pescado fresco", "filet de merluza",
         "gatuzo"]),
    ("Frescos", "Frutas", None,
        ["banana", "manzana", "naranja", "frutilla", "uva", "pera",
         "limon", "pomelo", "anana", "ciruela", "mandarina",
         "kiwi", "durazno fresco"]),
    ("Frescos", "Verduras", None,
        ["lechuga", "tomate", "cebolla", "zanahoria", "zapallo",
         "acelga", "espinaca", "batata", "papa", "morron",
         "berenjena", "pepino", "ajo", "pimiento", "hinojo"]),

    # ---------------------------------------------------------
    # Electrodomésticos y equipamiento para el hogar
    # ---------------------------------------------------------
    ("Electrodomésticos y Equipamiento para el Hogar", None, None,
        ["heladera", "microondas", "licuadora", "lavarropas",
         "ventilador", "aire acondicionado", "pava electrica",
         "cafetera", "batidora", "tostadora"]),

    # ---------------------------------------------------------
    # Materiales para la construcción
    # ---------------------------------------------------------
    ("Materiales para la Construcción", None, None,
        ["cemento", "pintura para pared", "ladrillo", "cal hidraulica",
         "hierro para construccion", "arena gruesa"]),

    # ---------------------------------------------------------
    # Almacén: va al final porque es el cajón de sastre de todo
    # lo que sea despensa
    # ---------------------------------------------------------
    ("Almacén", "Aceites", None,
        ["aceite"]),
    ("Almacén", "Conservas", None,
        ["conserva", "conservas", "atun", "arvejas", "choclo",
         "duraznos en almibar", "palmitos", "aceitunas", "aceituna",
         "pure de tomate", "porotos", "lentejas", "garbanzos"]),
    ("Almacén", "Desayuno y Merienda", None,
        ["yerba", "cafe", "mate cocido", "cacao", "mermelada",
         "dulce de leche", "miel", "cereales", "avena", "te",
         "saquitos", "coco rallado", "membrillo"]),
    ("Almacén", "Panificados", None,
        ["pan lactal", "pan integral", "pan de mesa", "pan de panchos",
         "pan de hamburguesa", "pan lacteado", "pan casero",
         "marinera", "grisines", "tostadas", "facturas",
         "bizcochuelo", "hojaldre", "bizcochos"]),
    ("Almacén", "Harinas y Pastas", None,
        ["harina", "fideos", "noquis", "ravioles", "arroz",
         "polenta", "premezcla", "pan rallado", "tapas de empanadas",
         "tapas para empanadas", "tapas empanadas", "tapas pascualina",
         "tapas canelon", "pascualina", "tapas"]),
    ("Almacén", "Snacks y Golosinas", None,
        ["galletitas", "galletas", "papas fritas", "snack",
         "alfajor", "chocolate", "golosina", "chicle", "caramelo",
         "caramelos", "chupetin", "chupetines", "mani", "turron",
         "obleas", "bombon", "bombones"]),
    ("Almacén", "Condimentos y Salsas", None,
        ["salsa", "mayonesa", "mostaza", "vinagre", "condimento",
         "especias", "azucar", "edulcorante", "sal fina", "caldo",
         "chimichurri", "parrillero"]),
    ("Almacén", "Sopas y Puré", None,
        ["sopa", "pure instantaneo", "pure de papas", "gelatina",
         "budin"]),
]

REGLAS = [
    (cat1, cat2, cat3, _regex(palabras))
    for cat1, cat2, cat3, palabras in _REGLAS_CRUDAS
]


def clasificar(nombre, marca=""):
    """Devuelve (categoria_1, categoria_2, categoria_3) o
    (None, None, None) si ninguna regla matchea."""

    texto = _normalizar(f"{nombre} {marca}")

    for cat1, cat2, cat3, patron in REGLAS:
        if patron.search(texto):
            return cat1, cat2 or "", cat3 or ""

    return None, None, None
