"""
Manually corrected Casalis A entries.
Each entry was read from casalis_a_cleaned.json, OCR errors fixed by hand,
merged entries split into their own records, and garbled headwords restored.
"""
import json
import re

entries = [
    # ---- A-D ----
    {"headword_english": "Adjunction",    "pos": "n.", "sesotho": "kekeletso"},
    {"headword_english": "Adjure",        "pos": "v.", "sesotho": "ho hlaponya, antsa"},
    {"headword_english": "Administer",    "pos": "v.", "sesotho": "ho lisa, tsamaisa"},
    {"headword_english": "Administration","pos": "n.", "sesotho": "puso, tiso"},
    {"headword_english": "Admire",        "pos": "v.", "sesotho": "(to wonder at) ho makala ke, bōha, tsota, babatsa ; (to feel respect) ho hlompha"},
    {"headword_english": "Admit",         "pos": "v.", "sesotho": "(to permit to enter) ho amohela, kenya ; (to receive as true) ho lumela, kholoa ke"},
    {"headword_english": "Admonish",      "pos": "v.", "sesotho": "ho laea"},
    {"headword_english": "Adolescent",    "pos": "n.", "sesotho": "mohlankana"},
    {"headword_english": "Adopt",         "pos": "v.", "sesotho": "(to adopt a child) ho thola nguana"},
    {"headword_english": "Adoration",     "pos": "n.", "sesotho": "ho khumamela, ho sebeletsa Molimo"},
    {"headword_english": "Adorn",         "pos": "v.", "sesotho": "ho khabisa, lilopha, hlophisa"},
    {"headword_english": "Adulterate",    "pos": "v.", "sesotho": "ho tsueberenya, senya bolisa"},
    {"headword_english": "Adultery",      "pos": "n.", "sesotho": "bofebe"},
    {"headword_english": "Advance",       "pos": "v.", "sesotho": "(lit. and fig.) ho tsuela pele"},
    {"headword_english": "Advantage",     "pos": "n.", "sesotho": "molemo"},
    {"headword_english": "Adventure",     "pos": "n.", "sesotho": "ntho e tsohang e hlahela motho, tsietsi, ngope-a-sesoha"},
    {"headword_english": "Adversary",     "pos": "n.", "sesotho": "sera, mohanyetsi"},
    {"headword_english": "Adversity",     "pos": "n.", "sesotho": "bomalibe, bosoto"},
    {"headword_english": "Advice",        "pos": "n.", "sesotho": "keletso, temoso"},
    {"headword_english": "Advise",        "pos": "v.", "sesotho": "ho lemosa, elotsa"},
    {"headword_english": "Advocate",      "pos": "v.", "sesotho": "ho bulelhi, emela"},
    {"headword_english": "Afar",          "pos": "adv.", "sesotho": "hole, moniamo"},
    {"headword_english": "Affability",    "pos": "n.", "sesotho": "mosa, molemo"},
    {"headword_english": "Affair",        "pos": "n.", "sesotho": "taba, mosebetsi"},
    {"headword_english": "Affect",        "pos": "v.", "sesotho": "(to move or touch) ho ama pelo, sisimosa ; (to be moved) ho perama, sisa pelo ; (to make a show) ho iketsisa"},
    {"headword_english": "Affection",     "pos": "n.", "sesotho": "lerato"},
    {"headword_english": "Affirm",        "pos": "v.", "sesotho": "ho tiisa, omela"},
    {"headword_english": "Affirmation",   "pos": "n.", "sesotho": "tiiso, komelo"},
    {"headword_english": "Afflict",       "pos": "v.", "sesotho": "ho hlokofatsa ; to be afflicted, ho hlomoha, siaba"},
    {"headword_english": "Affliction",    "pos": "n.", "sesotho": "masuabi, mahlomola"},
    {"headword_english": "Affright",      "pos": "v.", "sesotho": "ho tsosa, tsabisa"},
    {"headword_english": "Affront",       "pos": "v.", "sesotho": "ho fahla"},
    {"headword_english": "Afoot",         "pos": "adv.", "sesotho": "ka maoto"},
    {"headword_english": "Aforetime",     "pos": "adv.", "sesotho": "pele, khale"},
    {"headword_english": "Afraid",        "pos": "adj.", "sesotho": "e tsohileng, e tsohang ; to be afraid, ho tsaba, tsoha, qaea, feha mahlo"},
    {"headword_english": "Afresh",        "pos": "adv.", "sesotho": "hape, bocha"},
    {"headword_english": "After",         "pos": "adv.", "sesotho": "morao, ka morao ; prep. ka mora, ka morao"},
    {"headword_english": "Afternoon",     "pos": "n.", "sesotho": "motšehare oa mantsibōeng"},
    {"headword_english": "Afterwards",    "pos": "adv.", "sesotho": "kamora"},
    {"headword_english": "Agent",         "pos": "n.", "sesotho": "'moemeli, ajiante"},
    {"headword_english": "Agility",       "pos": "n.", "sesotho": "bobebe, lebelo"},
    {"headword_english": "Agitate",       "pos": "v.", "sesotho": "(to stir) ho tsukutla, fulua, tsoka, tsokotsa, kapeisu ; (to disturb) ho ferekanya, tsosu ; (to be mentally agitated) ho ferekana, ho erehana"},
    {"headword_english": "Ago",           "pos": "adv.", "sesotho": "khale, pele"},
    {"headword_english": "Agony",         "pos": "n.", "sesotho": "mahlomola a le tsona, bohloko bo boholo"},
    {"headword_english": "Agreeable",     "pos": "adj.", "sesotho": "(pleasing) e khahlelang, e khahlisoang ; to be agreeable, ho khahliha, e tle"},
    {"headword_english": "Agree",         "pos": "v.", "sesotho": "ho lumellana, ho utloana"},
    {"headword_english": "Agreement",     "pos": "n.", "sesotho": "tumellano"},
    {"headword_english": "Agriculture",   "pos": "n.", "sesotho": "bolemi, temo"},
    {"headword_english": "Ahead",         "pos": "adv.", "sesotho": "ka pele ; to go ahead (lit. and fig.), ho tsaela pele"},
    {"headword_english": "Aid",           "pos": "v.", "sesotho": "ho thusa, tlatsa, tlatsetsa ; n. thuso"},
    {"headword_english": "Ail",           "pos": "v.", "sesotho": "ho baba, kuha, ba bohloko"},
    {"headword_english": "Ailment",       "pos": "n.", "sesotho": "bohloko, boloetse, lefu, mafu"},
    {"headword_english": "Aim",           "pos": "v.", "sesotho": "(to endeavour) ho pheella, leka ; (to level at) ho korola, eka ; n. (intention) phihlelo, pheello"},
    {"headword_english": "Air",           "pos": "n.", "sesotho": "(wind) moea ; (manners) sebopeho, motsamao ; (tune) pina ; v. ho bea mot'eng hore e hloekisoe ke moea"},
    {"headword_english": "Alarm",         "pos": "v.", "sesotho": "ho tsosa, ho hlaba mokhosi ; n. letsoso"},
    {"headword_english": "Alas",          "pos": "interj.", "sesotho": "yo! khele!"},
    {"headword_english": "Albino",        "pos": "n.", "sesotho": "lesofe"},
    {"headword_english": "Alert",         "pos": "adj.", "sesotho": "e phakisang, e nang le mohelo"},
    {"headword_english": "Alien",         "pos": "n.", "sesotho": "mochaba"},
    {"headword_english": "Alienate",      "pos": "v.", "sesotho": "(to withdraw affection) ho aelefatsa ; (to transfer) ho neela ntho ho o mong"},
    {"headword_english": "Alive",         "pos": "adj.", "sesotho": "e utloang, phēlang ; to be alive, ho utloana, ho phela"},
    {"headword_english": "All",           "pos": "adj.", "sesotho": "eohle, tsohle, bohle ; n. kaofela ha"},
    {"headword_english": "Allay",         "pos": "v.", "sesotho": "(to make quiet) ho khutsisa ; (to make less in pain) ho bebola, kokobetsa bohloko"},
    {"headword_english": "Allege",        "pos": "v.", "sesotho": "ho hlahisa motatolo"},
    {"headword_english": "Allegory",      "pos": "n.", "sesotho": "setsuantso, papiso"},
    {"headword_english": "Alliance",      "pos": "n.", "sesotho": "selekanoe"},
    {"headword_english": "Allot",         "pos": "v.", "sesotho": "ho abela, arolela"},
    {"headword_english": "Allow",         "pos": "v.", "sesotho": "ho lumellana"},
    {"headword_english": "Allowance",     "pos": "n.", "sesotho": "(a salary) moputso"},
    {"headword_english": "Allure",        "pos": "v.", "sesotho": "ho qeka"},
    {"headword_english": "Alms",          "pos": "n.", "sesotho": "phonosetso"},
    {"headword_english": "Almighty",      "pos": "adj.", "sesotho": "ea matla 'ohle"},
    {"headword_english": "Almost",        "pos": "adv.", "sesotho": "e batlile ho, lekhatheng la ; they are almost here, ba se ba le haufi, ba se ba le lekhatheng la ho tla"},
    {"headword_english": "Aloe",          "pos": "n.", "sesotho": "lekhala"},
    {"headword_english": "Aloft",         "pos": "adv.", "sesotho": "phahameng, holimo, ka holimo"},
    {"headword_english": "Alone",         "pos": "adj.", "sesotho": "'notsi ; to be alone, ho ba mong, 'notsi ; I was quite alone, ea e-ba 'na qha"},
    {"headword_english": "Along",         "pos": "adv.", "sesotho": "pele, koo ; prep. ho ea le, haufi le, hammoho ; go along! u tsamaee!"},
    {"headword_english": "Aloud",         "pos": "adv.", "sesotho": "ka lentsoe le phahamileng, ka ho hoa, ka lentsoe le phepa"},
    {"headword_english": "Alphabet",      "pos": "n.", "sesotho": "ntleteroane"},
    {"headword_english": "Already",       "pos": "adv.", "sesotho": "se ; it is dark already, ho se ho phirimile"},
    {"headword_english": "Also",          "pos": "adv.", "sesotho": "le, hape"},
    {"headword_english": "Alter",         "pos": "v.", "sesotho": "ho fetola ; to become altered, ho fetoha"},
    {"headword_english": "Altercation",   "pos": "n.", "sesotho": "phapang, khang, tseko"},
    {"headword_english": "Alternate",     "pos": "v.", "sesotho": "(to do by turns) ho fapana, ho phomotsana"},
    {"headword_english": "Although",      "pos": "conj.", "sesotho": "leha"},
    {"headword_english": "Altitude",      "pos": "n.", "sesotho": "bolelele, bophahamo, boholo"},
    {"headword_english": "Altogether",    "pos": "adv.", "sesotho": "haramoho, mahong, hona"},
    {"headword_english": "Always",        "pos": "adv.", "sesotho": "kamehla, mehla eohle"},
    {"headword_english": "Amass",         "pos": "v.", "sesotho": "ho bokella"},
    {"headword_english": "Amaze",         "pos": "v.", "sesotho": "ho makatsa ; to be amazed, ho babatseha, makala"},
    {"headword_english": "Ambassador",    "pos": "n.", "sesotho": "lengosa"},
    {"headword_english": "Amiable",       "pos": "adj.", "sesotho": "e latehang"},
    {"headword_english": "Amidst",        "pos": "prep.", "sesotho": "har'a, mahareng a, pakong tsa"},
    {"headword_english": "Ammunition",    "pos": "n.", "sesotho": "limbu tsa ntoa (ukulo, mesili)"},
    {"headword_english": "Amongst",       "pos": "prep.", "sesotho": "bar'a, mahareng a"},
    {"headword_english": "Amount",        "pos": "n.", "sesotho": "palano, bongata"},
    {"headword_english": "Amputate",      "pos": "v.", "sesotho": "ho poua setho, ho khaola"},
    {"headword_english": "Amulet",        "pos": "n.", "sesotho": "thato"},
    {"headword_english": "Amuse",         "pos": "v.", "sesotho": "ho bapalisa, thetsa"},
    {"headword_english": "Ancestor",      "pos": "n.", "sesotho": "ntata-moholo ; (ancestors) litata-boholo"},
    {"headword_english": "Ancient",       "pos": "adj.", "sesotho": "ea khale, oa boholo, e tsofofang, e boneng"},
    {"headword_english": "And",           "pos": "conj.", "sesotho": "'me, hammoho, le"},
    {"headword_english": "Angel",         "pos": "n.", "sesotho": "lengeloi"},
    {"headword_english": "Anger",         "pos": "n.", "sesotho": "khalofo, boliale, boitsena, lunko ; v. ho halosa, tlaka"},
    {"headword_english": "Angle",         "pos": "n.", "sesotho": "kou, sekutlo"},
    {"headword_english": "Angry",         "pos": "adj.", "sesotho": "e halefang, e itsenang ; to be angry, ho halefa, tlokoma, itsena, llala pelo ; to be angry against, ho halefela, tonela motho"},
    {"headword_english": "Animal",        "pos": "n.", "sesotho": "(a being possessing life) sebōpuoa ; (a beast) phoofolo ; a wild animal, nyamasane ; adj. ea lebōpuoa"},
    {"headword_english": "Animosity",     "pos": "n.", "sesotho": "hlonamo, hloeo"},
    {"headword_english": "Ankle",         "pos": "n.", "sesotho": "legaqailane"},
    {"headword_english": "Annihilate",    "pos": "v.", "sesotho": "ho timeletsa, felisa"},
    {"headword_english": "Announce",      "pos": "v.", "sesotho": "ho tsebisa, hela, bebeletsa, tumisa"},
    {"headword_english": "Annoy",         "pos": "v.", "sesotho": "ho khathallisa, hlollea, totonisa, hlopha, horeetsa, felisa pelo"},
    {"headword_english": "Annoyance",     "pos": "n.", "sesotho": "khathallo, hlopha, khoreletso"},
    {"headword_english": "Annually",      "pos": "adv.", "sesotho": "ka selemo se seng le se seng, ka ngwahla o mong le o mong"},
    {"headword_english": "Antagonist",    "pos": "n.", "sesotho": "ea hanyetsang, sera"},
    {"headword_english": "Antelope",      "pos": "n.", "sesotho": "tsephe, letsa, khama"},
    {"headword_english": "Ant-hill",      "pos": "n.", "sesotho": "seolo"},
    {"headword_english": "Anvil",         "pos": "n.", "sesotho": "tsehlo"},
    {"headword_english": "Anxiety",       "pos": "n.", "sesotho": "pelaelo, tsieleho"},
    {"headword_english": "Anxious",       "pos": "adj.", "sesotho": "(troubled) e belaelang ; (eagerly desirous) e lakatsang ; I am anxious to see you, ke lakatsa haholo ho u bona"},
    {"headword_english": "Any",           "pos": "adj.", "sesotho": "mang le mang, eng le eng, efe le efe"},
    {"headword_english": "Anywhere",      "pos": "adv.", "sesotho": "kae le kae"},
    {"headword_english": "Apart",         "pos": "adv.", "sesotho": "kathoko"},
    {"headword_english": "Apologise",     "pos": "v.", "sesotho": "ho inyatsa"},
    {"headword_english": "Apologue",      "pos": "n.", "sesotho": "tsomo, setsuantso"},
    {"headword_english": "Appall",        "pos": "v.", "sesotho": "ho tsosa, tetemisa"},
    {"headword_english": "Apparel",       "pos": "n.", "sesotho": "liaparo"},
    {"headword_english": "Apparent",      "pos": "adj.", "sesotho": "e bonahalang"},
    {"headword_english": "Apparition",    "pos": "n.", "sesotho": "sethotsela, seriti"},
    {"headword_english": "Appeal",        "pos": "v.", "sesotho": "ho ipiletsa"},
    {"headword_english": "Appear",        "pos": "v.", "sesotho": "(to be visible) ho bonahala, boneha, rotoha ; (to come in sight) ho hlaha"},
    {"headword_english": "Appearance",    "pos": "n.", "sesotho": "(the look, the mien) ponahalo, ohali, molapo, sebopeho ; to make an appearance, ho hlaha, ho itiisa"},
    {"headword_english": "Appease",       "pos": "v.", "sesotho": "ho khutsisa"},
    {"headword_english": "Appetite",      "pos": "n.", "sesotho": "(for food) takatso ea lijo ; (a strong desire) takatso"},
    {"headword_english": "Applaud",       "pos": "v.", "sesotho": "(to clap the hands) ho etsa lehofi, ho opa ka liatla ; (to praise) ho rorisa"},
    {"headword_english": "Applause",      "pos": "n.", "sesotho": "lehofi, letlatse"},
    {"headword_english": "Apple",         "pos": "n.", "sesotho": "apole"},
    {"headword_english": "Application",   "pos": "n.", "sesotho": "(a petition) kopo, qelo ; (attention) pheelo, nahano"},
    {"headword_english": "Apply",         "pos": "v.", "sesotho": "(to have recourse to) ho kopa, qela ; (to fix the attention) ho sebetsa ka pheelo, ho nahana ka pheelo ; (to suit) ho lokela ; (to agree) ho lumellana le"},
    {"headword_english": "Appoint",       "pos": "v.", "sesotho": "ho khetha, bea, thonya"},
    {"headword_english": "Apprehend",     "pos": "v.", "sesotho": "(to seize) ho tsuara ; (to think with fear) ho tsaba, ho hopola ka pelaelo"},
    {"headword_english": "Approach",      "pos": "v.", "sesotho": "ho atamela ; n. katamelo"},
    {"headword_english": "Approbation",   "pos": "n.", "sesotho": "ho chaela boka"},
    {"headword_english": "Appropriate",   "pos": "v.", "sesotho": "ho inkela ; adj. e lokelang, e tsoanelang"},
    {"headword_english": "Approve",       "pos": "v.", "sesotho": "ho kholoa ke, emela, chaela, thata"},
    {"headword_english": "April",         "pos": "n.", "sesotho": "'Mesu"},
    {"headword_english": "Apron",         "pos": "n.", "sesotho": "pinafore, forokoto"},
    {"headword_english": "Argue",         "pos": "v.", "sesotho": "ho tseka taba ka lipolelo"},
    {"headword_english": "Arise",         "pos": "v.", "sesotho": "(to ascend) ho nyoloha ; (to emerge) ho hlaha ; (to get up) ho tsoha ; (to rise from the dead) ho tsoha"},
    {"headword_english": "Arm",           "pos": "n.", "sesotho": "letsoho ; v. ho hlokoa oa"},
    {"headword_english": "Arms",          "pos": "n.", "sesotho": "libetsa, lihlomo"},
    {"headword_english": "Armour",        "pos": "n.", "sesotho": "lihlomo, liaparo tsa tsepe tsa ntoa"},
    {"headword_english": "Armpit",        "pos": "n.", "sesotho": "lehati"},
    {"headword_english": "Army",          "pos": "n.", "sesotho": "mabotho"},
    {"headword_english": "Arrest",        "pos": "v.", "sesotho": "ho tsuara, emisa"},
    {"headword_english": "Arrive",        "pos": "v.", "sesotho": "ho fihla, ho re qi"},
    {"headword_english": "Arrogance",     "pos": "n.", "sesotho": "boikakaso, boikgoantšo"},
    {"headword_english": "Arrow",         "pos": "n.", "sesotho": "motsu"},
    {"headword_english": "Artery",        "pos": "n.", "sesotho": "mothapo oa mali"},
    {"headword_english": "Artful",        "pos": "adj.", "sesotho": "oa masene, ea loha"},
    {"headword_english": "Artless",       "pos": "adj.", "sesotho": "e se nang bohlatsoha, e tlhaho"},
    {"headword_english": "As",            "pos": "adv.", "sesotho": "joaleka, ka, ka mokhoa oa ; conj. joaleka ha, kamoo, kateng, ka ha, leha, leha e le"},
    {"headword_english": "Ascend",        "pos": "v.", "sesotho": "ho nyoloha, hloa, mela"},
    {"headword_english": "Ascent",        "pos": "n.", "sesotho": "moepa, mothipo"},
    {"headword_english": "Ascertain",     "pos": "v.", "sesotho": "ho botsisisa, ho batlisisa"},
    {"headword_english": "Ashamed",       "pos": "adj.", "sesotho": "e lihlong, suane, hlayoang ke lihlong"},
    {"headword_english": "Ashes",         "pos": "n.", "sesotho": "mohora"},
    {"headword_english": "Aside",         "pos": "adv.", "sesotho": "kathoko"},
    {"headword_english": "Asleep",        "pos": "adv.", "sesotho": "v. robetseng ; to be asleep, ho robala ; to fall asleep (lit. and fig.) ho ithoballa"},
    {"headword_english": "Asperse",       "pos": "v.", "sesotho": "(to slander) ho etselletsa ; aspersion: (a sprinkling with water) ho nfafatsa"},
    {"headword_english": "Assassin",      "pos": "n.", "sesotho": "'molai"},
    {"headword_english": "Assault",       "pos": "v.", "sesotho": "ho loantsa, futuhela ; n. phutuhelo"},
    {"headword_english": "Assay",         "pos": "n.", "sesotho": "temano, bohlisa"},
    {"headword_english": "Assemble",      "pos": "v.", "sesotho": "(to raise to assemble) ho phuntha, bokella, bokanya ; (to crowd together) ho phunthelela, bokana"},
    {"headword_english": "Assembly",      "pos": "n.", "sesotho": "phutheho, pokano, lekhotla, mokhatlo, pitso, seema"},
    {"headword_english": "Assent",        "pos": "v.", "sesotho": "ho lumela, lumellana"},
    {"headword_english": "Assert",        "pos": "v.", "sesotho": "ho tiisa, holelisa, loka, lokolisa"},
    {"headword_english": "Assist",        "pos": "v.", "sesotho": "ho thusa, tlatsa, emela"},
    {"headword_english": "Associate",     "pos": "v.", "sesotho": "ho kopana, ho etsa setsoalle"},
    {"headword_english": "Assort",        "pos": "v.", "sesotho": "ho bea ka lihlopha, ho teanya tse tsoanang, ho hlophisa, hlophoela"},
    {"headword_english": "Assuage",       "pos": "v.", "sesotho": "ho nolofatsa, kokobetsa"},
    {"headword_english": "Assume",        "pos": "v.", "sesotho": "(to take upon oneself) ho inkela ; (to take for granted) ho lekanya"},
    {"headword_english": "Assurance",     "pos": "n.", "sesotho": "(a declaration to dispel doubt) tsepiso, tiiso ; (a firm belief) tsepiso"},
    {"headword_english": "Assure",        "pos": "v.", "sesotho": "ho tsepisa, tiisa"},
    {"headword_english": "Asthma",        "pos": "n.", "sesotho": "lefuba"},
    {"headword_english": "Astonish",      "pos": "v.", "sesotho": "ho makatsa, tsotisa, hlolla ; to be astonished at, ho tjantjella, tsota, hlolloa ke, babatsa"},
    {"headword_english": "Astonishment",  "pos": "n.", "sesotho": "makalo, hlollo, tsoto, pabatso"},
    {"headword_english": "Astound",       "pos": "v.", "sesotho": "ho makatsa haholo"},
    {"headword_english": "Astray",        "pos": "adv.", "sesotho": "ka ho kheloha, ka ho lahleha ; to go astray, ho lahleha"},
    {"headword_english": "Asunder",       "pos": "adv.", "sesotho": "ka ho khaohanya, ka likoto"},
    {"headword_english": "At",            "pos": "prep.", "sesotho": "ka, ho, ha, haufi le"},
    {"headword_english": "Atone",         "pos": "v.", "sesotho": "(to make amends) ho inyatsa ; (to expiate) ho lefella, ho etsa pheko"},
    {"headword_english": "Attack",        "pos": "v.", "sesotho": "ho qala motho, loantsa, futuhela, tsohela matla ; n. phutuhelo, moqholo"},
    {"headword_english": "Attain",        "pos": "v.", "sesotho": "ho fihla"},
    {"headword_english": "Attention",     "pos": "n.", "sesotho": "(paying heed) mamelo, temoho, hlokomelo ; (act of courtesy) ketso ea hlomepho, kutloano"},
    {"headword_english": "Attest",        "pos": "v.", "sesotho": "ho paka"},
    {"headword_english": "Attire",        "pos": "v.", "sesotho": "ho apesa ; n. liaparo"},
    {"headword_english": "Attract",       "pos": "v.", "sesotho": "(to draw) ho hohela ; (to allure) ho qeka"},
    {"headword_english": "Audacious",     "pos": "adj.", "sesotho": "ea sa tsabeng letho"},
    {"headword_english": "August",        "pos": "n.", "sesotho": "Phato"},
    {"headword_english": "Aunt",          "pos": "n.", "sesotho": "'akhali, 'manguane"},
    {"headword_english": "Aurora",        "pos": "n.", "sesotho": "mafube"},
    {"headword_english": "Authority",     "pos": "n.", "sesotho": "(legal power) matla, bolaoli (bo loketseng, bo neoang ke molao)"},
    {"headword_english": "Autumn",        "pos": "n.", "sesotho": "lehoetla"},
    {"headword_english": "Avail",         "pos": "v.", "sesotho": "(to turn to profit) ho ithusa ; (to be of use) ho thusa ; it avails me nothing, ha ho nthuse letho"},
    {"headword_english": "Avarice",       "pos": "n.", "sesotho": "bokhonatla, takatso ea ho rua, qotho"},
    {"headword_english": "Avaricious",    "pos": "adj.", "sesotho": "ea lekhonatla, oa qotho"},
    {"headword_english": "Avenge",        "pos": "v.", "sesotho": "ho phethetsa, lefetsa ; to avenge one's self, ho iphethetsa"},
    {"headword_english": "Avenger",       "pos": "n.", "sesotho": "mophethetai, molefetsi"},
    {"headword_english": "Aversion",      "pos": "n.", "sesotho": "kheso, qeno"},
    {"headword_english": "Avert",         "pos": "v.", "sesotho": "(to turn away) ho phemisa, qobisa"},
    {"headword_english": "Avoid",         "pos": "v.", "sesotho": "ho kaekuetsa, phema, qoba, qena, sesefa"},
    {"headword_english": "Avow",          "pos": "v.", "sesotho": "ho lumela, ipolela"},
    {"headword_english": "Await",         "pos": "v.", "sesotho": "ho lebella, emela, leta"},
    {"headword_english": "Awaken",        "pos": "v.", "sesotho": "(to cause to awaken) ho tsosa boroko ; (to become awake) ho tsoha, phaphama ; adj. ea sa robaleng, ea falimehang"},
    {"headword_english": "Award",         "pos": "v.", "sesotho": "ho ahlolela ; n. kahlolo, khaolo ea nyeoe"},
    {"headword_english": "Away",          "pos": "adv.", "sesotho": "hole, hōle"},
    {"headword_english": "Awe",           "pos": "n.", "sesotho": "tsabo e kopaneng le hlompha"},
    {"headword_english": "Awful",         "pos": "adj.", "sesotho": "e tsabelang, tsabisang"},
    {"headword_english": "Awhile",        "pos": "adv.", "sesotho": "motsotso o se okae, motsotso feela"},
    {"headword_english": "Awkward",       "pos": "adj.", "sesotho": "(clumsy) e thata, e sethoto, e so khuahilapa ; (difficult) e mietalang, e thata"},
    {"headword_english": "Axe",           "pos": "n.", "sesotho": "selepe ; battle-axe, kuakoa, tsanka"},
]

