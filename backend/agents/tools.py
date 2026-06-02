from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import time


# ══════════════════════════════════════════════════════════════════
#  SHARED DISEASE NAME NORMALISER
#  Import this in crew_agents.py:  from backend.agents.tools import normalize_disease_name
# ══════════════════════════════════════════════════════════════════

_PLANT_NAMES = {
    "apple", "tomato", "potato", "grape", "corn", "rice", "wheat",
    "soybean", "soyabean", "strawberry", "peach", "pepper", "sugarcane",
    "sugercane", "mango", "banana", "coffee", "tea", "lemon", "orange",
    "papaya", "lettuce", "pea", "cabbage", "cauliflower", "chili",
    "eggplant", "gourd", "hibiscus", "jasmine", "rose", "pumpkin", "plum",
}

_STRIP_SUFFIXES = (
    " leaf", " disease", " on lettuce", " on pea", " on corn",
    " on rice", " on wheat", " on mango",
)


def normalize_disease_name(disease: str) -> str:
    """
    Convert any dataset disease label into a clean, readable string.

    Apple___Apple_scab            → Apple Scab
    Tomato_Early_blight           → Early Blight
    DOWNY_MILDEW_LEAF             → Downy Mildew
    Mango___Bacterial Canker      → Bacterial Canker
    Pepper__bell___Bacterial_spot → Bacterial Spot
    Soybean__bacterial_blight     → Bacterial Blight
    Common_Rust                   → Common Rust
    Boron                         → Boron
    Bacterial Lettuce             → Bacterial
    """
    # 1. PlantVillage triple-underscore format → keep part after "___"
    if "___" in disease:
        disease = disease.split("___", 1)[1]

    # 2. Underscores → spaces; collapse extra whitespace
    disease = " ".join(disease.replace("_", " ").split())

    # 3. Strip trailing noise suffixes (case-insensitive)
    low = disease.lower()
    for s in _STRIP_SUFFIXES:
        if low.endswith(s):
            disease = disease[: -len(s)].strip()
            low = disease.lower()
            break

    parts = disease.split()

    # 4. Remove leading plant name (only when multiple words remain)
    if len(parts) > 1 and parts[0].lower() in _PLANT_NAMES:
        parts = parts[1:]

    # 5. Remove trailing plant name  ("Bacterial Lettuce" → "Bacterial")
    if len(parts) > 1 and parts[-1].lower() in _PLANT_NAMES:
        parts = parts[:-1]

    # 6. Collapse duplicate leading word ("Apple Apple Scab" → "Apple Scab")
    if len(parts) >= 2 and parts[0].lower() == parts[1].lower():
        parts = parts[1:]

    return " ".join(parts).title().strip() or disease.title()


# ══════════════════════════════════════════════════════════════════
#  PESTICIDE DATABASE  (~80 entries covering all dataset diseases)
# ══════════════════════════════════════════════════════════════════

