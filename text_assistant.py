import re
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# =====================================================================
# COMPREHENSIVE MULTILINGUAL AGRICULTURAL KNOWLEDGE BASE
# Covers: English, Telugu (తెలుగు), and Romanized Telugu (Tanglish)
# =====================================================================

CROP_KNOWLEDGE = {
    "rice": {
        "names": ["rice", "paddy", "vari", "వరి", "బియ్యం", "ధాన్యం", "biyyam", "dhanyam"],
        "cultivation": {
            "en": (
                "🌾 **Rice / Paddy (వరి) Cultivation Guide:**\n\n"
                "• **Best Season:** Kharif (June-July sowing) and Rabi (Nov-Dec sowing).\n"
                "• **Seed Rate:** 20-25 kg/acre for normal transplanting; 2-3 kg/acre for direct seeding / SRI method.\n"
                "• **Seed Treatment:** Carbendazim 2g/kg seed or Trichoderma viride 10g/kg.\n"
                "• **Nursery Care:** Transplant 20-25 day old seedlings (2-3 seedlings per hill).\n"
                "• **Spacing:** 20 x 15 cm or 25 x 25 cm (SRI).\n"
                "• **Water Management:** Maintain 2-3 cm standing water from tillering until flowering. Drain field 10 days before harvest."
            ),
            "te": (
                "🌾 **వరి సాగు సమగ్ర యాజమాన్యం:**\n\n"
                "• **విత్తే కాలం:** ఖరీఫ్ (జూన్-జూలై), రబీ (నవంబర్-డిసెంబర్).\n"
                "• **విత్తన మోతాదు:** ఎకరానికి 20-25 కిలోలు (శ్రీ వరి పద్ధతిలో 2-3 కిలోలు సరిపోతాయి).\n"
                "• **విత్తన శుద్ధి:** కిలో విత్తనానికి 2 గ్రాముల కార్బండిజమ్ లేదా 10 గ్రాముల ట్రైకోడెర్మా విరిడెతో శుద్ధి చేయాలి.\n"
                "• **నాటు పద్ధతి:** 20-25 రోజుల నారును చదరపు మీటరుకు 33 కుదుళ్లు ఉండేలా నాటుకోవాలి.\n"
                "• **నీటి యాజమాన్యం:** పిలకలు తొడిగే దశ మరియు పూత దశలో 2-3 సెం.మీ నీరు నిల్వ ఉంచాలి. కోతకు 10 రోజుల ముందు నీటిని తీసివేయాలి."
            )
        },
        "fertilizer": {
            "en": (
                "🧪 **Fertilizer Dose for Rice (Per Acre):**\n\n"
                "• **Basal Dose (ఆఖరి దుక్కిలో):** DAP 50 kg + MOP (Potash) 25 kg + Zinc Sulphate 10 kg.\n"
                "• **1st Top Dressing (Tillering - 20-25 days):** Urea 35 kg.\n"
                "• **2nd Top Dressing (Panicle Initiation - 45-50 days):** Urea 30 kg + Potash 15 kg.\n"
                "• **Organic Advice:** Apply 4-5 tonnes Farmyard Manure (FYM) or Vermicompost before final puddling."
            ),
            "te": (
                "🧪 **వరిలో ఎరువుల మోతాదు (ఎకరానికి):**\n\n"
                "• **ఆఖరి దుక్కిలో:** డీఏపీ (DAP) 50 కిలోలు + పొటాష్ 25 కిలోలు + జింక్ సల్ఫేట్ 10 కిలోలు తప్పనిసరిగా వేయాలి.\n"
                "• **మొదటి దఫా (20-25 రోజులకు):** యూరియా 35 కిలోలు వేయాలి.\n"
                "• **రెండవ దఫా (చిరుపొట్ట దశలో - 45-50 రోజులకు):** యూరియా 30 కిలోలు + పొటాష్ 15 కిలోలు వేయాలి.\n"
                "• **సేంద్రీయ ఎరువు:** ఎకరానికి 4-5 టన్నుల పశువుల ఎరువును ఆఖరి దుక్కిలో కలపాలి."
            )
        },
        "pest": {
            "en": (
                "🛡️ **Rice Pest & Disease Management:**\n\n"
                "• **Stem Borer (కాండం తొలుచు పురుగు - Dead heart / White earhead):** Apply Cartap Hydrochloride 4G @ 8 kg/acre or Chlorantraniliprole 0.4% G @ 4 kg/acre.\n"
                "• **Brown Plant Hopper (BPH - సుడి దోమ):** Spray Pymetrozine 50% WG @ 120g/acre or Dinotefuran 20% SG @ 80g/acre directly at base of plants.\n"
                "• **Blast Disease (అగ్గి తెగులు):** Spray Tricyclazole 75% WP @ 120g/acre.\n"
                "• **Sheath Blight (మచ్చ తెగులు):** Spray Hexaconazole 5% EC @ 400ml/acre."
            ),
            "te": (
                "🛡️ **వరిలో తెగుళ్ళు మరియు పురుగుల సమగ్ర నివారణ:**\n\n"
                "• **కాండం తొలుచు పురుగు (Stem Borer):** ఎకరానికి కార్టాప్ హైడ్రోక్లోరైడ్ 4G గుళికలు 8 కిలోలు లేదా క్లోరాంట్రానిలిప్రోల్ 4 కిలోలు చల్లాలి.\n"
                "• **సుడి దోమ (BPH):** పిలకల మొదళ్ళలో పడేలా పైమెట్రోజైన్ 50% WG 120 గ్రాములు లేదా డైనోటెఫ్యూరాన్ 80 గ్రాములు పిచికారీ చేయాలి.\n"
                "• **అగ్గి తెగులు (Blast):** ట్రైసైక్లాజోల్ 75% WP 120 గ్రాములు ఎకరానికి పిచికారీ చేయాలి.\n"
                "• **సేంద్రీయ నివారణ:** వేప నూనె (Neem oil 10,000 ppm) 2 మి.లీ లీటరు నీటికి కలిపి పిచికారీ చేయాలి."
            )
        }
    },

    "tomato": {
        "names": ["tomato", "tomatoes", "tamata", "టమాటా", "టమోటా", "tamota", "thakkali"],
        "cultivation": {
            "en": (
                "🍅 **Tomato (టమాటా) Cultivation Guidelines:**\n\n"
                "• **High-Yield Hybrids:** US-440, Saaho, Arka Rakshak, Abhinav, Pahuja.\n"
                "• **Seed Rate:** 60-80 grams/acre for hybrid seed.\n"
                "• **Nursery:** Raise seedlings in pro-trays with cocopeat for 25-30 days.\n"
                "• **Spacing:** 90 x 45 cm on raised beds with drip irrigation and silver-black mulch sheet.\n"
                "• **Staking:** Trellising with bamboo poles and wire increases marketable yield by over 35%."
            ),
            "te": (
                "🍅 **టమాటా సాగు మెళకువలు:**\n\n"
                "• **ప్రధాన హైబ్రిడ్ రకాలు:** సాహో, యుఎస్-440, అర్క రక్షక్, అభినవ్.\n"
                "• **విత్తన మోతాదు:** ఎకరానికి 60-80 గ్రాములు.\n"
                "• **నారు పెంపకం:** ప్రో-ట్రేలలో కోకోపీట్ తో 25-30 రోజుల ఆరోగ్యకరమైన నారును పెంచాలి.\n"
                "• **నాటే విధానం:** బోదెలపై 90 x 45 సెం.మీ దూరంలో మల్చింగ్ షీట్ ఉపయోగించి నాటాలి.\n"
                "• **కర్రలు కట్టడం (Staking):** వెదురు కర్రలు మరియు తాళ్ళతో కట్టడం వల్ల కాయలు నేలకు తగలకుండా నాణ్యమైన దిగుబడి వస్తుంది."
            )
        },
        "fertilizer": {
            "en": (
                "🧪 **Fertilizer Schedule for Tomato (Per Acre):**\n\n"
                "• **Basal:** 10 tonnes Farmyard Manure + DAP 50 kg + Potash 40 kg + Micronutrient mix 10 kg.\n"
                "• **Vegetative Growth:** 19:19:19 water-soluble fertilizer @ 3 kg/acre per week via drip.\n"
                "• **Flowering & Fruit Setting:** 13:0:45 (Potassium Nitrate) @ 4 kg/acre + 0:52:34 @ 3 kg/acre."
            ),
            "te": (
                "🧪 **టమాటా ఎరువుల యాజమాన్యం (ఎకరానికి):**\n\n"
                "• **ఆఖరి దుక్కిలో:** 10 టన్నుల పశువుల ఎరువు + డీఏపీ 50 కిలోలు + పొటాష్ 40 కిలోలు + సూక్ష్మపోషకాల మిశ్రమం 10 కిలోలు.\n"
                "• **ఎదుగుదల దశలో:** 19:19:19 నీటిలో కరిగే ఎరువును వారానికి 3 కిలోలు డ్రిప్ ద్వారా అందించాలి.\n"
                "• **పూత, కాయ దశలో:** 13:0:45 పొటాషియం నైట్రేట్ ఎరువును ఎకరానికి 4 కిలోలు అందించాలి."
            )
        },
        "pest": {
            "en": (
                "🛡️ **Tomato Pest & Disease Control:**\n\n"
                "• **Leaf Curl Virus (ఆకుముడత):** Spread by Whitefly. Install Yellow Sticky Traps (25/acre) + Spray Imidacloprid 17.8% SL @ 0.5ml/litre or Diafenthiuron @ 1.25g/litre.\n"
                "• **Early / Late Blight (ఆకుమచ్చ తెగులు):** Spray Copper Oxychloride (COC) @ 3g/litre or Mancozeb @ 2.5g/litre.\n"
                "• **Fruit Borer (కాయ తొలుచు పురుగు):** Spray Emamectin Benzoate 5% SG @ 0.5g/litre or Flubendiamide @ 0.5ml/litre."
            ),
            "te": (
                "🛡️ **టమాటాలో తెగుళ్ళు & పురుగుల నివారణ:**\n\n"
                "• **ఆకుముడత తెగులు (Leaf Curl):** తెల్లదోమ ద్వారా వ్యాపిస్తుంది. ఎకరానికి 25 పసుపు రంగు జిగురు అట్టలు పెట్టాలి + ఇమిడాక్లోప్రిడ్ 0.5 మి.లీ లీటరు నీటికి కలపాలి.\n"
                "• **ఆకుమచ్చ తెగులు (Blight):** కాపర్ ఆక్సీక్లోరైడ్ 3 గ్రాములు లేదా మాంకోజెబ్ 2.5 గ్రాములు లీటరు నీటికి పిచికారీ చేయాలి.\n"
                "• **కాయ తొలుచు పురుగు:** ఎమామెక్టిన్ బెంజోయేట్ 5% SG 0.5 గ్రాములు లీటరు నీటికి పిచికారీ చేయాలి."
            )
        }
    },

    "chilli": {
        "names": ["chilli", "chili", "mirchi", "మిర్చి", "మిరప", "pachi mirchi", "green chilli"],
        "cultivation": {
            "en": (
                "🌶️ **Chilli (మిర్చి) Cultivation Best Practices:**\n\n"
                "• **Top Commercial Varieties:** Teja, Armoor, Guntur Hope, Indo-US 5, Byadgi.\n"
                "• **Nursery:** Transplant 35-40 day old seedlings into raised beds.\n"
                "• **Spacing:** 60 x 45 cm or 75 x 45 cm paired rows with drip irrigation.\n"
                "• **Mulching:** Silver-black plastic mulch sheet conserves moisture and suppresses weeds."
            ),
            "te": (
                "🌶️ **మిర్చి సాగు ఉత్తమ యాజమాన్య పద్ధతులు:**\n\n"
                "• **ప్రధాన వాణిజ్య రకాలు:** తేజ, ఆర్మూర్, గుంటూరు హోప్, బ్యాడగి.\n"
                "• **నాటు విధానం:** 35-40 రోజుల నారును బోదెలపై 60 x 45 సెం.మీ దూరంలో నాటాలి.\n"
                "• **మల్చింగ్ షీట్:** సిల్వర్-బ్లాక్ మల్చింగ్ షీట్ వాడితే కలుపు లేకుండా తేమ నిలిచి అధిక దిగుబడి వస్తుంది."
            )
        },
        "fertilizer": {
            "en": (
                "🧪 **Fertilizer Schedule for Chilli:**\n\n"
                "• **Basal:** DAP 50 kg + Potash 30 kg + Neem Cake 100 kg + Sulphur 10 kg.\n"
                "• **Flower Retention:** Spray Planofix (NAA) @ 0.25ml/litre or 13:0:45 @ 5g/litre + Boron @ 1g/litre to stop flower dropping."
            ),
            "te": (
                "🧪 **మిర్చిలో ఎరువుల యాజమాన్యం:**\n\n"
                "• **దుక్కిలో:** డీఏపీ 50 కిలోలు + పొటాష్ 30 కిలోలు + వేపపిండి 100 కిలోలు + సల్ఫర్ 10 కిలోలు.\n"
                "• **పూత రాలకుండా:** ప్లానోఫిక్స్ 0.25 మి.లీ లేదా 13:0:45 (5 గ్రాములు) మరియు బోరాన్ (1 గ్రాము) లీటరు నీటికి కలిపి పిచికారీ చేయాలి."
            )
        },
        "pest": {
            "en": (
                "🛡️ **Chilli Black Thrips & Mites Control:**\n\n"
                "• **Black Thrips (నల్ల తామర పురుగు):** Install Blue Sticky Traps (30/acre). Spray Spinetoram 11.7% SC @ 1ml/litre or Fipronil 5% SC @ 2ml/litre.\n"
                "• **Yellow / White Mites (నల్లి):** Spray Diafenthiuron 50% WP @ 1.25g/litre or Spiromesifen @ 1ml/litre.\n"
                "• **Dieback / Fruit Rot (కొమ్మ ఎండు తెగులు):** Spray Azoxystrobin + Difenoconazole @ 1ml/litre."
            ),
            "te": (
                "🛡️ **మిర్చిలో నల్ల తామర పురుగులు & నల్లి నివారణ:**\n\n"
                "• **నల్ల తామర పురుగు (Black Thrips):** ఎకరానికి 30 నీలి రంగు జిగురు అట్టలు (Blue Sticky Traps) పెట్టాలి + స్పినెటోరమ్ 1 మి.లీ లీటరు నీటికి కలిపి పిచికారీ చేయాలి.\n"
                "• **నల్లి పురుగు (Mites):** డయాఫెంథియురాన్ 1.25 గ్రాములు లేదా స్పైరోమెసిఫెన్ 1 మి.లీ పిచికారీ చేయాలి.\n"
                "• **కొమ్మ ఎండు తెగులు:** అజాక్సిస్ట్రోబిన్ + డైఫెనోకోనజోల్ 1 మి.లీ లీటరు నీటికి కలిపి పిచికారీ చేయాలి."
            )
        }
    },

    "cotton": {
        "names": ["cotton", "kapas", "patti", "పత్తి", "దూది"],
        "cultivation": {
            "en": (
                "🌱 **Cotton (పత్తి) Cultivation Guide:**\n\n"
                "• **Soil:** Deep Black cotton soils with good drainage.\n"
                "• **Spacing:** 90 x 60 cm for Bt hybrids.\n"
                "• **Topping (Nipping):** Cut terminal shoot at 80-90 days to promote boll development.\n"
                "• **Critical Irrigation:** Square formation, flowering, and boll development stages."
            ),
            "te": (
                "🌱 **పత్తి సాగు సమగ్ర సమాచారం:**\n\n"
                "• **అనుకూల నేలలు:** నల్లరేగడి నేలలు చాలా అనుకూలం.\n"
                "• **విత్తే ఎడం:** 90 x 60 సెం.మీ దూరంలో విత్తుకోవాలి.\n"
                "• **కొనలు తుంచడం (Topping):** 80-90 రోజుల వయసులో ప్రధాన కాండం కొనను తుంచితే కాయల సంఖ్య పెరుగుతుంది."
            )
        },
        "pest": {
            "en": (
                "🛡️ **Cotton Pink Bollworm & Sucking Pests:**\n\n"
                "• **Pink Bollworm (గులాబీ రంగు పురుగు):** Install Pheromone Traps (8/acre) + Spray Profenofos 50% EC @ 2ml/litre or Emamectin Benzoate.\n"
                "• **Whitefly & Aphids (తెల్లదోమ):** Spray Flonicamid 50% WG @ 0.3g/litre."
            ),
            "te": (
                "🛡️ **పత్తిలో గులాబీ రంగు పురుగు & రసం పీల్చే పురుగుల నివారణ:**\n\n"
                "• **గులాబీ రంగు కాయ తొలుచు పురుగు:** ఎకరానికి 8 లింగాకర్షక బుట్టలు (Pheromone Traps) పెట్టాలి + ప్రొఫెనోఫాస్ 2 మి.లీ పిచికారీ చేయాలి.\n"
                "• **తెల్లదోమ, పేనుబంక:** ఫ్లోనికామిడ్ 50% WG 0.3 గ్రాములు లీటరు నీటికి పిచికారీ చేయాలి."
            )
        }
    },

    "maize": {
        "names": ["maize", "corn", "mokkajonna", "మొక్కజొన్న", "జొన్న", "jonna"],
        "cultivation": {
            "en": (
                "🌽 **Maize (మొక్కజొన్న) Cultivation:**\n\n"
                "• **Seed Rate:** 7-8 kg/acre.\n"
                "• **Spacing:** 60 x 20 cm.\n"
                "• **Fertilizer:** Urea 75 kg + DAP 50 kg + Potash 25 kg + Zinc 10 kg/acre."
            ),
            "te": (
                "🌽 **మొక్కజొన్న సాగు పద్ధతులు:**\n\n"
                "• **విత్తన మోతాదు:** ఎకరానికి 7-8 కిలోలు.\n"
                "• **ఎడం:** 60 x 20 సెం.మీ దూరంలో బోదెలపై విత్తుకోవాలి.\n"
                "• **ఎరువులు:** ఎకరానికి 75 కిలోల యూరియా, 50 కిలోల DAP, 25 కిలోల పొటాష్, 10 కిలోల జింక్ వేయాలి."
            )
        },
        "pest": {
            "en": (
                "🛡️ **Fall Armyworm (కత్తెర పురుగు) in Maize:**\n\n"
                "• Spray Chlorantraniliprole 18.5% SC @ 0.4ml/litre or Emamectin Benzoate 5% SG @ 0.5g/litre into plant whorls (సుడిలో పడేలా)."
            ),
            "te": (
                "🛡️ **మొక్కజొన్నలో కత్తెర పురుగు నివారణ:**\n\n"
                "• క్లోరాంట్రానిలిప్రోల్ 0.4 మి.లీ లేదా ఎమామెక్టిన్ బెంజోయేట్ 0.5 గ్రాములు లీటరు నీటికి కలిపి మొక్క సుడులలో పడేలా పిచికారీ చేయాలి."
            )
        }
    },

    "onion": {
        "names": ["onion", "onions", "ulli", "ఉల్లి", "ఉల్లిపాయ", "ullipaya", "ulligadda"],
        "cultivation": {
            "en": (
                "🧅 **Onion (ఉల్లి) Farming Guide:**\n\n"
                "• **Nursery:** 40-45 day old healthy seedlings.\n"
                "• **Spacing:** 15 x 10 cm.\n"
                "• **Pre-Harvest:** Stop irrigation 10-15 days before harvest for longer shelf life."
            ),
            "te": (
                "🧅 **ఉల్లి సాగు యాజమాన్యం:**\n\n"
                "• **నారు వయసు:** 40-45 రోజుల నారును 15 x 10 సెం.మీ దూరంలో నాటాలి.\n"
                "• **కోతకు ముందు:** ఉల్లి తీయడానికి 10-15 రోజుల ముందు నీరు కట్టడం ఆపితే నిల్వ సామర్థ్యం పెరుగుతుంది."
            )
        }
    },

    "groundnut": {
        "names": ["groundnut", "peanut", "verusanaga", "వేరుశనగ", "పల్లీ", "palli"],
        "cultivation": {
            "en": (
                "🥜 **Groundnut (వేరుశనగ) Management:**\n\n"
                "• **Gypsum Application:** Apply 200 kg/acre Gypsum at 40-45 days (flowering/pegging) for bold pods and high oil percentage.\n"
                "• **Seed Treatment:** Trichoderma viride 10g/kg seed."
            ),
            "te": (
                "🥜 **వేరుశనగ సాగు మెళకువలు:**\n\n"
                "• **జిప్సం ప్రాముఖ్యత:** ఊడలు దిగే దశలో (40-45 రోజులకు) ఎకరానికి 200 కిలోల జిప్సం వేస్తే కాయ బాగా ఊరి నూనె శాతం పెరుగుతుంది.\n"
                "• **విత్తన శుద్ధి:** కిలో విత్తనానికి 10 గ్రాముల ట్రైకోడెర్మా విరిడె కలపాలి."
            )
        }
    }
}