def normalize_entry(entry):
    text = str(entry.get("sesotho", ""))
    text = text.replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text).strip()
    # High-confidence OCR punctuation cleanup.
    text = text.replace(",,", ",")
    text = re.sub(r"([,;:])\1+", r"\1", text)
    return {
        "headword_english": str(entry.get("headword_english", "")).strip(),
        "pos": str(entry.get("pos", "")).strip(),
        "sesotho": text,
    }


def build_ocr_review(entries_):
    review = []
    suspicious_fragments = [
        "moha o ng",  # likely broken tokenization from OCR
        "mafsia",     # uncommon cluster likely OCR drift
        "khefcha",    # uncommon cluster likely OCR drift
    ]
    for entry in entries_:
        text = entry["sesotho"]
        if re.search(r"\d", text):
            review.append(
                {
                    "headword_english": entry["headword_english"],
                    "issue": "digit_in_definition",
                    "snippet": text,
                }
            )
        if re.search(r"[,;:.]{2,}", text):
            review.append(
                {
                    "headword_english": entry["headword_english"],
                    "issue": "repeated_punctuation",
                    "snippet": text,
                }
            )
        for frag in suspicious_fragments:
            if frag in text:
                review.append(
                    {
                        "headword_english": entry["headword_english"],
                        "issue": "suspicious_fragment",
                        "fragment": frag,
                        "snippet": text,
                    }
                )
    return review


normalized_entries = [normalize_entry(entry) for entry in entries]
ocr_review = build_ocr_review(normalized_entries)

with open("casalis_a_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(normalized_entries, f, ensure_ascii=False, indent=2)

with open("casalis_a_ocr_review.json", "w", encoding="utf-8") as f:
    json.dump(ocr_review, f, ensure_ascii=False, indent=2)

print(f"Written {len(normalized_entries)} entries to casalis_a_cleaned.json")
print(f"Wrote {len(ocr_review)} OCR review flags to casalis_a_ocr_review.json")