_PESTICIDE_DB: dict[str, str] = {

    # ── FUNGAL ───────────────────────────────────────────────────
    "apple scab": (
        "Captan 50WP – 2.5 g/L, every 7–10 days. Cost: ₹300/kg. "
        "Organic: Sulfur dust 3 g/L or Neem oil 5 ml/L."
    ),
    "black rot": (
        "Captan 50WP – 2 g/L, every 10 days. Cost: ₹300/kg. "
        "Organic: Bordeaux mixture 1%."
    ),
    "cedar apple rust": (
        "Myclobutanil 20EW – 1 ml/L, every 10 days. Cost: ₹700/L. "
        "Organic: Sulfur dust 3 g/L."
    ),
    "early blight": (
        "Mancozeb 75WP – 2.5 g/L, every 7 days. Cost: ₹250/kg. "
        "Organic: Neem oil 5 ml/L."
    ),
    "late blight": (
        "Metalaxyl + Mancozeb – 2 g/L, every 5 days. Cost: ₹400/kg. "
        "Organic: Copper Oxychloride 3 g/L."
    ),
    "powdery mildew": (
        "Sulfur 80WP – 3 g/L, every 10 days. Cost: ₹180/kg. "
        "Organic: Baking soda 5 g/L + liquid soap 2 ml/L."
    ),
    "downy mildew": (
        "Cymoxanil + Mancozeb – 2.5 g/L, every 7 days. Cost: ₹450/kg. "
        "Organic: Copper Oxychloride 3 g/L."
    ),
    "rust": (
        "Propiconazole 25EC – 1 ml/L, every 10 days. Cost: ₹600/L. "
        "Organic: Neem oil 10 ml/L."
    ),
    "common rust": (
        "Propiconazole 25EC – 1 ml/L, every 10 days. Cost: ₹600/L. "
        "Organic: Neem oil 10 ml/L."
    ),
    "stripe rust": (
        "Tebuconazole 25.9EC – 1 ml/L, every 14 days. Cost: ₹750/L. "
        "Organic: Sulfur dust 3 g/L."
    ),
    "coffee rust": (
        "Copper Oxychloride 50WP – 3 g/L, every 14 days. Cost: ₹200/kg. "
        "Organic: Bordeaux mixture 1%."
    ),
    "sugarcane rust": (
        "Propiconazole 25EC – 1 ml/L, every 14 days. Cost: ₹600/L. "
        "Organic: Neem oil 10 ml/L."
    ),
    "anthracnose": (
        "Mancozeb + Carbendazim – 2 g/L, every 7 days. Cost: ₹350/kg. "
        "Organic: Bordeaux mixture 1%."
    ),
    "leaf spot": (
        "Carbendazim 50WP – 1 g/L, every 14 days. Cost: ₹300/kg. "
        "Organic: Trichoderma viride 5 g/L."
    ),
    "cercospora leaf spot": (
        "Carbendazim 50WP – 1 g/L, every 10 days. Cost: ₹300/kg. "
        "Organic: Neem oil 5 ml/L."
    ),
    "gray leaf spot": (
        "Azoxystrobin 23SC – 1 ml/L, every 14 days. Cost: ₹800/L. "
        "Organic: Copper Oxychloride 3 g/L."
    ),
    "septoria leaf spot": (
        "Chlorothalonil 75WP – 2 g/L, every 7–10 days. Cost: ₹400/kg. "
        "Organic: Copper sulfate 3 g/L."
    ),
    "septoria blight": (
        "Chlorothalonil 75WP – 2 g/L, every 7–10 days. Cost: ₹400/kg. "
        "Organic: Copper sulfate 3 g/L."
    ),
    "septoria": (
        "Chlorothalonil 75WP – 2 g/L, every 7–10 days. Cost: ₹400/kg. "
        "Organic: Copper sulfate 3 g/L."
    ),
    "alternaria spot": (
        "Iprodione 50WP – 1.5 g/L, every 10 days. Cost: ₹500/kg. "
        "Organic: Neem oil 5 ml/L."
    ),
    "brown spot": (
        "Propiconazole 25EC – 1 ml/L, every 10 days. Cost: ₹600/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "bird eye spot": (
        "Carbendazim 50WP – 1 g/L, every 14 days. Cost: ₹300/kg. "
        "Organic: Copper sulfate 3 g/L."
    ),
    "red leaf spot": (
        "Propiconazole 25EC – 1 ml/L, every 10 days. Cost: ₹600/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "algal leaf": (
        "Copper Oxychloride 50WP – 3 g/L, every 14 days. Cost: ₹200/kg. "
        "Organic: Bordeaux mixture 1%."
    ),
    "leaf blast": (
        "Tricyclazole 75WP – 0.6 g/L, every 10 days. Cost: ₹600/kg. "
        "Organic: Silicon-based foliar spray 2 ml/L."
    ),
    "neck blast": (
        "Tricyclazole 75WP – 0.6 g/L at panicle initiation, repeat once after 10 days. "
        "Cost: ₹600/kg. Organic: Pseudomonas fluorescens 10 g/L."
    ),
    "blight": (
        "Mancozeb 75WP – 2.5 g/L, every 7 days. Cost: ₹250/kg. "
        "Organic: Copper Oxychloride 3 g/L."
    ),
    "leaf blight": (
        "Propiconazole 25EC – 1 ml/L, every 10 days. Cost: ₹600/L. "
        "Organic: Copper Oxychloride 3 g/L."
    ),
    "brown blight": (
        "Carbendazim 50WP – 1 g/L, every 14 days. Cost: ₹300/kg. "
        "Organic: Trichoderma viride 5 g/L."
    ),
    "wilt and leaf blight": (
        "Mancozeb 75WP + Carbendazim 50WP – 2 g/L, every 7 days. Cost: ₹250/kg. "
        "Organic: Copper Oxychloride 3 g/L."
    ),
    "southern blight": (
        "Flutolanil 20WP – 2 g/L soil drench, every 14 days. Cost: ₹600/kg. "
        "Organic: Trichoderma harzianum 5 g/L drench."
    ),
    "wilt": (
        "Carbendazim 50WP – 1 g/L soil drench, every 14 days. Cost: ₹300/kg. "
        "Organic: Trichoderma harzianum 5 g/L."
    ),
    "white mold": (
        "Carbendazim 50WP – 1 g/L, every 14 days. Cost: ₹300/kg. "
        "Organic: Trichoderma viride 5 g/L."
    ),
    "sooty mould": (
        "Copper Oxychloride 50WP – 3 g/L + Neem oil 5 ml/L, every 14 days. "
        "Cost: ₹200/kg. Also control sap-sucking insects (aphids/mealybugs) that produce honeydew."
    ),
    "sooty mold": (
        "Copper Oxychloride 50WP – 3 g/L + Neem oil 5 ml/L, every 14 days. "
        "Cost: ₹200/kg. Also control sap-sucking insects that produce honeydew."
    ),
    "black spot": (
        "Chlorothalonil 75WP – 2 g/L, every 7–10 days. Cost: ₹400/kg. "
        "Organic: Neem oil 5 ml/L + Baking soda 5 g/L."
    ),
    "esca": (
        "No direct cure. Remove infected wood. Apply wound sealant after pruning. "
        "Organic: Trichoderma viride 5 g/L on pruning wounds."
    ),
    "black measles": (
        "No direct cure. Remove infected wood. Apply wound sealant after pruning. "
        "Organic: Trichoderma viride 5 g/L on pruning wounds."
    ),
    "target spot": (
        "Chlorothalonil 75WP – 2 g/L, every 10 days. Cost: ₹400/kg. "
        "Organic: Copper Oxychloride 3 g/L."
    ),
    "leaf mold": (
        "Chlorothalonil 75WP – 2 g/L, every 7 days. Cost: ₹400/kg. "
        "Organic: Neem oil 5 ml/L."
    ),
    "leaf scorch": (
        "Captan 50WP – 2 g/L, every 10 days. Cost: ₹300/kg. "
        "Organic: Neem oil 5 ml/L."
    ),
    "red rot": (
        "Carbendazim 50WP – 1 g/L, every 14 days. Cost: ₹300/kg. "
        "Organic: Trichoderma viride 5 g/L. Remove and destroy infected stalks immediately."
    ),
    "wheat scab": (
        "Tebuconazole 25.9EC – 1 ml/L at heading stage. Cost: ₹750/L. "
        "Organic: Trichoderma harzianum 10 g/L."
    ),
    "die back": (
        "Copper Oxychloride 50WP – 3 g/L + prune affected branches to healthy wood. "
        "Cost: ₹200/kg. Organic: Bordeaux paste on cut surfaces."
    ),

    # ── BACTERIAL ────────────────────────────────────────────────
    "bacterial": (
        "Copper Oxychloride 50WP – 3 g/L, every 7 days. Cost: ₹200/kg. "
        "Organic: Copper hydroxide 2 g/L."
    ),
    "bacterial blight": (
        "Streptomycin Sulfate 90SP – 0.5 g/L, every 7 days. Cost: ₹500/100g. "
        "Organic: Copper hydroxide 2 g/L."
    ),
    "bacterial spot": (
        "Copper Oxychloride 50WP – 3 g/L, every 7 days. Cost: ₹200/kg. "
        "Organic: Copper hydroxide 2 g/L."
    ),
    "bacterial canker": (
        "Copper Oxychloride 50WP – 3 g/L + prune infected branches. "
        "Cost: ₹200/kg. Organic: Bordeaux paste on pruning wounds."
    ),
    "citrus canker": (
        "Copper Oxychloride 50WP – 3 g/L, every 7 days. Cost: ₹200/kg. "
        "Organic: Bordeaux mixture 1%."
    ),
    "citrus greening": (
        "No cure available. Remove and destroy infected trees. "
        "Control psyllid vector: Imidacloprid 17.8SL – 0.5 ml/L. Cost: ₹700/L. "
        "Organic: Neem oil 5 ml/L + Yellow sticky traps."
    ),
    "yellow dragon": (
        "No cure available. Remove and destroy infected trees. "
        "Control psyllid vector: Imidacloprid 17.8SL – 0.5 ml/L. Cost: ₹700/L."
    ),
    "fire blight": (
        "Streptomycin 17WP – 1 g/L at blossom stage. Cost: ₹600/100g. "
        "Organic: Copper sulfate 3 g/L."
    ),
    "red stripe": (
        "Copper Oxychloride 50WP – 3 g/L, every 7 days. Cost: ₹200/kg. "
        "Organic: Bordeaux mixture 1%. Remove and destroy infected leaves."
    ),
    "black rot": (
        "Copper Oxychloride 50WP – 3 g/L, every 7 days. Cost: ₹200/kg. "
        "Organic: Bordeaux mixture 1%."
    ),

    # ── VIRAL ────────────────────────────────────────────────────
    "viral": (
        "No direct chemical cure. Remove infected plants immediately. "
        "Control insect vectors: Imidacloprid 17.8SL – 0.5 ml/L. Cost: ₹700/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "mosaic": (
        "No direct cure. Remove infected plants immediately. "
        "Control aphid/whitefly vectors: Imidacloprid 17.8SL – 0.5 ml/L. Cost: ₹700/L. "
        "Organic: Yellow sticky traps + Neem oil 5 ml/L."
    ),
    "mosaic virus": (
        "No direct cure. Remove infected plants immediately. "
        "Control aphid/whitefly vectors: Imidacloprid 17.8SL – 0.5 ml/L. Cost: ₹700/L. "
        "Organic: Yellow sticky traps + Neem oil 5 ml/L."
    ),
    "leaf curl": (
        "No direct cure. Control whitefly vector: Thiamethoxam 25WG – 0.3 g/L. "
        "Cost: ₹800/kg. Organic: Yellow sticky traps + Neem oil 5 ml/L."
    ),
    "curl virus": (
        "No direct cure. Control whitefly vector: Thiamethoxam 25WG – 0.3 g/L. "
        "Cost: ₹800/kg. Organic: Yellow sticky traps + Neem oil 5 ml/L."
    ),
    "yellow leaf curl virus": (
        "No direct cure. Control whitefly vector: Thiamethoxam 25WG – 0.3 g/L. "
        "Cost: ₹800/kg. Organic: Yellow sticky traps + Neem oil 5 ml/L."
    ),
    "ringspot": (
        "No direct cure. Remove infected plants. "
        "Control mite/aphid vectors: Abamectin 1.8EC – 1 ml/L. Cost: ₹800/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "yellow leaf disease": (
        "No direct cure. Control insect vectors: Imidacloprid 17.8SL – 0.5 ml/L. "
        "Cost: ₹700/L. Organic: Neem oil 5 ml/L."
    ),
    "yellow mosaic virus": (
        "No direct cure. Control whitefly vectors: Thiamethoxam 25WG – 0.3 g/L. "
        "Cost: ₹800/kg. Organic: Yellow sticky traps."
    ),

    # ── PEST ATTACKS ─────────────────────────────────────────────
    "aphid": (
        "Imidacloprid 17.8SL – 0.5 ml/L, every 7 days. Cost: ₹700/L. "
        "Organic: Neem oil 5 ml/L + Yellow sticky traps."
    ),
    "whitefly": (
        "Thiamethoxam 25WG – 0.3 g/L, every 7 days. Cost: ₹800/kg. "
        "Organic: Yellow sticky traps + Neem oil 5 ml/L."
    ),
    "spiny whitefly": (
        "Thiamethoxam 25WG – 0.3 g/L, every 7 days. Cost: ₹800/kg. "
        "Organic: Yellow sticky traps + Neem oil 5 ml/L."
    ),
    "spider mites": (
        "Abamectin 1.8EC – 1 ml/L, every 7 days. Cost: ₹800/L. "
        "Organic: Neem oil 5 ml/L + Sulfur dust 3 g/L."
    ),
    "red spider mite": (
        "Abamectin 1.8EC – 1 ml/L, every 7 days. Cost: ₹800/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "mite disease": (
        "Abamectin 1.8EC – 1 ml/L, every 7 days. Cost: ₹800/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "mealybug": (
        "Chlorpyrifos 20EC – 2 ml/L, every 14 days. Cost: ₹400/L. "
        "Organic: Neem oil 10 ml/L + Rubbing alcohol swab on stems."
    ),
    "citrus mealybugs": (
        "Chlorpyrifos 20EC – 2 ml/L, every 14 days. Cost: ₹400/L. "
        "Organic: Neem oil 10 ml/L."
    ),
    "leaf miner": (
        "Spinosad 45SC – 0.3 ml/L, every 7 days. Cost: ₹1200/L. "
        "Organic: Neem oil 5 ml/L + Yellow sticky traps."
    ),
    "leafminer": (
        "Spinosad 45SC – 0.3 ml/L, every 7 days. Cost: ₹1200/L. "
        "Organic: Neem oil 5 ml/L + Yellow sticky traps."
    ),
    "cutting weevil": (
        "Chlorpyrifos 20EC – 2 ml/L, every 14 days. Cost: ₹400/L. "
        "Organic: Neem oil 10 ml/L + Sticky barrier around trunk."
    ),
    "gall midge": (
        "Imidacloprid 17.8SL – 0.5 ml/L, every 7 days. Cost: ₹700/L. "
        "Organic: Neem oil 5 ml/L + Remove and destroy all galls."
    ),
    "caterpillar": (
        "Chlorpyrifos 20EC – 2 ml/L, every 7 days. Cost: ₹400/L. "
        "Organic: Bacillus thuringiensis (Bt) 2 g/L."
    ),
    "diabrotica speciosa": (
        "Chlorpyrifos 20EC – 2 ml/L, every 7 days. Cost: ₹400/L. "
        "Organic: Neem oil 5 ml/L + Kaolin clay spray."
    ),
    "insect": (
        "Chlorpyrifos 20EC – 2 ml/L, every 14 days. Cost: ₹400/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "insect pest": (
        "Chlorpyrifos 20EC – 2 ml/L, every 14 days. Cost: ₹400/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "insect hole": (
        "Chlorpyrifos 20EC – 2 ml/L, every 14 days. Cost: ₹400/L. "
        "Organic: Neem oil 5 ml/L."
    ),
    "insect bite": (
        "Neem oil 5 ml/L, every 7 days. "
        "Organic: Garlic spray (20 g crushed garlic/L) + Yellow sticky traps."
    ),

    # ── NUTRIENT DEFICIENCIES (Banana & others) ──────────────────
    "boron": (
        "Borax (Sodium Borate) – 1–2 g/L foliar spray, every 15 days. "
        "Cost: ₹50/kg. Soil application: 5–10 kg Borax/acre once per season."
    ),
    "boron deficiency": (
        "Borax (Sodium Borate) – 1–2 g/L foliar spray, every 15 days. "
        "Cost: ₹50/kg. Soil application: 5–10 kg Borax/acre once per season."
    ),
    "calcium": (
        "Calcium Nitrate – 2 g/L foliar spray, every 15 days. Cost: ₹200/kg. "
        "Organic: Crushed eggshells or Gypsum in soil."
    ),
    "calcium deficiency": (
        "Calcium Nitrate – 2 g/L foliar spray, every 15 days. Cost: ₹200/kg. "
        "Organic: Gypsum soil amendment 200 kg/acre."
    ),
    "iron": (
        "Ferrous Sulfate (FeSO4) – 2 g/L foliar spray, every 15 days. Cost: ₹80/kg. "
        "Organic: Composted organic matter improves iron availability."
    ),
    "iron deficiency": (
        "Ferrous Sulfate (FeSO4) – 2 g/L foliar spray, every 15 days. Cost: ₹80/kg. "
        "Organic: Composted organic matter."
    ),
    "magnesium": (
        "Magnesium Sulfate (Epsom Salt) – 10 g/L foliar spray, every 15 days. "
        "Cost: ₹60/kg. Organic: Dolomite lime soil amendment."
    ),
    "magnesium deficiency": (
        "Magnesium Sulfate (Epsom Salt) – 10 g/L foliar spray, every 15 days. "
        "Cost: ₹60/kg. Organic: Dolomite lime soil amendment."
    ),
    "manganese": (
        "Manganese Sulfate – 2 g/L foliar spray, every 15 days. Cost: ₹100/kg. "
        "Avoid over-liming soil which locks out manganese."
    ),
    "manganese deficiency": (
        "Manganese Sulfate – 2 g/L foliar spray, every 15 days. Cost: ₹100/kg. "
        "Avoid over-liming soil."
    ),
    "potassium": (
        "Potassium Sulfate (SOP) – 5 g/L foliar spray, every 15 days. Cost: ₹200/kg. "
        "Organic: Wood ash 50 g/L soil drench."
    ),
    "potassium deficiency": (
        "Potassium Sulfate (SOP) – 5 g/L foliar spray, every 15 days. Cost: ₹200/kg. "
        "Organic: Wood ash 50 g/L soil drench."
    ),
    "sulphur": (
        "Sulfur 80WP – 3 g/L spray, every 15 days. Cost: ₹180/kg. "
        "Organic: Gypsum soil amendment 200 kg/acre."
    ),
    "sulphur deficiency": (
        "Sulfur 80WP – 3 g/L spray, every 15 days. Cost: ₹180/kg. "
        "Organic: Gypsum soil amendment 200 kg/acre."
    ),
    "zinc": (
        "Zinc Sulfate – 2 g/L foliar spray, every 15 days. Cost: ₹120/kg. "
        "Organic: Organic compost improves zinc availability."
    ),
    "zinc deficiency": (
        "Zinc Sulfate – 2 g/L foliar spray, every 15 days. Cost: ₹120/kg. "
        "Organic: Organic compost."
    ),

    # ── ABIOTIC / PHYSIOLOGICAL ───────────────────────────────────
    "yellowish": (
        "Check soil pH (ideal 6.0–7.0) and run a nutrient test. "
        "Apply balanced NPK (19:19:19) – 3 g/L foliar spray. "
        "Ensure adequate irrigation. Consult KVK for soil test."
    ),
    "yellow leaves": (
        "Check soil pH and run nutrient test. Apply balanced NPK – 3 g/L. "
        "Ensure adequate irrigation. Consult KVK for soil test."
    ),
    "dry leaf": (
        "Improve irrigation schedule; apply mulch to conserve moisture. "
        "Check for root rot. No chemical treatment needed."
    ),
    "foliage damaged": (
        "Remove damaged leaves. Apply balanced NPK fertilizer. "
        "No fungicide needed."
    ),
    "scorch": (
        "Provide shade netting during peak afternoon heat. "
        "Increase irrigation frequency. No chemical treatment needed."
    ),
    "death leaf": (
        "Remove dead tissue promptly. Check soil drainage. Apply balanced NPK. "
        "Consult KVK for further diagnosis."
    ),
    "deficiency": (
        "Conduct a full soil test for nutrient deficiencies. "
        "Apply chelated micronutrient mix – 2 g/L foliar spray. "
        "Consult KVK for crop-specific tailored advice."
    ),
}