# General Topics
TOPICS_KNOWLEDGE = {
    "scheme": {
        "en": (
            "🏛️ **Government Agricultural Schemes for Farmers:**\n\n"
            "1. **PM-KISAN:** ₹6,000 per year direct income support in 3 equal installments.\n"
            "2. **Rythu Bharosa / State Input Assistance:** Direct financial assistance for farm seeds and inputs.\n"
            "3. **Micro-Irrigation Subsidy:** 70% to 90% subsidy on Drip and Sprinkler systems.\n"
            "4. **PM Fasal Bima Yojana (PMFBY):** Comprehensive crop insurance covering drought, floods, and unseasonal rains.\n"
            "5. **Kisan Credit Card (KCC):** Agricultural crop loans at an effective 4% interest rate."
        ),
        "te": (
            "🏛️ **రైతులకు ముఖ్యమైన ప్రభుత్వ సంక్షేమ పథకాలు:**\n\n"
            "1. **పీఎం కిసాన్ (PM-KISAN):** ప్రతి రైతు ఖాతాలో సంవత్సరానికి ₹6,000 నగదు జమ (3 విడతలలో ₹2,000 చొప్పున).\n"
            "2. **రైతు భరోసా / పెట్టుబడి సాయం:** విత్తనాలు, ఎరువుల కొనుగోలుకు ఆర్థిక సహాయం.\n"
            "3. **డ్రిప్ ఇరిగేషన్ రాయితీ:** బిందు సేద్యం (Drip) మరియు స్ప్రింక్లర్లపై 70% నుండి 90% వరకు ప్రభుత్వ సబ్సిడీ.\n"
            "4. **ప్రధానమంత్రి ఫసల్ బీమా యోజన:** పంట నష్టపోయినప్పుడు ప్రభుత్వం అందించే బీమా పరిహారం.\n"
            "5. **కిసాన్ క్రెడిట్ కార్డు (KCC):** కేవలం 4% నామమాత్రపు వడ్డీతో బ్యాంక్ పంట రుణాలు."
        )
    },
    "organic": {
        "en": (
            "🌿 **Organic & Natural Farming Methods:**\n\n"
            "• **Jeevamrutham (జీవామృతం):** Cow dung (10kg), cow urine (10L), jaggery (2kg), pulse flour (2kg), soil (handful) fermented in 200L water for 48 hours. Excellent soil microbe booster.\n"
            "• **Neem Seed Kernel Extract (NSKE 5%):** Highly effective against leafhoppers, whiteflies, and bollworms.\n"
            "• **Panchagavya:** Natural plant immunity and flowering stimulant.\n"
            "• **Vermicompost:** 2 tonnes/acre restores soil organic carbon."
        ),
        "te": (
            "🌿 **సేంద్రీయ మరియు ప్రకృతి వ్యవసాయ పద్ధతులు:**\n\n"
            "• **జీవామృతం:** ఆవు పేడ (10 కేజీలు), ఆవు మూత్రం (10 లీటర్లు), బెల్లం (2 కేజీలు), పప్పుపిండి (2 కేజీలు), పుట్టమట్టితో తయారుచేసే ద్రావణం భూసారాన్ని రెట్టింపు చేస్తుంది.\n"
            "• **వేప నూనె / కషాయం (NSKE 5%):** రసం పీల్చే పురుగులు, ఆకుతినే పురుగులను సహజంగా నివారిస్తుంది.\n"
            "• **పంచగవ్య:** మొక్కల రోగనిరోధక శక్తిని పెంచి పూత, కాయ రాలకుండా కాపాడుతుంది.\n"
            "• **వర్మీకంపోస్ట్:** ఎకరానికి 2 టన్నులు వాడితే నేలలో తేమ నిల్వ సామర్థ్యం పెరుగుతుంది."
        )
    },
    "soil": {
        "en": (
            "🌱 **Soil Testing & Soil Health Card:**\n\n"
            "• **Sample Collection:** Collect 'V' shaped soil slices from 6-8 spots up to 15 cm depth.\n"
            "• **Tested Parameters:** Nitrogen (N), Phosphorus (P), Potassium (K), Soil pH, Organic Carbon, Zinc.\n"
            "• **Benefits:** Prevents excess fertilizer wastage, cuts input cost by 25%, and preserves long-term farm fertility."
        ),
        "te": (
            "🌱 **మట్టి పరీక్ష (Soil Health Card) విధానం & లాభాలు:**\n\n"
            "• **నమూనా సేకరణ:** పొలంలో 6-8 చోట్ల 'V' ఆకారంలో 15 సెం.మీ లోతు వరకు మట్టిని సేకరించి బాగా కలపాలి.\n"
            "• **పరీక్షించే పోషకాలు:** నత్రజని (N), భాస్వరం (P), పొటాష్ (K), మట్టి pH, కర్బన శాతం మరియు జింక్.\n"
            "• **లాభాలు:** ఏ ఎరువు ఎంత మోతాదులో వాడాలో తెలుస్తుంది, ఎరువుల ఖర్చు 25% తగ్గుతుంది."
        )
    },
    "weed": {
        "en": (
            "🌿 **Comprehensive Weed Management & Herbicides Guide:**\n\n"
            "• **Pre-emergence (విత్తిన 48 గంటల్లో):** Pendimethalin 30% EC @ 1.0 to 1.3 liters/acre in moist soil (Paddy, Cotton, Chilli, Groundnut, Maize).\n"
            "• **Paddy Post-emergence (వరిలో మొలకల తర్వాత 15-20 రోజులకు):** Bispyribac Sodium 10% SC (Nominee Gold) @ 100-120 ml/acre or Pyrazosulfuron Ethyl 10% WP @ 80g/acre.\n"
            "• **Broadleaf Weeds (వెడల్పాకు కలుపు):** 2,4-D Sodium Salt @ 400g/acre or Metsulfuron Methyl 20% WP @ 8g/acre.\n"
            "• **Grassy Weeds in Cotton/Chilli/Pulses:** Quizalofop-ethyl 5% EC @ 300-400 ml/acre or Propaquizafop 10% EC @ 250 ml/acre.\n"
            "• **Organic/Physical Advice:** Use plastic mulch film (30 micron) with drip lines to permanently suppress 90% of weeds without spray."
        ),
        "te": (
            "🌿 **పంటలలో సమగ్ర కలుపు నివారణ మందులు (Weed Management):**\n\n"
            "• **మొలకల ముందు (ఆఖరి దుక్కి/నాటిన 48 గంటల్లో):** పెండిమిథాలిన్ 30% EC ఎకరానికి 1 నుండి 1.3 లీటర్లు తడి నేలపై పిచికారీ చేయాలి (వరి, పత్తి, మిర్చి, వేరుశనగ, మొక్కజొన్నలకు).\n"
            "• **వరిలో మొలకల తర్వాత (15-20 రోజులకు):** బిస్పైరిబాక్ సోడియం 10% SC (నామినీ గోల్డ్) 100-120 మి.లీ లేదా పైరజోసల్ఫ్యూరాన్ ఇథైల్ 80 గ్రాములు పిచికారీ చేయాలి.\n"
            "• **వెడల్పాకు కలుపు నివారణకు:** 2,4-D సోడియం సాల్ట్ 400 గ్రాములు లేదా మెట్సల్ఫ్యూరాన్ మిథైల్ 8 గ్రాములు వాడాలి.\n"
            "• **మిర్చి, పత్తి, పప్పుదినుసుల్లో గడ్డిజాతి కలుపునకు:** క్విజాలోఫాప్ ఇథైల్ 5% EC ఎకరానికి 350-400 మి.లీ పిచికారీ చేయాలి.\n"
            "• **సేంద్రీయ సూచన:** డ్రిప్ తో పాటు సిల్వర్-బ్లాక్ ప్లాస్టిక్ మల్చింగ్ షీట్ వాడితే 90% కలుపు సమస్య సహజంగానే నివారింపబడుతుంది."
        )
    },
    "profit": {
        "en": (
            "💰 **High-Profit Commercial Crops Analysis (Per Acre):**\n\n"
            "1. **🌶️ Hybrid Chilli (గుంటూరు మిర్చి):**\n"
            "   • Average Yield: 25-35 Quintals dry chilli/acre.\n"
            "   • Market Price: ₹14,000 - ₹22,000 per Quintal.\n"
            "   • **Net Profit: ₹1.5 Lakh to ₹2.5 Lakhs per acre.**\n\n"
            "2. **🍅 High-Tech Mulched Tomato:**\n"
            "   • Trellised Drip yield: 25-35 Tonnes/acre.\n"
            "   • Price: ₹15 - ₹40/kg during market demand peaks.\n"
            "   • **Net Profit: ₹1.0 Lakh to ₹1.8 Lakhs per acre.**\n\n"
            "3. **🌿 Turmeric (పసుపు) & Ginger (అల్లం):**\n"
            "   • Long duration 8-9 months, highly stable price.\n"
            "   • **Net Profit: ₹1.8 Lakh to ₹3.0 Lakhs per acre.**\n\n"
            "4. **🍌 Tissue Culture Banana (G-9):**\n"
            "   • 1,200 plants/acre, bunch weight 25-30 kg.\n"
            "   • **Net Profit: ₹1.5 Lakh to ₹2.2 Lakhs per acre.**\n\n"
            "5. **🍉 Summer Watermelon (పుచ్చకాయ):**\n"
            "   • Fast 65-75 day short cycle crop.\n"
            "   • **Net Profit: ₹60,000 to ₹1,00,000 per acre.**"
        ),
        "te": (
            "💰 **ఎక్కువ లాభాలనిచ్చే వాణిజ్య పంటల విశ్లేషణ (ఎకరానికి నికర లాభం):**\n\n"
            "1. **🌶️ హైబ్రిడ్ మిర్చి (గుంటూరు తేజ / సెంజెంటా 5531):**\n"
            "   • ఎండుమిర్చి సగటు దిగుబడి: 25-35 క్వింటాళ్లు.\n"
            "   • సగటు క్వింటాల్ ధర: ₹15,000 నుండి ₹24,000.\n"
            "   • **నికర లాభం: ఎకరానికి ₹1.5 లక్షల నుండి ₹2.5 లక్షలు.**\n\n"
            "2. **🍅 మల్చింగ్ & డ్రిప్ టమాటా (సాహో / US-440):**\n"
            "   • దిగుబడి: 25-35 టన్నులు.\n"
            "   • రేటు సీజన్ బట్టి కిలో ₹15 నుండి ₹45 వరకు ఉంటుంది.\n"
            "   • **నికర లాభం: ఎకరానికి ₹1.0 లక్ష నుండి ₹1.8 లక్షలు.**\n\n"
            "3. **🌿 పసుపు (Turmeric) మరియు అల్లం (Ginger):**\n"
            "   • స్థిరమైన మార్కెట్ ధర ఉండే సుగంధ ద్రవ్య పంటలు.\n"
            "   • **నికర లాభం: ఎకరానికి ₹1.8 లక్షల నుండి ₹3.0 లక్షలు.**\n\n"
            "4. **🍌 టిష్యూ కల్చర్ అరటి (గ్రాండ్ నైన్ - G9):**\n"
            "   • ఎకరానికి 1,200 మొక్కలు, గెల బరువు 25-32 కిలోలు.\n"
            "   • **నికర లాభం: ఎకరానికి ₹1.5 లక్షల నుండి ₹2.2 లక్షలు.**\n\n"
            "5. **🍉 వేసవి పుచ్చకాయ (Watermelon):**\n"
            "   • కేవలం 65-75 రోజుల్లో వచ్చే స్వల్పకాలిక పంట.\n"
            "   • **నికర లాభం: ఎకరానికి ₹60,000 నుండి ₹1,00,000.**"
        )
    },
    "app_guide": {
        "en": (
            "📱 **How to Use AgriMarket Intelligence:**\n\n"
            "• **📊 Dashboard:** Overview of active crops, sales transactions, and ML prediction summaries.\n"
            "• **🌱 My Crops:** View, manage, or delete registered crops.\n"
            "• **➕ Add Crop:** Add crop details (planting date, harvest date, land area) to MySQL.\n"
            "• **📈 Price Prediction:** XGBoost ML model forecasts APMC mandi prices per Quintal & per Kg.\n"
            "• **📊 Demand Forecasting:** XGBoost ML forecasts market arrival volumes.\n"
            "• **🏪 Market Intelligence:** Real-time APMC Mandi price comparison across Indian markets.\n"
            "• **🌾 Crop Recommendation:** Scientific ML model recommends crops using soil N-P-K and climate data.\n"
            "• **🎤 Voice Assistant:** Speak in Telugu or English to get instant agricultural advice."
        ),
        "te": (
            "📱 **అగ్రిమార్కెట్ ఇంటెలిజెన్స్ ను ఎలా ఉపయోగించాలి:**\n\n"
            "• **📊 Dashboard:** మీ పంటలు, లావాదేవీలు మరియు AI ప్రిడిక్షన్ల సారాంశం.\n"
            "• **🌱 My Crops:** మీ పొలంలోని పంటల వివరాలు చూడటానికి మరియు నిర్వహించడానికి.\n"
            "• **➕ Add Crop:** కొత్త పంట వివరాలను డేటాబేస్ లో సేవ్ చేయడానికి.\n"
            "• **📈 Price Prediction:** XGBoost మోడల్ ద్వారా భవిష్యత్ మార్కెట్ ధరల అంచనా.\n"
            "• **📊 Demand Forecasting:** మార్కెట్ డిమాండ్ అంచనా.\n"
            "• **🏪 Market Intelligence:** అసలైన ప్రభుత్వ మండి మార్కెట్ల ధరల పోలిక.\n"
            "• **🌾 Crop Recommendation:** మట్టి పోషకాలు (N-P-K) ఆధారంగా సరిపోయే పంటల సిఫార్సు.\n"
            "• **🎤 Voice Assistant:** తెలుగులో మాట్లాడి వ్యవసాయ సమాధానాలు పొందవచ్చు."
        )
    }
}


