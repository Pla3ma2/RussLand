import json, pathlib
OUT=pathlib.Path(''+str(pathlib.Path(__file__).resolve().parents[2]/'content'/'levels')+'')
def ph(id, speaker, ru, fr, note, gap=None, dis=None, orders=None, why=None):
    d={"id":id,"speaker":speaker,"ru":ru,"fr":fr,"noteFr":note}
    if gap: d["gap"]={"word":gap,"distractors":dis}
    if gap and why: d["gap"]["whyFr"]=why
    if orders: d["orders"]=orders
    return d
def D(sp,ru,fr): return {"speaker":sp,"ru":ru,"fr":fr}
def B(ps,rv=None):
    d={"type":"block","phrases":ps}
    if rv: d["review"]=rv
    return d
def W(ps): return {"type":"warmup","phrases":ps}
I=lambda i:{"type":"insight","index":i}
SC={"type":"scene"}; EX={"type":"explore"}; FIN=[{"type":"final"},{"type":"roleplay"}]
def lesson(**kw):
    kw={"version":2,"learner":"luka",**kw}
    if kw.get("combos"):
        kw["parts"][1]["steps"].append({"type":"combine","phrases":[f"c{i+1}" for i in range(len(kw["combos"]))]})
    (OUT/f"{kw['id']}.json").write_text(json.dumps(kw,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
COMMON={"здравствуйте":"bonjour (poli)","я":"je, moi","ты":"tu","вы":"vous","да":"oui","нет":"non","а":"et, mais","и":"et","это":"c'est, voici","не":"ne… pas","в":"dans, à","на":"sur, en","что":"quoi, que","как":"comment, comme","где":"où","очень":"très","спасибо":"merci","пожалуйста":"s'il te plaît / je t'en prie","хорошо":"bien, d'accord","привет":"salut","лука":"Luka (prénom)","маша":"Macha (prénom)","олег":"Oleg (prénom)","анна":"Anna (prénom)","у":"chez","меня":"moi (у меня = j'ai)","тебя":"toi (у тебя = tu as)","есть":"il y a","мой":"mon","моя":"ma","мне":"à moi","тоже":"aussi","сегодня":"aujourd'hui","завтра":"demain","вчера":"hier","потом":"puis, ensuite","давай":"allons-y, faisons"}
def G(d): return {**COMMON, **d}
def C(ru, fr, extra, orders=None, note=""):
    d={"ru":ru,"fr":fr,"extra":extra}
    if orders: d["orders"]=orders
    if note: d["noteFr"]=note
    return d


# ---------------- 17. Magasin de vêtements ----------------
lesson(id="17-vetements", order=17, titleFr="Acheter un bonnet", titleRu="В магазине одежды", emoji="🧣",
 sceneFr="Comme Macha l'a dit, Luka va acheter un bonnet. Il entre dans un magasin de vêtements.",
 dialogue=[D("seller","Здравствуйте! Вам помочь?","Bonjour ! Je peux vous aider ?"),
   D("luka","Да, я хочу купить шапку.","Oui, je voudrais acheter un bonnet."),
   D("seller","Вот эта шапка тёплая.","Ce bonnet-ci est chaud."),
   D("luka","Можно посмотреть?","Je peux regarder ?"),
   D("seller","Конечно. Вот, пожалуйста.","Bien sûr. Voilà."),
   D("luka","Сколько она стоит?","Combien il coûte ?"),
   D("seller","Тысяча рублей.","Mille roubles."),
   D("luka","Хорошо, я возьму. И ещё шарф, пожалуйста.","D'accord, je le prends. Et aussi une écharpe, s'il vous plaît.")],
 phrases=[
   ph("help","seller","Вам помочь?","Je peux vous aider ?","Mot à mot : « vous aider ? ». Les vendeurs le disent tout le temps.","помочь",["тёплая","возьму"]),
   ph("buy","luka","Да, я хочу купить шапку.","Oui, je voudrais acheter un bonnet.","« Хочу купить » = je veux acheter. Le bonnet est la chose qu'on achète : « шапку ».","шапку",["шапка","тысяча"],["да я хочу купить шапку","да я шапку хочу купить"],"On veut acheter le bonnet : « шапку » (-у), le bleu."),
   ph("warm","seller","Вот эта шапка тёплая.","Ce bonnet-ci est chaud.","« Эта » = cette. « Тёплая » = chaude (féminin, comme « шапка »).","тёплая",["тёплый","можно"],None,"« Шапка » est féminin : « тёплая » (-ая). « Тёплый », c'est pour un mot masculin."),
   ph("may","luka","Можно посмотреть?","Je peux regarder ?","« Можно…? » = est-ce que je peux… ? Un mot magique pour demander poliment.","можно",["помочь","сколько"]),
   ph("price","luka","Сколько она стоит?","Combien il coûte ?","« Она » remplace « шапка » (féminin). En français on dit « il » pour un bonnet, en russe « она ».","она",["он","можно"],None,"« Шапка » est féminin, donc on la remplace par « она »."),
   ph("thousand","seller","Тысяча рублей.","Mille roubles.","« Тысяча » = mille."),
   ph("take","luka","Хорошо, я возьму.","D'accord, je le prends.","« Я возьму » = je prends (mot à mot : je prendrai).","возьму",["можно","помочь"]),
   ph("scarf","luka","И ещё шарф, пожалуйста.","Et aussi une écharpe, s'il vous plaît.","« Шарф » = écharpe. Masculin : il ne change pas.","шарф",["шарфа","помочь"])],
 parts=[{"titleFr":"Demander","steps":[SC,EX,I(0),B(["help","buy"]),B(["warm","may"],["buy"])]},
   {"titleFr":"Payer","steps":[W(["help","buy","may"]),B(["price","thousand"],["warm","may"]),B(["take","scarf"],["price"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"seller","fr":["« Хочу купить… » = je veux acheter… Et ce qu'on achète prend le bleu : « шапка » → « шапку », « куртка » → « куртку ».","« Шарф » (masculin) ne change pas. « Перчатки » (gants) non plus."]},
   {"by":"seller","fr":["« Можно…? » sert à tout : « Можно посмотреть ? » (je peux regarder ?), « Можно меню ? », « Можно воду ? ».","Et les adjectifs suivent le genre : « тёплый шарф », « тёплая шапка »."]}],
 explore={"type":"case","speaker":"luka","case":"accs","frame":"Я хочу купить ___.","frameFr":"Je voudrais acheter ___.","color":"#3a86ff","hintFr":"Mets chaque vêtement après « купить » et regarde bien la fin du mot.","words":[
   {"tile":"шапка","fr":"un bonnet","phraseFr":"Je voudrais acheter un bonnet."},{"tile":"шарф","fr":"une écharpe","phraseFr":"Je voudrais acheter une écharpe."},
   {"tile":"куртка","fr":"une veste","phraseFr":"Je voudrais acheter une veste."},{"tile":"перчатки","formAcc":"перчатки","fr":"des gants","phraseFr":"Je voudrais acheter des gants."}]},
 tasks=[{"type":"pick","fr":"Dis que tu veux acheter une veste.","answer":"куртка"},{"type":"pick","fr":"Dis que tu veux acheter des gants.","answer":"перчатки"}],
 cando=["demander de l'aide dans un magasin","demander « je peux… ? »","acheter un vêtement"],
 unlocks=[{"case":"accs","gender":"femn","from":"куртка","to":"куртку"}],
 glossary=G({"вам":"vous (à vous)","помочь":"aider","хочу":"(je) veux","купить":"acheter","шапку":"bonnet (après купить)","шапка":"bonnet","вот":"voici","эта":"cette","тёплая":"chaude","теплая":"chaude","тёплый":"chaud","теплый":"chaud","можно":"on peut, je peux","посмотреть":"regarder","конечно":"bien sûr","сколько":"combien","она":"elle","он":"il","стоит":"coûte","тысяча":"mille","рублей":"roubles","возьму":"(je) prendrai","ещё":"encore, aussi","шарф":"écharpe","шарфа":"(forme incorrecte ici)","куртка":"veste","куртку":"veste (après купить)","перчатки":"gants"}),
 combos=[C("Можно посмотреть шарф?","Je peux regarder l'écharpe ?",["шапка"],["можно посмотреть шарф","шарф можно посмотреть"]),
   C("Вот эта куртка тёплая.","Cette veste-ci est chaude.",["шарф"]),
   C("Сколько стоит куртка?","Combien coûte la veste ?",["куртку"],["сколько стоит куртка","куртка сколько стоит"])])

# ---------------- 18. À la gare ----------------
lesson(id="18-gare", order=18, titleFr="À la gare", titleRu="На вокзале", emoji="🚆",
 sceneFr="Anton, le frère de Macha, les invite à Moscou pour le Nouvel An. Luka va à la gare acheter les billets.",
 dialogue=[D("luka","Здравствуйте! Два билета в Москву, пожалуйста.","Bonjour ! Deux billets pour Moscou, s'il vous plaît."),
   D("cashier","На какое число?","Pour quelle date ?"),
   D("luka","На тридцатое декабря.","Pour le trente décembre."),
   D("cashier","Есть поезд в восемь утра.","Il y a un train à huit heures du matin."),
   D("luka","Отлично. А сколько часов ехать?","Parfait. Et combien d'heures de trajet ?"),
   D("cashier","Четыре часа.","Quatre heures."),
   D("luka","Хорошо. Туда и обратно, пожалуйста.","D'accord. Aller-retour, s'il vous plaît."),
   D("cashier","Вот ваши билеты. Счастливого пути!","Voici vos billets. Bon voyage !")],
 phrases=[
   ph("tickets","luka","Два билета в Москву, пожалуйста.","Deux billets pour Moscou, s'il vous plaît.","« В Москву » = vers Moscou : la direction prend le bleu (-у). « Два билета » = deux billets.","москву",["москве","поезд"],["два билета в москву пожалуйста","пожалуйста два билета в москву"],"On va VERS Moscou : « в Москву » (-у). « В Москве » (-е), c'est quand on y est."),
   ph("date","cashier","На какое число?","Pour quelle date ?","« Число » = nombre, date. « На какое число ? » = pour quelle date ?","число",["поезд","утра"]),
   ph("thirty","luka","На тридцатое декабря.","Pour le trente décembre.","« Тридцатое декабря » = le trente décembre.","декабря",["поезд","утра"]),
   ph("train","cashier","Есть поезд в восемь утра.","Il y a un train à huit heures du matin.","« Поезд » = train. « В восемь утра » = à huit heures du matin.","поезд",["билета","число"]),
   ph("hours","luka","А сколько часов ехать?","Et combien d'heures de trajet ?","Mot à mot : « combien d'heures aller (en véhicule) ? ». Tu connais « ехать » : я еду, ты едешь.","ехать",["билета","утра"]),
   ph("four","cashier","Четыре часа.","Quatre heures.","Avec 2, 3, 4 : « часа ». Avec 5 et plus : « часов ». Retiens les deux formes.","четыре",["восемь","поезд"]),
   ph("return","luka","Туда и обратно, пожалуйста.","Aller-retour, s'il vous plaît.","« Туда » = là-bas (aller), « обратно » = retour.","обратно",["туда","поезд"]),
   ph("trip","cashier","Счастливого пути!","Bon voyage !","« Счастливого пути ! » = bon voyage ! (mot à mot : heureux chemin !).")],
 parts=[{"titleFr":"Les billets","steps":[SC,EX,I(0),B(["tickets","date"]),B(["thirty","train"],["tickets"])]},
   {"titleFr":"Le voyage","steps":[W(["tickets","date","train"]),B(["hours","four"],["thirty","train"]),B(["return","trip"],["hours"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"cashier","fr":["Pour une destination, on utilise « в » + le bleu : « в Москву », « в Казань ». C'est comme « в театр », « в больницу ».","Rappel : « я в Москве » (j'y suis, vert) / « я еду в Москву » (j'y vais, bleu)."]},
   {"by":"cashier","fr":["Les nombres russes changent le mot qui suit : « один билет », « два билета », « пять билетов ». Ne t'inquiète pas, on te comprendra même si tu te trompes !","Pour l'heure : « в восемь утра » (8 h du matin), « в семь вечера » (7 h du soir)."]}],
 explore={"type":"case","speaker":"luka","case":"accs","frame":"Один билет в ___, пожалуйста.","frameFr":"Un billet pour ___, s'il vous plaît.","color":"#3a86ff","hintFr":"Mets chaque ville après « в » (on y va) et regarde bien la fin du mot.","words":[
   {"tile":"Москва","fr":"Moscou","phraseFr":"Un billet pour Moscou, s'il vous plaît."},{"tile":"Казань","formAcc":"Каз+ань","fr":"Kazan","phraseFr":"Un billet pour Kazan, s'il vous plaît."},
   {"tile":"Сочи","formAcc":"С+очи","fr":"Sotchi","phraseFr":"Un billet pour Sotchi, s'il vous plaît."},{"tile":"Самара","fr":"Samara","phraseFr":"Un billet pour Samara, s'il vous plaît."}]},
 tasks=[{"type":"pick","fr":"Demande un billet pour Samara.","answer":"Самара"},{"type":"pick","fr":"Demande un billet pour Sotchi.","answer":"Сочи"}],
 cando=["acheter un billet de train","dire une date","demander la durée du trajet"],
 unlocks=[{"case":"accs","gender":"femn","from":"Москва","to":"Москву"}],
 glossary=G({"два":"deux","билета":"billets (après 2, 3, 4)","москву":"Moscou (vers)","москве":"Moscou (on y est)","москва":"Moscou","какое":"quel","число":"date, nombre","тридцатое":"trente (date)","декабря":"décembre","поезд":"train","восемь":"huit","утра":"du matin","отлично":"parfait","сколько":"combien","часов":"heures (après 5…)","ехать":"aller (en véhicule)","четыре":"quatre","часа":"heures (après 2, 3, 4)","туда":"là-bas (aller)","обратно":"retour","вот":"voici","ваши":"vos","билеты":"billets","счастливого":"heureux","пути":"chemin (счастливого пути = bon voyage)","один":"un","билет":"billet","казань":"Kazan","сочи":"Sotchi","самара":"Samara","самару":"Samara (vers)"}),
 combos=[C("Один билет в Москву, пожалуйста.","Un billet pour Moscou, s'il vous plaît.",["москве"],["один билет в москву пожалуйста","пожалуйста один билет в москву"]),
   C("Поезд в Москву в восемь утра.","Le train pour Moscou est à huit heures du matin.",["москве"]),
   C("Завтра я еду в Москву.","Demain, je vais à Moscou.",["москве"],["завтра я еду в москву","я еду в москву завтра"])])

# ---------------- 19. Moscou ----------------
lesson(id="19-moscou", order=19, titleFr="Bienvenue à Moscou", titleRu="Москва", emoji="🏰",
 sceneFr="Le 30 décembre, Luka et Macha arrivent à Moscou. Anton, le frère de Macha, les attend à la gare.",
 dialogue=[D("anton","Маша! Привет! Как доехали?","Macha ! Salut ! Le voyage s'est bien passé ?"),
   D("masha","Хорошо! Антон, это Л+ука, мой друг.","Bien ! Anton, voici Luka, mon ami."),
   D("anton","Очень приятно, Л+ука! Добро пожаловать в Москву!","Enchanté, Luka ! Bienvenue à Moscou !"),
   D("luka","Спасибо! Москва — очень большой город.","Merci ! Moscou, c'est une très grande ville."),
   D("anton","Да, и очень красивый. Это Красная площадь.","Oui, et très belle. Voici la place Rouge."),
   D("luka","Какая большая площадь!","Quelle grande place !"),
   D("anton","А это Кремль. Он очень старый.","Et ça, c'est le Kremlin. Il est très vieux."),
   D("luka","Как интересно! Я хочу всё посмотреть!","Comme c'est intéressant ! Je veux tout voir !")],
 phrases=[
   ph("arrived","anton","Как доехали?","Le voyage s'est bien passé ?","Mot à mot : « comment êtes-vous arrivés ? ». La question qu'on pose à la gare.","доехали",["старый","пожаловать"]),
   ph("friend","masha","Антон, это Л+ука, мой друг.","Anton, voici Luka, mon ami.","Tu connais « это мой друг » depuis le dîner chez Macha.","друг",["город","кремль"]),
   ph("welcome","anton","Добро пожаловать в Москву!","Bienvenue à Moscou !","« Добро пожаловать » = bienvenue. On y va / on y arrive : « в Москву ».","москву",["москве","город"],None,"Après « добро пожаловать в », c'est la direction : « в Москву » (-у)."),
   ph("big","luka","Москва — очень большой город.","Moscou, c'est une très grande ville.","« Город » (ville) est masculin en russe : « большой город ». Le tiret « — » remplace le verbe « être ».","большой",["большая","площадь"],["москва очень большой город"],"« Город » est masculin : « большой ». « Большая », c'est pour un mot féminin."),
   ph("square","anton","Это Красная площадь.","Voici la place Rouge.","« Площадь » = place (féminin). « Красная » = rouge (autrefois : « belle »).","площадь",["город","кремль"]),
   ph("bigsquare","luka","Какая большая площадь!","Quelle grande place !","« Площадь » est féminin : « какая большая ». Attention, ce mot finit par -ь mais il est féminin.","большая",["большой","город"],["какая большая площадь"],"« Площадь » est féminin : « большая » (-ая)."),
   ph("old","anton","А это Кремль. Он очень старый.","Et ça, c'est le Kremlin. Il est très vieux.","« Старый » = vieux. « Кремль » est masculin : « он », « старый ».","старый",["старая","большая"],None,"« Кремль » est masculin : « старый ». « Старая », c'est pour un mot féminin."),
   ph("all","luka","Как интересно! Я хочу всё посмотреть!","Comme c'est intéressant ! Je veux tout voir !","« Всё » = tout. « Посмотреть » = voir, regarder.","всё",["большой","старый"])],
 parts=[{"titleFr":"L'arrivée","steps":[SC,B(["arrived","friend"]),B(["welcome","big"],["friend"]),EX,I(0)]},
   {"titleFr":"La place Rouge","steps":[W(["welcome","big","friend"]),B(["square","bigsquare"],["big"]),B(["old","all"],["bigsquare","square"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anton","fr":["Les adjectifs suivent le genre du nom : masculin « большой город », « старый город » ; féminin « большая площадь », « старая площадь ».","Le plus souvent : masculin -ый / -ой, féminin -ая. Écoute la fin !"]},
   {"by":"anton","fr":["Attention aux mots en -ь : certains sont masculins (« Кремль »), d'autres féminins (« площадь »). On les apprend avec un adjectif : « большая площадь ».","Le tiret « — » remplace souvent le verbe « être » : « Москва — большой город »."]}],
 explore={"type":"plain","speaker":"luka","frame":"Москва — ___ город.","frameFr":"Moscou est une ville ___.","color":"#5c677d","hintFr":"Mets chaque adjectif dans la phrase et écoute. « Город » est masculin.","words":[
   {"tile":"большой","fr":"grande","phraseFr":"Moscou est une grande ville."},{"tile":"красивый","fr":"belle","phraseFr":"Moscou est une belle ville."},
   {"tile":"старый","fr":"vieille","phraseFr":"Moscou est une vieille ville."},{"tile":"интересный","fr":"intéressante","phraseFr":"Moscou est une ville intéressante."}]},
 tasks=[{"type":"pick","fr":"Dis que Moscou est une vieille ville.","answer":"старый"},{"type":"pick","fr":"Dis que Moscou est une ville intéressante.","answer":"интересный"}],
 cando=["présenter un ami","décrire une ville","dire bienvenue"],
 unlocks=[],
 glossary=G({"как":"comment","доехали":"(êtes) arrivés","антон":"Anton (prénom)","мой":"mon","друг":"ami","приятно":"agréable","добро":"bien (добро пожаловать = bienvenue)","пожаловать":"(добро пожаловать = bienvenue)","москву":"Moscou (vers)","москве":"Moscou (on y est)","москва":"Moscou","большой":"grand","большая":"grande","город":"ville","красивый":"beau","красная":"rouge","площадь":"place","какая":"quelle","кремль":"Kremlin","он":"il","старый":"vieux","старая":"vieille","интересно":"intéressant","интересный":"intéressant","хочу":"(je) veux","всё":"tout","все":"tout","посмотреть":"voir, regarder"}),
 combos=[C("Ли+он — очень красивый город.","Lyon est une très belle ville.",["большая"],["лион очень красивый город"]),
   C("Это мой друг. Он из Франции.","C'est mon ami. Il vient de France.",["она"]),
   C("Я хочу посмотреть Кремль.","Je veux voir le Kremlin.",["площадь"],["я хочу посмотреть кремль","кремль я хочу посмотреть"])])

# ---------------- 20. Nouvel An ----------------
lesson(id="20-nouvel-an", order=20, titleFr="Le Nouvel An", titleRu="Новый год", emoji="🎄",
 sceneFr="Le 31 décembre, chez Anton. Il est presque minuit : tout le monde prépare la fête.",
 dialogue=[D("anton","Скоро Новый год! Что ты хочешь на Новый год, Л+ука?","Bientôt le Nouvel An ! Qu'est-ce que tu veux pour le Nouvel An, Luka ?"),
   D("luka","Я хочу хорошо говорить по-русски!","Je veux bien parler russe !"),
   D("masha","Ты уже хорошо говоришь!","Tu parles déjà bien !"),
   D("anton","Двенадцать часов! С Новым годом!","Minuit ! Bonne année !"),
   D("luka","С Новым годом! С новым счастьем!","Bonne année ! Plein de bonheur !"),
   D("masha","Давайте пить шампанское!","Buvons du champagne !"),
   D("anton","За нас! За дружбу!","À nous ! À l'amitié !"),
   D("luka","За дружбу!","À l'amitié !")],
 phrases=[
   ph("soon","anton","Скоро Новый год!","Bientôt le Nouvel An !","« Скоро » = bientôt. « Новый год » = le Nouvel An (mot à mot : nouvelle année).","скоро",["нас","давайте"]),
   ph("want","anton","Что ты хочешь на Новый год?","Qu'est-ce que tu veux pour le Nouvel An ?","« Хочешь » = (tu) veux. « На Новый год » = pour le Nouvel An.","хочешь",["хочу","скоро"],["что ты хочешь на новый год","что ты на новый год хочешь"],"Avec « ты » : « хочешь ». « Хочу », c'est pour « я »."),
   ph("speak","luka","Я хочу хорошо говорить по-р+усски!","Je veux bien parler russe !","« Хочу » + infinitif : je veux (faire). « Говорить » = parler.","говорить",["говорю","скоро"],["я хочу хорошо говорить по-русски","я хочу говорить по-русски хорошо"],"Après « хочу », le verbe reste à l'infinitif : « хочу говорить »."),
   ph("already","masha","Ты уже хорошо говоришь!","Tu parles déjà bien !","« Уже » = déjà. « Ты говоришь » = tu parles.","уже",["нас","давайте"],["ты уже хорошо говоришь","ты уже говоришь хорошо"]),
   ph("happy","anton","С Новым годом!","Bonne année !","Mot à mot : « avec la nouvelle année ! ». La phrase du 31 décembre à minuit.","годом",["год","счастьем"],None,"Après « с » : « с Новым годом ». Retiens-le tel quel !"),
   ph("happiness","luka","С новым счастьем!","Plein de bonheur !","« Счастье » = bonheur. On le dit juste après « С Новым годом ! ».","счастьем",["дружбу","нас"]),
   ph("champagne","masha","Давайте пить шампанское!","Buvons du champagne !","« Давайте » + infinitif = faisons… ! Tu connais « давайте ужинать ».","пить",["пей","шампанское"],["давайте пить шампанское"],"Après « давайте », l'infinitif : « пить »."),
   ph("toast","anton","За нас! За дружбу!","À nous ! À l'amitié !","« За… ! » = à… ! (pour trinquer). « Дружба » = amitié → « за дружбу » (-у).","дружбу",["дружба","счастьем"],None,"Pour trinquer, « за » + le bleu : « дружба » → « за дружбу ».")],
 parts=[{"titleFr":"Avant minuit","steps":[SC,B(["soon","want"]),B(["speak","already"],["want"]),I(0)]},
   {"titleFr":"Minuit !","steps":[W(["want","speak","already"]),B(["happy","happiness"],["speak"]),EX,I(1),B(["champagne","toast"],["happy","happiness"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anton","fr":["« Хочу » + un verbe à l'infinitif : « я хочу говорить », « я хочу посмотреть », « я хочу купить ». Super pratique !","Et « хочу » + une chose (en bleu) : « я хочу шапку »."]},
   {"by":"anton","fr":["Pour trinquer, on dit « За… ! » + le bleu : « за дружбу ! », « за любовь ! », « за нас ! ».","Le Nouvel An est LA grande fête en Russie : on fait un sapin, on mange la salade « Оливье », et à minuit on dit « С Новым годом ! »."]}],
 explore={"type":"case","speaker":"anton","case":"accs","frame":"За ___!","frameFr":"À ___ !","color":"#3a86ff","hintFr":"Trinque avec chaque mot et regarde bien la fin du mot.","words":[
   {"tile":"дружба","fr":"l'amitié","phraseFr":"À l'amitié !"},{"tile":"любовь","fr":"l'amour","phraseFr":"À l'amour !"},
   {"tile":"здоровье","fr":"la santé","phraseFr":"À la santé !"},{"tile":"Россия","fr":"la Russie","phraseFr":"À la Russie !"}]},
 tasks=[{"type":"pick","fr":"Trinque à l'amour.","answer":"любовь"},{"type":"pick","fr":"Trinque à la Russie.","answer":"Россия"}],
 cando=["souhaiter une bonne année","trinquer","dire ce que tu veux faire"],
 unlocks=[{"case":"accs","gender":"femn","from":"дружба","to":"дружбу"}],
 glossary=G({"скоро":"bientôt","новый":"nouveau","год":"année, an","хочешь":"(tu) veux","хочу":"(je) veux","говорить":"parler","говорю":"(je) parle","по-русски":"en russe","уже":"déjà","говоришь":"(tu) parles","двенадцать":"douze","часов":"heures","с":"avec","новым":"nouveau (après с)","годом":"année (с Новым годом = bonne année)","счастьем":"bonheur (après с)","давайте":"faisons, allons","пить":"boire","пей":"bois !","шампанское":"champagne","за":"à (pour trinquer)","нас":"nous","дружбу":"amitié (après за)","дружба":"amitié","любовь":"amour","здоровье":"santé","россию":"Russie (après за)","россия":"Russie"}),
 combos=[C("Я хочу купить шампанское.","Je veux acheter du champagne.",["пить"],["я хочу купить шампанское","шампанское я хочу купить"]),
   C("Что ты хочешь посмотреть в Москве?","Qu'est-ce que tu veux voir à Moscou ?",["москву"],["что ты хочешь посмотреть в москве","что ты хочешь в москве посмотреть"]),
   C("Ты уже говоришь по-англ+ийски?","Tu parles déjà anglais ?",["говорю"],["ты уже говоришь по-английски","ты уже по-английски говоришь"])])

# ---------------- 21. L'appartement ----------------
lesson(id="21-appartement", order=21, titleFr="L'appartement d'Anton", titleRu="Квартира", emoji="🏠",
 sceneFr="Anton fait visiter son appartement à Luka et Macha.",
 dialogue=[D("anton","Вот моя квартира. Проходите!","Voici mon appartement. Entrez !"),
   D("luka","Какая большая квартира!","Quel grand appartement !"),
   D("anton","Это моя комната, а это кухня.","Ça, c'est ma chambre, et ça, c'est la cuisine."),
   D("luka","А где туалет?","Et où sont les toilettes ?"),
   D("anton","Туалет там, направо.","Les toilettes sont là-bas, à droite."),
   D("masha","А где Л+ука будет спать?","Et où va dormir Luka ?"),
   D("anton","Здесь, на диване.","Ici, sur le canapé."),
   D("masha","Отлично! А ужинать мы будем на кухне.","Parfait ! Et on va dîner dans la cuisine.")],
 phrases=[
   ph("flat","anton","Вот моя квартира.","Voici mon appartement.","« Квартира » = appartement (féminin en russe : « моя »).","квартира",["квартире","комнате"],None,"Ici, « квартира » est juste présentée : forme de base, sans -е."),
   ph("bigflat","luka","Какая большая квартира!","Quel grand appartement !","Féminin : « какая большая квартира ».","большая",["большой","кухне"],["какая большая квартира"],"« Квартира » est féminin : « большая » (-ая)."),
   ph("room","anton","Это моя комната, а это кухня.","Ça, c'est ma chambre, et ça, c'est la cuisine.","« Комната » = chambre, pièce. « Кухня » = cuisine.","кухня",["кухне","спать"],None,"On présente la cuisine : forme de base « кухня ». « На кухне », c'est « dans la cuisine »."),
   ph("toilet","luka","А где туалет?","Et où sont les toilettes ?","« Туалет » = les toilettes. Phrase de survie !","туалет",["диване","кухне"]),
   ph("there","anton","Туалет там, направо.","Les toilettes sont là-bas, à droite.","Tu connais « там » et « направо » !","направо",["диване","спать"]),
   ph("sleep","masha","А где Л+ука будет спать?","Et où va dormir Luka ?","« Спать » = dormir. « Будет спать » = va dormir (le futur, avec « он будет »).","спать",["сплю","диване"],None,"Après « будет », l'infinitif : « спать »."),
   ph("sofa","anton","Здесь, на диване.","Ici, sur le canapé.","« Диван » = canapé → « на диване » (sur le canapé) : le vert du lieu.","диване",["диван","кухня"],None,"Pour dire où : « на » + -е : « диван » → « на диване »."),
   ph("kitchen","masha","А ужинать мы будем на кухне.","Et on va dîner dans la cuisine.","Attention : on dit « на кухне » (et pas « в кухне »). C'est une exception à retenir.","кухне",["кухня","диван"],["а ужинать мы будем на кухне","а мы будем ужинать на кухне"],"Pour dire où : « на кухне » (-е). « Кухня », c'est la forme de base.")],
 parts=[{"titleFr":"La visite","steps":[SC,B(["flat","bigflat"]),B(["room","toilet"],["bigflat"]),EX,I(0)]},
   {"titleFr":"Qui dort où ?","steps":[W(["flat","room","toilet"]),B(["there","sleep"],["room"]),B(["sofa","kitchen"],["sleep","there"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anton","fr":["Tu connais bien ce vert maintenant : « в комнате », « в квартире », « в сумке ». Pour dire où se trouve quelque chose, -е à la fin.","Ça marche pour les choses aussi, pas seulement les villes !"]},
   {"by":"anton","fr":["Certains lieux prennent « на » au lieu de « в » : « на кухне » (dans la cuisine), « на диване » (sur le canapé), « на работе » (au travail).","Pas de règle simple : retiens-les avec leur « на »."]}],
 explore={"type":"case","speaker":"anton","case":"loct","frame":"Кошка в ___.","frameFr":"Le chat est dans ___.","color":"#2a9d8f","hintFr":"Mets chaque endroit après « в » et regarde bien la fin du mot.","words":[
   {"tile":"комната","fr":"la chambre","phraseFr":"Le chat est dans la chambre."},{"tile":"квартира","fr":"l'appartement","phraseFr":"Le chat est dans l'appartement."},
   {"tile":"сумка","fr":"le sac","phraseFr":"Le chat est dans le sac."},{"tile":"коробка","fr":"la boîte","phraseFr":"Le chat est dans la boîte."}]},
 tasks=[{"type":"pick","fr":"Dis que le chat est dans le sac.","answer":"сумка"},{"type":"pick","fr":"Dis que le chat est dans la boîte.","answer":"коробка"}],
 cando=["décrire un appartement","demander où sont les toilettes","dire où se trouve quelque chose"],
 unlocks=[{"case":"loct","gender":"femn","from":"комната","to":"комнате"}],
 glossary=G({"вот":"voici","квартира":"appartement","квартире":"appartement (après в)","проходите":"entrez","какая":"quelle","большая":"grande","большой":"grand","комната":"chambre, pièce","комнате":"chambre (après в)","кухня":"cuisine","кухне":"cuisine (на кухне)","туалет":"toilettes","там":"là-bas","направо":"à droite","будет":"(il) sera / va","спать":"dormir","сплю":"(je) dors","здесь":"ici","диване":"canapé (après на)","диван":"canapé","отлично":"parfait","ужинать":"dîner","мы":"nous","будем":"(nous) allons","антон":"Anton (prénom)","кошка":"chat","сумка":"sac","сумке":"sac (après в)","коробка":"boîte","коробке":"boîte (après в)"}),
 combos=[C("Моя сестра в Москве, а я в Петербурге.","Ma sœur est à Moscou, et moi, je suis à Saint-Pétersbourg.",["москва"]),
   C("Кошка на диване.","Le chat est sur le canapé.",["кухня"],["кошка на диване","на диване кошка"]),
   C("Где моя сумка? На кухне?","Où est mon sac ? Dans la cuisine ?",["кухня"])])

# ---------------- 22. J'aime bien ----------------
lesson(id="22-plaire", order=22, titleFr="Ça te plaît ?", titleRu="Тебе нравится?", emoji="💛",
 sceneFr="Le 1er janvier, en se promenant dans Moscou, Anton demande à Luka ce qu'il pense de la ville.",
 dialogue=[D("anton","Л+ука, тебе нравится Москва?","Luka, Moscou te plaît ?"),
   D("luka","Да, очень нравится!","Oui, beaucoup !"),
   D("luka","Мне нравится метро. Оно очень красивое.","J'aime bien le métro. Il est très beau."),
   D("anton","А что тебе не нравится?","Et qu'est-ce qui ne te plaît pas ?"),
   D("luka","Мне не нравится холод!","Je n'aime pas le froid !"),
   D("masha","А мне нравится зима!","Et moi, j'aime l'hiver !"),
   D("anton","Маша любит зиму, а я люблю лето.","Macha aime l'hiver, et moi, j'aime l'été."),
   D("luka","Я тоже люблю лето!","Moi aussi, j'aime l'été !")],
 phrases=[
   ph("like","anton","Тебе нравится Москва?","Moscou te plaît ?","Mot à mot : « à toi plaît Moscou ? ». « Тебе » = à toi.","тебе",["тебя","меня"],["тебе нравится москва","москва тебе нравится"],"Avec « нравится », c'est « тебе » (à toi). « Тебя » sert dans « у тебя есть »."),
   ph("verymuch","luka","Да, очень нравится!","Oui, beaucoup !","« Очень нравится » = ça me plaît beaucoup.","нравится",["тоже","холод"]),
   ph("metro","luka","Мне нравится метро.","J'aime bien le métro.","« Мне нравится » = ça me plaît, j'aime bien. Mot à mot : « à moi plaît le métro ».","мне",["меня","тебя"],["мне нравится метро","метро мне нравится"],"Pour soi : « мне нравится » (à moi). « Меня » sert dans « меня зовут »."),
   ph("beautiful","luka","Оно очень красивое.","Il est très beau.","« Метро » est neutre : « оно » (il) et « красивое » (-ое).","красивое",["красивая","холод"],None,"« Метро » est neutre : « красивое » (-ое). « Красивая », c'est pour un mot féminin."),
   ph("dislike","anton","А что тебе не нравится?","Et qu'est-ce qui ne te plaît pas ?","« Не нравится » = ne plaît pas.","не",["холод","лето"]),
   ph("cold","luka","Мне не нравится холод!","Je n'aime pas le froid !","« Холод » = le froid (le nom). Tu connais « холодно » (il fait froid).","холод",["холодно","зиму"],None,"Ici il faut un nom : « холод » (le froid). « Холодно », c'est « il fait froid »."),
   ph("winter","masha","А мне нравится зима!","Et moi, j'aime l'hiver !","Avec « нравится », la chose qui plaît reste à la forme de base : « зима » (et pas « зиму » !).","зима",["зиму","холодно"],["а мне нравится зима","а мне зима нравится"],"Avec « нравится », forme de base : « зима ». « Зиму », c'est après « люблю »."),
   ph("summer","anton","Маша любит зиму, а я люблю лето.","Macha aime l'hiver, et moi, j'aime l'été.","Avec « люблю / любит », le bleu : « зиму ». « Лето » (été, neutre) ne change pas.","зиму",["зима","нравится"],None,"Après « любит », le bleu : « зиму » (-у). Avec « нравится », ce serait « зима »."),
   ph("metoo","luka","Я тоже люблю лето!","Moi aussi, j'aime l'été !","« Тоже » = aussi.","тоже",["мне","тебе"])],
 parts=[{"titleFr":"Ça me plaît","steps":[SC,B(["like","verymuch"]),EX,I(0),B(["metro","beautiful"],["like"])]},
   {"titleFr":"Les goûts","steps":[W(["like","verymuch","metro"]),B(["dislike","cold"],["metro","beautiful"]),B(["winter","summer","metoo"],["cold"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anton","fr":["« Мне нравится… » = j'aime bien, ça me plaît. Mot à mot : « à moi plaît… ».","Et la chose qui plaît reste à la forme de base : « мне нравится Москва », « мне нравится музыка ». Pas de -у ici !"]},
   {"by":"anton","fr":["Compare : « я люблю зиму » (bleu, -у) mais « мне нравится зима » (forme de base). Même idée, deux constructions.","Pour les autres : « тебе нравится » (ça te plaît), « Маше нравится » (ça plaît à Macha)."]}],
 explore={"type":"plain","speaker":"luka","frame":"Мне нравится ___.","frameFr":"J'aime bien ___.","color":"#5c677d","hintFr":"Mets chaque mot après « нравится » et écoute : le mot ne change pas !","words":[
   {"tile":"Москва","fr":"Moscou","phraseFr":"Moscou me plaît."},{"tile":"музыка","fr":"la musique","phraseFr":"J'aime bien la musique."},
   {"tile":"зима","fr":"l'hiver","phraseFr":"J'aime bien l'hiver."},{"tile":"метро","fr":"le métro","phraseFr":"J'aime bien le métro."}]},
 tasks=[{"type":"pick","fr":"Dis que tu aimes bien la musique.","answer":"музыка"},{"type":"pick","fr":"Dis que l'hiver te plaît.","answer":"зима"}],
 cando=["dire ce qui te plaît","dire ce qui ne te plaît pas","demander l'avis de quelqu'un"],
 unlocks=[],
 glossary=G({"тебе":"à toi","нравится":"plaît","мне":"à moi","метро":"métro","оно":"il (neutre)","красивое":"beau (neutre)","красивая":"belle","холод":"le froid","холодно":"il fait froid","зима":"hiver","зиму":"hiver (après люблю)","любит":"(il, elle) aime","люблю":"(j')aime","лето":"été","тоже":"aussi","москва":"Moscou","музыка":"musique","меня":"me, moi","тебя":"te, toi"}),
 combos=[C("Тебе нравится Ли+он?","Lyon te plaît ?",["тебя"],["тебе нравится лион","лион тебе нравится"]),
   C("Мне не нравится зима, но я люблю лето.","Je n'aime pas l'hiver, mais j'aime l'été.",["зиму"]),
   C("Мне очень нравится музыка.","J'aime beaucoup la musique.",["музыку"],["мне очень нравится музыка","музыка мне очень нравится"])])

# ---------------- 23. Pouvoir ----------------
lesson(id="23-patinoire", order=23, titleFr="À la patinoire", titleRu="На катке", emoji="⛸️",
 sceneFr="Le 2 janvier, Anton emmène Luka et Macha à la patinoire. Luka n'a jamais patiné…",
 dialogue=[D("anton","Пойдём на каток!","Allons à la patinoire !"),
   D("luka","Но я не умею кататься на коньках.","Mais je ne sais pas patiner."),
   D("anton","Ничего, я могу помочь.","Pas grave, je peux t'aider."),
   D("masha","Это просто! Смотри!","C'est facile ! Regarde !"),
   D("luka","Антон, ты можешь мне помочь?","Anton, tu peux m'aider ?"),
   D("anton","Конечно! Дай руку.","Bien sûr ! Donne-moi la main."),
   D("luka","Ой! Я упал!","Aïe ! Je suis tombé !"),
   D("masha","Ничего! Ещё раз!","Pas grave ! Encore une fois !")],
 phrases=[
   ph("rink","anton","Пойдём на каток!","Allons à la patinoire !","« Каток » = patinoire. « Пойдём » = allons. Tu connais « давай пойдём ».","каток",["катке","помочь"],None,"On y va : « на каток » (forme de base). « На катке », c'est quand on y est."),
   ph("cant","luka","Но я не умею кататься на коньках.","Mais je ne sais pas patiner.","« Уметь » = savoir faire. « Я не умею » = je ne sais pas (faire). « Кататься на коньках » = patiner.","умею",["можешь","каток"],None,"Pour une compétence (savoir patiner) : « умею ». « Могу », c'est « je peux »."),
   ph("canhelp","anton","Ничего, я могу помочь.","Pas grave, je peux t'aider.","« Я могу » = je peux. « Помочь » = aider.","могу",["можешь","умею"],["ничего я могу помочь"],"Avec « я » : « могу ». « Можешь », c'est pour « ты »."),
   ph("easy","masha","Это просто! Смотри!","C'est facile ! Regarde !","« Просто » = facile, simple. « Смотри ! » = regarde !","просто",["помочь","руку"]),
   ph("canyou","luka","Антон, ты можешь мне помочь?","Anton, tu peux m'aider ?","« Ты можешь » = tu peux. « Мне помочь » = m'aider.","можешь",["могу","умею"],["антон ты можешь мне помочь","антон ты можешь помочь мне"],"Avec « ты » : « можешь ». « Могу », c'est pour « я »."),
   ph("hand","anton","Конечно! Дай руку.","Bien sûr ! Donne-moi la main.","« Дай » = donne (à « ты »). « Рука » = main → « дай руку » (-у).","руку",["рука","каток"],None,"On donne la main : le bleu, « рука » → « руку »."),
   ph("fell","luka","Ой! Я упал!","Aïe ! Je suis tombé !","« Я упал » = je suis tombé (homme). Une femme dirait « я упала ».","упал",["упала","могу"],None,"Luka est un homme : « упал ». « Упала », c'est pour une femme."),
   ph("again","masha","Ничего! Ещё раз!","Pas grave ! Encore une fois !","« Ещё раз » = encore une fois.","раз",["каток","упал"])],
 parts=[{"titleFr":"Je ne sais pas…","steps":[SC,B(["rink","cant"]),B(["canhelp","easy"],["cant"]),EX,I(0)]},
   {"titleFr":"Tu peux m'aider ?","steps":[W(["rink","cant","canhelp"]),B(["canyou","hand"],["canhelp","easy"]),B(["fell","again"],["canyou"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anton","fr":["« Мочь » = pouvoir : я могу, ты можешь, он может, мы можем, вы можете, они могут.","Comme « хочу », on ajoute un verbe à l'infinitif : « я могу помочь », « ты можешь говорить медленнее ? »."]},
   {"by":"anton","fr":["Attention : « уметь » = savoir faire (une compétence) : « я умею кататься », « я не умею плавать ».","« Мочь » = pouvoir (c'est possible, j'ai le temps, j'ai le droit) : « я не могу, я работаю »."]}],
 explore={"type":"person","speaker":"anton","verb":"мочь","frame":"___ {V} помочь.","frameFr":"___ pouvoir aider.","color":"#8e44ad","hintFr":"Change la personne et écoute le verbe : il change beaucoup !","words":[
   {"tile":"я","fr":"je","phraseFr":"Je peux aider."},{"tile":"ты","fr":"tu","phraseFr":"Tu peux aider."},
   {"tile":"он","fr":"il","phraseFr":"Il peut aider."},{"tile":"мы","fr":"nous","phraseFr":"Nous pouvons aider."},
   {"tile":"вы","fr":"vous","phraseFr":"Vous pouvez aider."},{"tile":"они","fr":"ils, elles","phraseFr":"Ils peuvent aider."}]},
 tasks=[{"type":"pick","fr":"Dis : « Nous pouvons aider. »","answer":"мы"},{"type":"pick","fr":"Dis : « Vous pouvez aider. »","answer":"вы"}],
 cando=["dire ce que tu sais faire","demander de l'aide","dire « je peux / je ne peux pas »"],
 unlocks=[],
 glossary=G({"пойдём":"allons","пойдем":"allons","каток":"patinoire","катке":"patinoire (on y est)","но":"mais","умею":"(je) sais (faire)","кататься":"glisser, faire du…","коньках":"patins (на коньках)","ничего":"pas grave","могу":"(je) peux","можешь":"(tu) peux","может":"(il) peut","можем":"(nous) pouvons","можете":"(vous) pouvez","могут":"(ils) peuvent","помочь":"aider","просто":"facile, simple","смотри":"regarde !","антон":"Anton (prénom)","конечно":"bien sûr","дай":"donne !","руку":"main (après дай)","рука":"main","ой":"aïe, oh","упал":"(je suis) tombé","упала":"(je suis) tombée","ещё":"encore","раз":"fois","он":"il","мы":"nous","они":"ils, elles"}),
 combos=[C("Я не могу, я работаю.","Je ne peux pas, je travaille.",["умею"],["я не могу я работаю"]),
   C("Ты можешь говорить медленнее?","Tu peux parler plus lentement ?",["могу"],["ты можешь говорить медленнее","ты можешь медленнее говорить"]),
   C("Я не умею играть в футбол.","Je ne sais pas jouer au foot.",["могу"])])

# ---------------- 24. Le retour ----------------
lesson(id="24-retour", order=24, titleFr="De retour", titleRu="Снова дома", emoji="🧳",
 sceneFr="De retour à Saint-Pétersbourg, Luka retrouve Oleg et lui raconte son voyage à Moscou.",
 dialogue=[D("oleg","Привет, Л+ука! Ну, как Москва?","Salut, Luka ! Alors, comment c'était Moscou ?"),
   D("luka","Привет! Было очень интересно!","Salut ! C'était très intéressant !"),
   D("oleg","Что вы делали?","Qu'est-ce que vous avez fait ?"),
   D("luka","Мы гуляли в центре и смотрели Кремль.","On s'est promenés dans le centre et on a regardé le Kremlin."),
   D("luka","А Новый год мы встречали у Антона.","Et on a fêté le Nouvel An chez Anton."),
   D("oleg","А что ещё?","Et quoi d'autre ?"),
   D("luka","Мы были на катке. Я катался, но плохо!","On est allés à la patinoire. J'ai patiné, mais mal !"),
   D("oleg","Молодец! Тебе понравилась Москва?","Bravo ! Moscou t'a plu ?"),
   D("luka","Очень понравилась! Но Петербург я люблю больше.","Beaucoup ! Mais je préfère Saint-Pétersbourg.")],
 phrases=[
   ph("howwas","oleg","Ну, как Москва?","Alors, comment c'était Moscou ?","« Ну » = alors, bon. On l'entend partout en russe.","москва",["москве","центре"]),
   ph("interesting","luka","Было очень интересно!","C'était très intéressant !","Tu le connais : « было » = c'était.","было",["был","были"],None,"Pour « c'était » (sans nom), on dit « было »."),
   ph("whatdid","oleg","Что вы делали?","Qu'est-ce que vous avez fait ?","Au pluriel, le passé finit en -ли : « вы делали ».","делали",["делал","делаете"],None,"Avec « вы » (ou « мы »), le passé finit en -ли : « делали »."),
   ph("walked","luka","Мы гуляли в центре и смотрели Кремль.","On s'est promenés dans le centre et on a regardé le Kremlin.","« Гуляли » = nous nous sommes promenés. « В центре » = dans le centre.","гуляли",["гулял","гулять"],["мы гуляли в центре и смотрели кремль","мы смотрели кремль и гуляли в центре"],"Avec « мы », le passé finit en -ли : « гуляли »."),
   ph("newyear","luka","А Новый год мы встречали у Антона.","Et on a fêté le Nouvel An chez Anton.","« Встречать Новый год » = fêter le Nouvel An (mot à mot : accueillir). « У Антона » = chez Anton (comme « у меня »).","встречали",["встречал","катке"]),
   ph("rink","luka","Мы были на катке.","On est allés à la patinoire.","« Мы были » = nous étions. « На катке » : le vert du lieu.","катке",["каток","центр"],None,"On y était : « на катке » (-е). « На каток », c'est quand on y va."),
   ph("skated","luka","Я катался, но плохо!","J'ai patiné, mais mal !","« Я катался » = j'ai patiné (homme).","плохо",["катке","было"],None,"Luka a patiné « mais mal » : « но плохо »."),
   ph("liked","oleg","Тебе понравилась Москва?","Moscou t'a plu ?","Le passé de « нравится » : « понравилась » (Moscou est féminin).","понравилась",["понравилось","понравился"],None,"Au passé, et « Москва » est féminin : « понравилась »."),
   ph("more","luka","Но Петербург я люблю больше.","Mais je préfère Saint-Pétersbourg.","« Больше » = plus. « Люблю больше » = j'aime plus, je préfère.","больше",["было","были"])],
 parts=[{"titleFr":"Raconter","steps":[SC,EX,I(0),B(["howwas","interesting"]),B(["whatdid","walked"],["interesting"])]},
   {"titleFr":"La fête et la patinoire","steps":[W(["howwas","interesting","walked"]),B(["newyear","rink"],["whatdid","walked"]),B(["skated","liked","more"],["rink"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"oleg","fr":["Pour raconter ce que « nous » avons fait : le passé en -ли. « Мы гуляли », « мы смотрели », « мы были ».","Rappel : homme -л (я гулял), femme -ла (я гуляла), pluriel -ли (мы гуляли)."]},
   {"by":"oleg","fr":["Le passé de « нравится » : « понравился » (masculin), « понравилась » (féminin), « понравилось » (neutre). « Мне понравилось ! » = ça m'a plu !","Bravo : tu sais maintenant raconter un voyage entier en russe !"]}],
 explore={"type":"plain","speaker":"luka","frame":"Вчера мы ___.","frameFr":"Hier, nous ___.","color":"#5c677d","hintFr":"Écoute la fin : avec « мы », le passé finit en -ли.","words":[
   {"tile":"гуляли","fr":"nous sommes promenés","phraseFr":"Hier, nous nous sommes promenés."},{"tile":"отдыхали","fr":"nous sommes reposés","phraseFr":"Hier, nous nous sommes reposés."},
   {"tile":"работали","fr":"avons travaillé","phraseFr":"Hier, nous avons travaillé."},{"tile":"ужинали","fr":"avons dîné","phraseFr":"Hier, nous avons dîné."}]},
 tasks=[{"type":"pick","fr":"Dis : « Hier, nous avons travaillé. »","answer":"работали"},{"type":"pick","fr":"Dis : « Hier, nous avons dîné. »","answer":"ужинали"}],
 cando=["raconter un voyage","parler au passé au pluriel","dire ce qui t'a plu"],
 unlocks=[{"case":"loct","gender":"masc","from":"центр","to":"центре"}],
 glossary=G({"ну":"alors, bon","москва":"Moscou","москве":"Moscou (après в)","было":"c'était","был":"(il) était","будет":"(ce) sera","интересно":"intéressant","делали":"(vous) avez fait","делал":"(il) a fait","делаете":"(vous) faites","мы":"nous","гуляли":"(nous) nous sommes promenés","гулял":"(il) s'est promené","гулять":"se promener","центре":"centre (après в)","центр":"centre","смотрели":"(nous) avons regardé","кремль":"Kremlin","новый":"nouveau","год":"année","встречали":"(nous) avons fêté, accueilli","встречал":"(il) a fêté","антона":"Anton (у Антона = chez Anton)","ещё":"encore","были":"(nous) étions","катке":"patinoire (on y est)","каток":"patinoire","катался":"(j')ai patiné","но":"mais","плохо":"mal","молодец":"bravo","тебе":"à toi","понравилась":"a plu (féminin)","понравился":"a plu (masculin)","понравилось":"a plu (neutre)","нравится":"plaît","петербург":"Saint-Pétersbourg","люблю":"(j')aime","больше":"plus","отдыхали":"(nous) nous sommes reposés","работали":"(nous) avons travaillé","ужинали":"(nous) avons dîné"}),
 combos=[C("Вчера мы были в театре.","Hier, nous étions au théâtre.",["театр"],["вчера мы были в театре","мы были в театре вчера"]),
   C("Мне понравилась Москва, но я люблю Петербург.","Moscou m'a plu, mais j'aime Saint-Pétersbourg.",["нравится"]),
   C("Вы гуляли в центре?","Vous vous êtes promenés dans le centre ?",["гулять"],["вы гуляли в центре","в центре вы гуляли"])])
print("ok")