def _lookup_pesticide(disease: str) -> str:
    """Internal lookup with exact → most-specific-substring fallback."""
    clean = normalize_disease_name(disease).lower()

    # 1. Exact match
    if clean in _PESTICIDE_DB:
        return _PESTICIDE_DB[clean]

    # 2. Substring match – prefer the longest (most specific) key
    matches = [
        (k, v) for k, v in _PESTICIDE_DB.items()
        if k in clean or clean in k
    ]
    if matches:
        return max(matches, key=lambda x: len(x[0]))[1]

    return (
        f"No specific data for '{disease}'. "
        "General advice: apply Copper Oxychloride 3 g/L as a broad-spectrum fallback. "
        "Consult Krishi Vigyan Kendra or call Kisan Call Center: 1800-180-1551 (free, 24×7)."
    )


# ══════════════════════════════════════════════════════════════════
#  WEATHER TOOL  (with 30-minute in-memory TTL cache)
# ══════════════════════════════════════════════════════════════════

_weather_cache: dict[str, tuple[str, float]] = {}
_WEATHER_TTL = 1800  # seconds


class WeatherInput(BaseModel):
    location: str = Field(
        description="Latitude and longitude as 'lat,lng', e.g. '20.5937,78.9629'"
    )


class WeatherTool(BaseTool):
    name: str = "get_weather_forecast"
    description: str = (
        "Get 7-day weather forecast for a lat,lng location. "
        "Input: plain string like '20.5937,78.9629'. Call ONCE only."
    )
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, location: str) -> str:
        # ── Cache check ──────────────────────────────────────────
        cached = _weather_cache.get(location)
        if cached and (time.time() - cached[1]) < _WEATHER_TTL:
            return cached[0]

        try:
            parts = location.split(",")
            if len(parts) != 2:
                return f"Invalid location format '{location}'. Expected 'lat,lng'."
            lat, lng = parts[0].strip(), parts[1].strip()
            float(lat); float(lng)          # validate they are numbers

            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lng}"
                f"&daily=temperature_2m_max,precipitation_sum,windspeed_10m_max"
                f"&timezone=auto&forecast_days=7"
            )
            data = requests.get(url, timeout=10).json()
            daily = data["daily"]
            rows = []
            for i in range(7):
                rain = daily["precipitation_sum"][i]
                wind = daily["windspeed_10m_max"][i]
                safe = "✅ Safe to spray" if rain < 5 and wind < 20 else "❌ Unsafe (rain/wind)"
                rows.append(
                    f"{daily['time'][i]}: {daily['temperature_2m_max'][i]}°C, "
                    f"Rain {rain} mm, Wind {wind} km/h — {safe}"
                )
            result = "\n".join(rows)
            _weather_cache[location] = (result, time.time())
            return result

        except ValueError:
            return f"Location must be numeric lat,lng. Got: '{location}'."
        except Exception as e:
            return f"Weather fetch failed: {e}"