def get_live_mandi_prices(crop_name, language="English"):
    """Query real APMC mandi dataset for prices."""
    csv_cleaned = BASE_DIR / "data" / "mandi_prices_cleaned.csv"
    csv_raw = BASE_DIR / "data" / "mandi_prices.csv"
    csv_path = csv_cleaned if csv_cleaned.exists() else csv_raw

    if not csv_path.exists():
        return None

    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip().str.replace("_x0020_", "_", regex=False)

        commodity_col = next((c for c in df.columns if c.lower() == "commodity"), None)
        price_col = next((c for c in df.columns if "modal" in c.lower()), None)
        if not price_col:
            price_col = next((c for c in df.columns if "price" in c.lower()), None)

        if not commodity_col or not price_col:
            return None

        pattern = crop_name
        if crop_name.lower() in ["rice", "paddy"]:
            pattern = "Rice|Paddy"
        elif crop_name.lower() in ["chilli", "mirchi"]:
            pattern = "Chilli|Chili"

        matches = df[df[commodity_col].str.contains(pattern, case=False, na=False)].dropna(subset=[price_col])

        if matches.empty:
            return None

        matches[price_col] = pd.to_numeric(matches[price_col], errors="coerce")
        matches = matches.sort_values(by=price_col, ascending=False).head(5)

        is_telugu = (language == "Telugu")
        if is_telugu:
            msg = f"📊 **{crop_name}** తాజా APMC మండి మార్కెట్ ధరలు (క్వింటాల్ కి / 100 కేజీలు):\n\n"
            for _, r in matches.iterrows():
                mkt = r.get("Market", "మండి")
                dist = r.get("District", "")
                stt = r.get("State", "")
                p = r.get(price_col, 0)
                msg += f"- 📍 **{mkt}** ({dist}, {stt}): **₹ {p:,.0f} / Qtl** (కిలో ₹ {p/100.0:.2f})\n"
            return msg
        else:
            msg = f"📊 **{crop_name}** Live APMC Mandi Market Prices (per Quintal / 100 kg):\n\n"
            for _, r in matches.iterrows():
                mkt = r.get("Market", "Mandi")
                dist = r.get("District", "")
                stt = r.get("State", "")
                p = r.get(price_col, 0)
                msg += f"- 📍 **{mkt}** ({dist}, {stt}): **₹ {p:,.0f} / Qtl** (₹ {p/100.0:.2f} / kg)\n"
            return msg

    except Exception:
        return None


def get_text_response(user_query, language="English"):
    """
    Intelligent Agricultural Assistant that handles English, pure Telugu,
    and Romanized Telugu (Tanglish like 'vari dharalu', 'tamata rate', 'mirchi purugulu').
    """
    query = str(user_query).strip().lower()

    if not query:
        return "దయచేసి మీ వ్యవసాయ సందేహాన్ని అడగండి." if language == "Telugu" else "Please enter your farming or mandi question."

    # Detect Telugu script or language setting
    has_telugu_script = bool(re.search(r'[\u0c00-\u0c7f]', query))
    is_telugu = (language == "Telugu") or has_telugu_script
    lang_key = "te" if is_telugu else "en"

    # 1. GREETINGS
    greetings = ["hello", "hi", "namaste", "హలో", "నమస్కారం", "బాగున్నారా", "hey", "good morning", "good evening", "namaskaram"]
    if any(query == g or query.startswith(g + " ") for g in greetings):
        if is_telugu:
            return (
                "🙏 **నమస్కారం! అగ్రిమార్కెట్ ఇంటెలిజెన్స్ కి స్వాగతం.**\n\n"
                "నేను మీకు సహాయం చేయగలను:\n"
                "• 📊 **మండి ధరలు:** వరి, టమాటా, మిర్చి, పత్తి, ఉల్లి తాజా మార్కెట్ ధరలు.\n"
                "• 🌱 **సాగు పద్ధతులు:** విత్తన మోతాదు, నాటు విధానం, నీటి యాజమాన్యం.\n"
                "• 🛡️ **తెగుళ్ళు & పురుగులు:** పంటల వ్యాధులు, నివారణ మందులు (రసాయన & సేంద్రీయ).\n"
                "• 🧪 **ఎరువుల మోతాదు:** డీఏపీ, యూరియా, పొటాష్ ఎరువుల షెడ్యూల్.\n"
                "• 🏛️ **ప్రభుత్వ పథకాలు:** పీఎం కిసాన్, రైతు భరోసా, సబ్సిడీలు.\n\n"
                "మీ ప్రశ్నను అడగండి!"
            )
        return (
            "🙏 **Hello! Welcome to AgriMarket Intelligence.**\n\n"
            "I am your Smart Agriculture Assistant. I can assist you with:\n"
            "• 📊 **Live APMC Mandi Prices** (Rice, Tomato, Chilli, Cotton, Onion, Maize, etc.)\n"
            "• 🌱 **Crop Cultivation Best Practices** (Sowing, seed rate, spacing, irrigation)\n"
            "• 🛡️ **Pest & Disease Control** (Chemical and organic bio-pesticides)\n"
            "• 🧪 **Fertilizer Schedules** (N-P-K recommendation per acre)\n"
            "• 🏛️ **Government Subsidies & Schemes** (PM-KISAN, Rythu Bharosa, Micro-irrigation)\n\n"
            "What would you like to know?"
        )

    # 2. APP / PROJECT GUIDE
    app_keywords = ["how to use", "project", "app", "website", "system", "features", "dashboard", "ఉపయోగించాలి", "యాప్", "ప్రాజెక్ట్"]
    if any(ak in query for ak in app_keywords):
        return TOPICS_KNOWLEDGE["app_guide"][lang_key]

    # 3. DETECT CROP
    detected_crop = None
    for crop, data in CROP_KNOWLEDGE.items():
        if any(alias in query for alias in data["names"]):
            detected_crop = crop
            break

    # 4. INTENT DETECTION (English + Telugu + Tanglish)
    is_price_query = any(w in query for w in [
        "price", "rate", "cost", "mandi", "market", "apmc", "dharalu", "dhara", "retu",
        "ధర", "రేటు", "మార్కెట్", "మండి", "ఎంత", "ఖరీదు", "ధరలు", "ధర ఎంత"
    ])

    is_pest_query = any(w in query for w in [
        "pest", "disease", "insect", "control", "spray", "cure", "thrips", "mites", "borer", "blight", "virus",
        "పురుగు", "తెగులు", "మందు", "నివారణ", "దోమ", "ముడత", "నల్లి", "రోగం",
        "purugu", "tegulu", "mandulu", "nivarana", "doma", "mudatha", "nalli"
    ])

    is_fert_query = any(w in query for w in [
        "fertilizer", "nutrient", "npk", "urea", "dap", "potash", "manure", "dose",
        "ఎరువు", "ఎరువులు", "యూరియా", "డీఏపీ", "బలం", "పోషకాలు",
        "eruvu", "eruvulu", "yuria", "balam", "poshakalu"
    ])

    is_scheme_query = any(w in query for w in [
        "scheme", "subsidy", "pm kisan", "pmkisan", "rythu", "bharosa", "insurance", "loan", "kcc",
        "పథకం", "సబ్సిడీ", "రైతు భరోసా", "పీఎం కిసాన్", "బీమా", "రుణం",
        "pathakam", "subsidi", "beema"
    ])

    is_organic_query = any(w in query for w in [
        "organic", "natural", "panchagavya", "jeevamrut", "bio", "vermicompost", "neem",
        "సేంద్రీయ", "ప్రకృతి", "జీవామృతం", "పంచగవ్య", "వర్మీకంపోస్ట్", "వేప",
        "sendriya", "prakruthi", "jeevamrutham"
    ])

    is_soil_query = any(w in query for w in [
        "soil", "testing", "ph", "carbon", "మట్టి", "భూసార", "నేల", "మట్టి పరీక్ష", "matti", "bhoosara"
    ])

    is_weed_query = any(w in query for w in [
        "weed", "herbicide", "weedicide", "kalupu", "కలుపు", "కలుపు మందు", "కలుపు నివారణ",
        "kaluputheese", "pendimethalin", "nominee gold", "2,4-d"
    ])

    is_profit_query = any(w in query for w in [
        "profit", "income", "labham", "margin", "returns", "best crop", "high profit",
        "లాభం", "ఎక్కువ లాభం", "ఏ పంట వేస్తే లాభం", "ఆదాయం", "ye panta vesthe labham"
    ])

    # 5. EXECUTE MATCHED INTENTS
    if is_profit_query:
        return TOPICS_KNOWLEDGE["profit"][lang_key]

    if is_weed_query:
        return TOPICS_KNOWLEDGE["weed"][lang_key]

    if is_scheme_query:
        return TOPICS_KNOWLEDGE["scheme"][lang_key]

    if is_organic_query:
        return TOPICS_KNOWLEDGE["organic"][lang_key]

    if is_soil_query and not detected_crop:
        return TOPICS_KNOWLEDGE["soil"][lang_key]

    # Price queries
    if is_price_query:
        target_name = detected_crop.capitalize() if detected_crop else "Tomato"
        live_mandi = get_live_mandi_prices(target_name, "Telugu" if is_telugu else "English")
        if live_mandi:
            return live_mandi

    # Crop-specific queries
    if detected_crop and detected_crop in CROP_KNOWLEDGE:
        crop_data = CROP_KNOWLEDGE[detected_crop]

        if is_pest_query and "pest" in crop_data:
            return crop_data["pest"][lang_key]

        if is_fert_query and "fertilizer" in crop_data:
            return crop_data["fertilizer"][lang_key]

        if "cultivation" in crop_data:
            ans = crop_data["cultivation"][lang_key]
            # Also attach live prices
            m_price = get_live_mandi_prices(detected_crop.capitalize(), "Telugu" if is_telugu else "English")
            if m_price:
                ans += "\n\n" + m_price
            return ans

    # 6. COMPREHENSIVE INTELLIGENT FALLBACK
    if is_telugu:
        return (
            "🌾 **వ్యవసాయ సమాచారం & సలహా:**\n\n"
            "మీరు అడిగిన ప్రశ్నకు ముఖ్య సూచనలు:\n"
            "1. **మండి ధరలు:** నిర్దిష్ట మార్కెట్ ధరల కోసం ఉదాహరణకు: *'వరి ధర ఎంత?'*, *'టమాటా రేటు'*, *'మిర్చి మండి ధర'* అని అడగండి.\n"
            "2. **పంటల సాగు & ఎరువులు:** ఉదాహరణకు: *'వరి ఎరువుల మోతాదు'*, *'టమాటా సాగు విధానం'*, *'పత్తి సాగు పద్ధతులు'*.\n"
            "3. **తెగుళ్ళు & పురుగులు:** ఉదాహరణకు: *'మిర్చి నల్ల తామర పురుగు నివారణ'*, *'వరి కాండం తొలుచు పురుగు'*, *'టమాటా ఆకుముడత'*.\n"
            "4. **పథకాలు:** *'రైతు ప్రభుత్వ పథకాలు'*, *'పీఎం కిసాన్'*, *'డ్రిప్ సబ్సిడీ'* అని అడగండి."
        )
    else:
        return (
            "🌾 **AgriMarket Farming Advice:**\n\n"
            "Here is practical guidance based on your query:\n"
            "1. **APMC Mandi Prices:** To check real prices, ask specifically (e.g. *'Rice price in APMC'*, *'Tomato market rate'*, *'Cotton price'*).\n"
            "2. **Crop Practices:** Ask for guides like *'How to cultivate rice?'*, *'Tomato fertilizer schedule'*, *'Cotton spacing'*.\n"
            "3. **Pest Control:** Inquire about specific problems like *'Chilli black thrips control'*, *'Rice stem borer'*, *'Tomato leaf curl'*, or organic neem methods.\n"
            "4. **Government Schemes:** Ask about *'PM-KISAN scheme'*, *'Drip irrigation subsidy'*, or *'Soil health card'*."
        )