# ══════════════════════════════════════════════════════════════════
#  PESTICIDE PRICE TOOL
# ══════════════════════════════════════════════════════════════════

class PesticideInput(BaseModel):
    disease: str = Field(
        description="Plain disease name string only, e.g. 'Apple Scab'"
    )


class PesticidePriceTool(BaseTool):
    name: str = "get_pesticide_info"
    description: str = (
        "Get pesticide recommendations and prices for a plant disease. "
        "Input must be a plain string disease name, e.g. 'Apple Scab'."
    )
    args_schema: Type[BaseModel] = PesticideInput

    def _run(self, disease: str) -> str:
        return _lookup_pesticide(disease)


# ══════════════════════════════════════════════════════════════════
#  TRANSLATE TOOL  (chunked – no silent 500-char truncation)
# ══════════════════════════════════════════════════════════════════

# Supported Indian language codes for MyMemory API
SUPPORTED_LANGS = {
    "hi": "Hindi",
    "mr": "Marathi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "gu": "Gujarati",
    "bn": "Bengali",
    "pa": "Punjabi",
}


def _chunk_text(text: str, max_chars: int = 480) -> list[str]:
    """Split text at sentence/newline boundaries to fit MyMemory's per-request limit."""
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) <= max_chars:
            current += line
        else:
            if current:
                chunks.append(current.strip())
            current = line if len(line) <= max_chars else line[:max_chars]
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text[:max_chars]]


class TranslateInput(BaseModel):
    text: str = Field(description="English text to translate")
    target_lang: str = Field(
        default="hi",
        description=(
            "Target language code: hi=Hindi, mr=Marathi, te=Telugu, "
            "ta=Tamil, kn=Kannada, gu=Gujarati, bn=Bengali, pa=Punjabi"
        ),
    )


class TranslateTool(BaseTool):
    name: str = "translate_report"
    description: str = (
        "Translate the farmer report into the specified Indian language. "
        "Pass the full report text and a target_lang code. Call ONCE only."
    )
    args_schema: Type[BaseModel] = TranslateInput

    def _run(self, text: str, target_lang: str = "hi") -> str:
        lang = target_lang.lower().strip()
        if lang not in SUPPORTED_LANGS:
            lang = "hi"         # graceful fallback to Hindi

        chunks = _chunk_text(text)
        translated_parts: list[str] = []

        for chunk in chunks:
            try:
                resp = requests.get(
                    "https://api.mymemory.translated.net/get",
                    params={"q": chunk, "langpair": f"en|{lang}"},
                    timeout=10,
                )
                data = resp.json()
                part = data.get("responseData", {}).get("translatedText", "")
                translated_parts.append(part if part else chunk)
            except Exception:
                translated_parts.append(chunk)     # fallback: keep original chunk

        return "\n".join(translated_parts) if translated_parts else text