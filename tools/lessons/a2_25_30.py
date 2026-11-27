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
COMMON={"здравствуйте":"bonjour (poli)","тебе":"à toi","здесь":"ici","я":"je, moi","ты":"tu","вы":"vous","да":"oui","нет":"non","а":"et, mais","и":"et","это":"c'est, voici","не":"ne… pas","в":"dans, à","на":"sur, en","что":"quoi, que","как":"comment, comme","где":"où","очень":"très","спасибо":"merci","пожалуйста":"s'il te plaît / je t'en prie","хорошо":"bien, d'accord","привет":"salut","лука":"Luka (prénom)","маша":"Macha (prénom)","олег":"Oleg (prénom)","анна":"Anna (prénom)","у":"chez","меня":"moi (у меня = j'ai)","тебя":"toi (у тебя = tu as)","есть":"il y a","мой":"mon","моя":"ma","мне":"à moi","тоже":"aussi","сегодня":"aujourd'hui","завтра":"demain","вчера":"hier","потом":"puis, ensuite","давай":"allons-y, faisons"}
def G(d): return {**COMMON, **d}
def C(ru, fr, extra, orders=None, note=""):
    d={"ru":ru,"fr":fr,"extra":extra}
    if orders: d["orders"]=orders
    if note: d["noteFr"]=note
    return d



# ---------------- 25. Au téléphone ----------------
lesson(id="25-telephone", order=25, titleFr="Au téléphone", titleRu="По телефону", emoji="📞",
 sceneFr="Fin janvier, c'est bientôt l'anniversaire de Luka. Il appelle Anna pour l'inviter.",
 dialogue=[D("luka","Алло, +Анна? Это Л+ука.","Allô, Anna ? C'est Luka."),
   D("anna","Привет, Л+ука! Как дела?","Salut, Luka ! Comment ça va ?"),
   D("luka","Хорошо, спасибо! В субботу у меня день рождения.","Bien, merci ! Samedi, c'est mon anniversaire."),
   D("luka","Приходи ко мне!","Viens chez moi !"),
   D("anna","С удовольствием! Во сколько?","Avec plaisir ! À quelle heure ?"),
   D("luka","В шесть часов.","À six heures."),
   D("anna","Отлично, я приду. Что тебе подарить?","Parfait, je viendrai. Qu'est-ce que je peux t'offrir ?"),
   D("luka","Ничего не надо! Просто приходи.","Rien du tout ! Viens, c'est tout.")],
 phrases=[
   ph("itsme","luka","Алло, +Анна? Это Л+ука.","Allô, Anna ? C'est Luka.","Au téléphone, on se présente avec « это » : « Это Лука » = c'est Luka.","это",["меня","дела"]),
   ph("howareyou","anna","Как дела?","Comment ça va ?","« Как дела ? » = comment ça va ? (mot à mot : comment les affaires ?). Entre amis.","дела",["приду","часов"]),
   ph("birthday","luka","В субботу у меня день рождения.","Samedi, c'est mon anniversaire.","« День рождения » = anniversaire (mot à mot : jour de naissance). « У меня день рождения » = c'est mon anniversaire.","рождения",["часов","дела"],["в субботу у меня день рождения","у меня в субботу день рождения","у меня день рождения в субботу"]),
   ph("come","luka","Приходи ко мне!","Viens chez moi !","« Приходи ! » = viens ! (à « ты »). « Ко мне » = chez moi (quand on y va).","приходи",["приду","подарить"],None,"Pour inviter « ты » : « приходи ! ». « Приду », c'est « je viendrai »."),
   ph("when","anna","С удовольствием! Во сколько?","Avec plaisir ! À quelle heure ?","Tu connais les deux expressions depuis l'invitation au théâtre !","сколько",["шесть","дела"]),
   ph("six","luka","В шесть часов.","À six heures.","« В шесть часов » = à six heures. De 5 à 20 : « часов ».","шесть",["приду","дела"]),
   ph("willcome","anna","Отлично, я приду.","Parfait, je viendrai.","« Я приду » = je viendrai.","приду",["приходи","подарить"],None,"Pour dire « je viendrai » : « я приду ». « Приходи », c'est « viens ! »."),
   ph("gift","anna","Что тебе подарить?","Qu'est-ce que je peux t'offrir ?","« Подарить » = offrir. « Тебе » = à toi.","подарить",["приходи","приду"]),
   ph("nothing","luka","Ничего не надо! Просто приходи.","Rien du tout ! Viens, c'est tout.","« Ничего не надо » = il ne faut rien. « Просто » = simplement.","надо",["часов","дела"])],
 parts=[{"titleFr":"L'appel","steps":[SC,B(["itsme","howareyou"]),B(["birthday","come"],["howareyou"]),I(0)]},
   {"titleFr":"L'heure et le cadeau","steps":[W(["itsme","birthday","come"]),B(["when","six"],["come"]),EX,I(1),B(["willcome","gift","nothing"],["six"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anna","fr":["Au téléphone : « Алло ! », puis « Это Лука » (c'est Luka). Et entre amis : « Как дела ? » — « Хорошо, спасибо ! ».","« У меня день рождения » = c'est mon anniversaire (mot à mot : chez moi, il y a un jour de naissance). Tu reconnais « у меня » !"]},
   {"by":"anna","fr":["Pour l'heure : « в » + le nombre + « часов » : « в пять часов », « в шесть часов », « в семь часов ».","Avec 2, 3, 4 : « часа » (« в два часа »). Avec 1 : « в час ». On se comprend même si tu te trompes !"]}],
 explore={"type":"plain","speaker":"luka","frame":"Приходи в ___ часов!","frameFr":"Viens à ___ heures !","color":"#5c677d","hintFr":"Mets chaque nombre dans la phrase et écoute.","words":[
   {"tile":"пять","fr":"cinq","phraseFr":"Viens à cinq heures !"},{"tile":"шесть","fr":"six","phraseFr":"Viens à six heures !"},
   {"tile":"семь","fr":"sept","phraseFr":"Viens à sept heures !"},{"tile":"восемь","fr":"huit","phraseFr":"Viens à huit heures !"}]},
 tasks=[{"type":"pick","fr":"Dis : « Viens à huit heures ! »","answer":"восемь"},{"type":"pick","fr":"Dis : « Viens à cinq heures ! »","answer":"пять"}],
 cando=["téléphoner à un ami","inviter quelqu'un chez toi","donner une heure"],
 unlocks=[],
 glossary=G({"алло":"allô","как":"comment","дела":"affaires (как дела = ça va ?)","субботу":"samedi (в субботу)","день":"jour","рождения":"naissance (день рождения = anniversaire)","приходи":"viens !","ко":"chez, vers (ко мне = chez moi)","с":"avec","удовольствием":"plaisir (с удовольствием = avec plaisir)","во":"à (во сколько = à quelle heure)","сколько":"combien","шесть":"six","часов":"heures","отлично":"parfait","приду":"(je) viendrai","подарить":"offrir","ничего":"rien","надо":"il faut","просто":"simplement","пять":"cinq","семь":"sept","восемь":"huit"}),
 combos=[C("Приходи ко мне в субботу!","Viens chez moi samedi !",["приду"],["приходи ко мне в субботу","в субботу приходи ко мне"]),
   C("Алло, Маша? Это Лука. Как дела?","Allô, Macha ? C'est Luka. Ça va ?",["меня"]),
   C("Завтра в семь часов я буду дома.","Demain à sept heures, je serai à la maison.",["приду"],["завтра в семь часов я буду дома","завтра я буду дома в семь часов"])])

# ---------------- 26. L'anniversaire ----------------
lesson(id="26-anniversaire", order=26, titleFr="Joyeux anniversaire !", titleRu="С днём рождения!", emoji="🎂",
 sceneFr="Samedi, six heures. Les amis arrivent chez Luka pour son anniversaire.",
 dialogue=[D("anna","С днём рождения, Л+ука!","Joyeux anniversaire, Luka !"),
   D("luka","Спасибо! Проходи!","Merci ! Entre !"),
   D("anna","Это тебе подарок.","C'est un cadeau pour toi."),
   D("luka","Какой красивый шарф! Спасибо!","Quelle belle écharpe ! Merci !"),
   D("oleg","Л+ука, сколько тебе лет?","Luka, quel âge as-tu ?"),
   D("luka","Мне двадцать пять лет.","J'ai vingt-cinq ans."),
   D("masha","А мне тридцать. Я старше!","Et moi, trente. Je suis plus âgée !"),
   D("oleg","Желаю тебе счастья и здоровья!","Je te souhaite du bonheur et la santé !")],
 phrases=[
   ph("happybd","anna","С днём рождения!","Joyeux anniversaire !","Comme « с Новым годом », avec « с ». Mot à mot : « avec le jour de naissance ! ».","днём",["день","подарок"],None,"Après « с » : « с днём рождения ». Retiens-le tel quel, comme « с Новым годом »."),
   ph("enter","luka","Спасибо! Проходи!","Merci ! Entre !","« Проходи ! » = entre ! (à « ты »). Anton disait « проходите » (à « вы »).","проходи",["проходите","лет"],None,"Anna est une amie : on la tutoie, « проходи ». « Проходите », c'est pour « вы »."),
   ph("present","anna","Это тебе подарок.","C'est un cadeau pour toi.","« Подарок » = cadeau. « Тебе » = à toi, pour toi.","подарок",["лет","желаю"]),
   ph("scarf","luka","Какой красивый шарф!","Quelle belle écharpe !","« Шарф » est masculin : « какой красивый ».","какой",["какая","сколько"],["какой красивый шарф"],"« Шарф » est masculin : « какой » (-ой). « Какая », c'est pour un mot féminin."),
   ph("age","oleg","Л+ука, сколько тебе лет?","Luka, quel âge as-tu ?","Mot à mot : « combien à toi d'années ? ». L'âge se dit avec « мне / тебе ».","тебе",["тебя","меня"],["лука сколько тебе лет"],"Pour l'âge : « тебе » (à toi). « Тебя » sert dans « у тебя »."),
   ph("twentyfive","luka","Мне двадцать пять лет.","J'ai vingt-cinq ans.","« Мне … лет » = j'ai … ans. Mot à mot : « à moi vingt-cinq années ».","мне",["меня","тебя"],["мне двадцать пять лет"],"Pour son âge : « мне » (à moi). Pas « у меня » ici !"),
   ph("older","masha","А мне тридцать. Я старше!","Et moi, trente. Je suis plus âgée !","« Старше » = plus âgé(e).","тридцать",["желаю","лет"]),
   ph("wish","oleg","Желаю тебе счастья и здоровья!","Je te souhaite du bonheur et la santé !","« Желаю тебе… » = je te souhaite… La formule de tous les anniversaires russes.","желаю",["подарок","лет"])],
 parts=[{"titleFr":"Les invités","steps":[SC,B(["happybd","enter"]),B(["present","scarf"],["happybd"]),I(1)]},
   {"titleFr":"L'âge","steps":[W(["happybd","present","scarf"]),EX,I(0),B(["age","twentyfive"],["present"]),B(["older","wish"],["age","twentyfive"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"oleg","fr":["Pour l'âge, le russe dit « à moi … années » : « мне двадцать лет » (j'ai vingt ans), « тебе тридцать лет ».","Le mot « ans » change : « двадцать лет », mais « двадцать один год », « двадцать два года ». On t'a appris le plus simple : 20, 25, 30… → « лет »."]},
   {"by":"anna","fr":["Les formules de fête commencent par « с » : « С днём рождения ! », « С Новым годом ! ».","Et pour souhaiter : « Желаю тебе счастья ! » (je te souhaite du bonheur)."]}],
 explore={"type":"plain","speaker":"luka","frame":"Мне ___ лет.","frameFr":"J'ai ___ ans.","color":"#5c677d","hintFr":"Mets chaque âge dans la phrase et écoute.","words":[
   {"tile":"двадцать","fr":"vingt","phraseFr":"J'ai vingt ans."},{"tile":"тридцать","fr":"trente","phraseFr":"J'ai trente ans."},
   {"tile":"сорок","fr":"quarante","phraseFr":"J'ai quarante ans."},{"tile":"пятьдесят","fr":"cinquante","phraseFr":"J'ai cinquante ans."}]},
 tasks=[{"type":"pick","fr":"Dis : « J'ai quarante ans. »","answer":"сорок"},{"type":"pick","fr":"Dis : « J'ai vingt ans. »","answer":"двадцать"}],
 cando=["souhaiter un joyeux anniversaire","dire ton âge","remercier pour un cadeau"],
 unlocks=[],
 glossary=G({"с":"avec","днём":"jour (с днём рождения = joyeux anniversaire)","день":"jour","рождения":"naissance","проходи":"entre !","проходите":"entrez !","тебе":"à toi","подарок":"cadeau","какой":"quel","какая":"quelle","красивый":"beau","шарф":"écharpe","сколько":"combien","лет":"ans","двадцать":"vingt","пять":"cinq","тридцать":"trente","старше":"plus âgé(e)","желаю":"(je) souhaite","счастья":"bonheur","здоровья":"santé","сорок":"quarante","пятьдесят":"cinquante"}),
 combos=[C("Какой красивый подарок!","Quel beau cadeau !",["какая"]),
   C("Сколько тебе лет? Мне сорок лет.","Quel âge as-tu ? J'ai quarante ans.",["меня"]),
   C("Мне двадцать лет, а тебе?","J'ai vingt ans, et toi ?",["меня"])])

# ---------------- 27. Il n'y a plus de… ----------------
lesson(id="27-plus-de", order=27, titleFr="Il n'y a plus de pain !", titleRu="Нет хлеба!", emoji="🥖",
 sceneFr="Pendant la fête, Luka ouvre le frigo… il manque des choses ! Oleg propose d'aller au magasin.",
 dialogue=[D("luka","Ой! У нас нет хлеба!","Oh ! On n'a plus de pain !"),
   D("oleg","И сока тоже нет.","Et il n'y a plus de jus non plus."),
   D("luka","А вода есть?","Et de l'eau, il y en a ?"),
   D("oleg","Нет, воды тоже нет!","Non, plus d'eau non plus !"),
   D("luka","Где здесь магазин?","Où est le magasin, par ici ?"),
   D("oleg","Рядом, две минуты. Я пойду.","Tout près, deux minutes. J'y vais."),
   D("luka","Спасибо! Купи хлеб, сок и воду.","Merci ! Achète du pain, du jus et de l'eau."),
   D("oleg","Хорошо. Что-нибудь ещё?","D'accord. Autre chose ?")],
 phrases=[
   ph("nobread","luka","У нас нет хлеба!","On n'a plus de pain !","« У нас » = chez nous. « Нет » + le mot qui change : « хлеб » → « нет хлеба ».","хлеба",["хлеб","рядом"],["у нас нет хлеба"],"Après « нет » (il n'y a pas), « хлеб » devient « хлеба » (-а)."),
   ph("nojuice","oleg","И сока тоже нет.","Et il n'y a plus de jus non plus.","« Сок » = jus → « нет сока ».","сока",["сок","воду"],None,"Après « нет », « сок » → « сока »."),
   ph("water","luka","А вода есть?","Et de l'eau, il y en a ?","Avec « есть » (il y a), le mot reste à la forme de base : « вода есть ».","вода",["воды","воду"],["а вода есть","а есть вода"],"Avec « есть », forme de base : « вода ». Avec « нет », ce serait « воды »."),
   ph("nowater","oleg","Нет, воды тоже нет!","Non, plus d'eau non plus !","« Вода » → « нет воды » : -а devient -ы.","воды",["вода","воду"],None,"Après « нет », « вода » → « воды » (-ы)."),
   ph("shop","luka","Где здесь магазин?","Où est le magasin, par ici ?","« Магазин » = magasin. Même phrase que « где здесь банк ? ».","магазин",["магазине","рядом"]),
   ph("near","oleg","Рядом, две минуты. Я пойду.","Tout près, deux minutes. J'y vais.","« Рядом » = tout près, à côté. « Я пойду » = j'y vais.","рядом",["воды","купи"]),
   ph("buy","luka","Купи хлеб, сок и воду.","Achète du pain, du jus et de l'eau.","« Купи ! » = achète ! Ici, ce qu'on achète prend le bleu : « воду ». Pas « нет » ici !","воду",["нет","вода"],["купи хлеб сок и воду","купи сок хлеб и воду"],"On achète l'eau : le bleu, « воду ». « Воды », c'est après « нет »."),
   ph("more","oleg","Хорошо. Что-нибудь ещё?","D'accord. Autre chose ?","Tu connais cette phrase du café !","ещё",["купи","нет"])],
 parts=[{"titleFr":"Le frigo est vide","steps":[SC,EX,I(0),B(["nobread","nojuice"]),B(["water","nowater"],["nobread"])]},
   {"titleFr":"Au magasin !","steps":[W(["nobread","nojuice","nowater"]),B(["shop","near"],["water","nowater"]),B(["buy","more"],["nobread","near"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"oleg","fr":["Nouvelle couleur : l'orange ! Après « нет » (il n'y a pas), le mot change : « хлеб » → « нет хлеба », « вода » → « нет воды », « молоко » → « нет молока ».","Le plus souvent : masculin et neutre → -а, féminin -а → -ы. Tu as déjà vu « у меня нет шапки » !"]},
   {"by":"oleg","fr":["Compare les trois : « вода есть » (il y a de l'eau, forme de base), « воды нет » (il n'y a pas d'eau, orange), « купи воду » (achète de l'eau, bleu).","Le même mot, trois formes : c'est tout le puzzle du russe !"]}],
 explore={"type":"case","speaker":"luka","case":"gent","frame":"У нас нет ___.","frameFr":"On n'a pas de ___.","color":"#e76f51","hintFr":"Mets chaque mot après « нет » et regarde bien la fin du mot.","words":[
   {"tile":"хлеб","fr":"pain","phraseFr":"On n'a pas de pain."},{"tile":"вода","fr":"eau","phraseFr":"On n'a pas d'eau."},
   {"tile":"молоко","fr":"lait","phraseFr":"On n'a pas de lait."},{"tile":"сок","fr":"jus","phraseFr":"On n'a pas de jus."}]},
 tasks=[{"type":"pick","fr":"Dis qu'on n'a pas de lait.","answer":"молоко"},{"type":"pick","fr":"Dis qu'on n'a pas d'eau.","answer":"вода"}],
 cando=["dire qu'il manque quelque chose","demander s'il y a…","demander à quelqu'un d'acheter"],
 unlocks=[],
 glossary=G({"ой":"oh","нас":"nous (у нас = chez nous)","хлеба":"pain (après нет)","хлеб":"pain","сока":"jus (après нет)","сок":"jus","вода":"eau","воды":"eau (après нет)","воду":"eau (après купи)","магазин":"magasin","магазине":"magasin (après в)","рядом":"tout près","две":"deux","минуты":"minutes (après 2, 3, 4)","пойду":"(j')y vais","купи":"achète !","что-нибудь":"quelque chose","ещё":"encore","молоко":"lait","молока":"lait (après нет)"}),
 combos=[C("У меня нет шапки, но есть шарф.","Je n'ai pas de bonnet, mais j'ai une écharpe.",["шапку"]),
   C("У нас нет молока. Купи молоко!","On n'a pas de lait. Achète du lait !",["хлеба"]),
   C("Где здесь магазин? Рядом?","Où est le magasin, par ici ? Tout près ?",["купи"])])

# ---------------- 28. Avec quoi ? Avec qui ? ----------------
lesson(id="28-avec", order=28, titleFr="Avec du lait ?", titleRu="С молоком?", emoji="☕",
 sceneFr="Le lendemain de la fête, Luka passe au café. Anna lui sert un café… et lui pose des questions sur Macha.",
 dialogue=[D("anna","Привет, Л+ука! Тебе кофе?","Salut, Luka ! Un café pour toi ?"),
   D("luka","Да, кофе с молоком, пожалуйста.","Oui, un café au lait, s'il te plaît."),
   D("anna","С сахаром?","Avec du sucre ?"),
   D("luka","Нет, без сахара.","Non, sans sucre."),
   D("anna","А что ты будешь делать вечером?","Et qu'est-ce que tu vas faire ce soir ?"),
   D("luka","Я пойду в кино с М+ашей.","Je vais aller au cinéma avec Macha."),
   D("anna","С Машей? Как интересно!","Avec Macha ? C'est intéressant !"),
   D("luka","Мы просто друзья!","On est juste amis !")],
 phrases=[
   ph("coffee","anna","Тебе кофе?","Un café pour toi ?","Mot à mot : « à toi un café ? ». Très courant pour proposer.","кофе",["молоком","без"]),
   ph("milk","luka","Да, кофе с молоком, пожалуйста.","Oui, un café au lait, s'il te plaît.","« С » = avec. Après « с », le mot change : « молоко » → « с молоком ».","молоком",["молоко","молока"],["да кофе с молоком пожалуйста"],"Après « с » (avec), « молоко » → « с молоком » (-ом)."),
   ph("sugar","anna","С сахаром?","Avec du sucre ?","« Сахар » = sucre → « с сахаром ».","сахаром",["сахар","сахара"],None,"Après « с » (avec) : « сахар » → « сахаром » (-ом)."),
   ph("without","luka","Нет, без сахара.","Non, sans sucre.","« Без » = sans. Après « без », c'est l'orange, comme après « нет » : « без сахара ».","сахара",["сахаром","сахар"],None,"Après « без » (sans), comme après « нет » : « сахара » (-а)."),
   ph("evening","anna","А что ты будешь делать вечером?","Et qu'est-ce que tu vas faire ce soir ?","Tu connais : « будешь делать » = tu vas faire.","будешь",["буду","вечером"]),
   ph("withmasha","luka","Я пойду в кино с М+ашей.","Je vais aller au cinéma avec Macha.","« Пойду » = j'irai. « С Машей » : « Маша » → « Машей ».","кино",["кинотеатре","молоком"],["я пойду в кино с машей","я пойду с машей в кино","с машей я пойду в кино"]),
   ph("interesting","anna","С Машей? Как интересно!","Avec Macha ? C'est intéressant !","Anna est curieuse…","интересно",["сахара","кофе"]),
   ph("friends","luka","Мы просто друзья!","On est juste amis !","« Друзья » = amis (pluriel de « друг »). « Просто » = juste, simplement.","друзья",["друг","кино"],None,"Au pluriel : « друзья » (des amis). « Друг », c'est un seul ami.")],
 parts=[{"titleFr":"Le café","steps":[SC,B(["coffee","milk"]),EX,I(0),B(["sugar","without"],["milk"])]},
   {"titleFr":"Avec qui ?","steps":[W(["coffee","milk","sugar"]),B(["evening","withmasha"],["without"]),B(["interesting","friends"],["withmasha"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anna","fr":["Nouvelle couleur : le violet foncé ! Après « с » (avec), le mot prend -ом ou -ой / -ей : « с молоком », « с сахаром », « с Машей ».","Masculin et neutre : -ом. Féminin : -ой (ou -ей)."]},
   {"by":"anna","fr":["Et le contraire, « без » (sans), prend l'orange, comme « нет » : « без сахара », « без молока ».","« С » (avec) = violet, « без » (sans) = orange. Avec ou sans, tu sais tout dire !"]}],
 explore={"type":"case","speaker":"luka","case":"ablt","frame":"Чай с ___, пожалуйста.","frameFr":"Un thé avec ___, s'il vous plaît.","color":"#6a4c93","hintFr":"Mets chaque mot après « с » (avec) et regarde bien la fin du mot.","words":[
   {"tile":"молоко","fr":"du lait","phraseFr":"Un thé au lait, s'il vous plaît."},{"tile":"сахар","fr":"du sucre","phraseFr":"Un thé avec du sucre, s'il vous plaît."},
   {"tile":"лимон","fr":"du citron","phraseFr":"Un thé au citron, s'il vous plaît."},{"tile":"мёд","formAcc":"мёдом","fr":"du miel","phraseFr":"Un thé au miel, s'il vous plaît."}]},
 tasks=[{"type":"pick","fr":"Commande un thé au citron.","answer":"лимон"},{"type":"pick","fr":"Commande un thé au miel.","answer":"мёд"}],
 cando=["commander avec / sans","dire avec qui tu sors","parler de tes amis"],
 unlocks=[],
 glossary=G({"кофе":"café","с":"avec","молоком":"lait (après с)","молоко":"lait","молока":"lait (après без, нет)","сахаром":"sucre (après с)","сахар":"sucre","сахара":"sucre (après без, нет)","без":"sans","будешь":"(tu) vas","буду":"(je) vais","делать":"faire","вечером":"le soir","пойду":"(j')irai","кино":"cinéma","кинотеатре":"cinéma (après в)","машей":"Macha (après с)","интересно":"intéressant","мы":"nous","просто":"juste, simplement","друзья":"amis","друг":"ami","чай":"thé","лимон":"citron","лимоном":"citron (après с)","мёд":"miel","мед":"miel","мёдом":"miel (après с)","медом":"miel (après с)"}),
 combos=[C("Чай с лимоном и без сахара, пожалуйста.","Un thé au citron et sans sucre, s'il vous plaît.",["сахаром"]),
   C("Мы с Машей просто друзья.","Macha et moi, on est juste amis.",["друг"],["мы с машей просто друзья"]),
   C("Я буду кофе без молока.","Je vais prendre un café sans lait.",["молоком"],["я буду кофе без молока"])])

# ---------------- 29. L'université ----------------
lesson(id="29-universite", order=29, titleFr="À l'université", titleRu="В университете", emoji="🎓",
 sceneFr="À l'université, une nouvelle étudiante, Nina, parle avec Luka à la pause. C'est la caissière de l'épicerie !",
 dialogue=[D("nina","Привет! Ты тоже здесь уч+ишься?","Salut ! Tu étudies ici aussi ?"),
   D("luka","Да, я учусь в университете. А ты?","Oui, j'étudie à l'université. Et toi ?"),
   D("nina","Я тоже! Я работаю в магазине и учусь.","Moi aussi ! Je travaille au magasin et j'étudie."),
   D("luka","Что ты изучаешь?","Qu'est-ce que tu étudies ?"),
   D("nina","Я изучаю французский язык!","J'étudie le français !"),
   D("luka","Правда? А я изучаю русский язык.","C'est vrai ? Et moi, j'étudie le russe."),
   D("nina","Кем ты хочешь быть?","Qu'est-ce que tu veux devenir ?"),
   D("luka","Я хочу быть переводчиком.","Je veux être traducteur.")],
 phrases=[
   ph("studyq","nina","Ты тоже здесь уч+ишься?","Tu étudies ici aussi ?","« Учиться » = étudier (faire ses études). « Ты учишься » = tu étudies.","учишься",["учусь","изучаю"],["ты тоже здесь учишься","ты тоже учишься здесь"],"Avec « ты » : « учишься ». « Учусь », c'est pour « я »."),
   ph("study","luka","Да, я учусь в университете.","Oui, j'étudie à l'université.","« Я учусь » = j'étudie. « В университете » : le vert du lieu.","учусь",["учишься","изучаю"],["да я учусь в университете","да в университете я учусь"],"Avec « я » : « учусь »."),
   ph("work","nina","Я работаю в магазине и учусь.","Je travaille au magasin et j'étudie.","« В магазине » = au magasin (le vert du lieu).","магазине",["магазин","язык"],["я работаю в магазине и учусь","я учусь и работаю в магазине"],"Pour dire où : « в магазине » (-е)."),
   ph("what","luka","Что ты изучаешь?","Qu'est-ce que tu étudies ?","« Изучать » = étudier une matière. « Ты изучаешь » = tu étudies.","изучаешь",["изучаю","учусь"],["что ты изучаешь"],"Avec « ты » : « изучаешь »."),
   ph("french","nina","Я изучаю французский язык!","J'étudie le français !","« Французский язык » = la langue française. « Язык » = langue.","французский",["французски","переводчиком"],["я изучаю французский язык"],"Pour nommer la langue : « французский язык ». « По-французски », c'est « en français »."),
   ph("russian","luka","Правда? А я изучаю русский язык.","C'est vrai ? Et moi, j'étudie le russe.","« Правда ? » = c'est vrai ?","правда",["кем","быть"]),
   ph("become","nina","Кем ты хочешь быть?","Qu'est-ce que tu veux devenir ?","Mot à mot : « qui (en violet) tu veux être ? ». Après « быть », le métier prend le violet.","кем",["кто","что"],None,"Avec « быть », c'est « кем » (violet). « Кто », c'est juste « qui »."),
   ph("translator","luka","Я хочу быть переводчиком.","Je veux être traducteur.","« Переводчик » = traducteur → « быть переводчиком » (-ом), le violet, comme après « с ».","переводчиком",["переводчик","языком"],["я хочу быть переводчиком"],"Après « быть » (être, devenir), le violet : « переводчиком » (-ом).")],
 parts=[{"titleFr":"Tu étudies ici ?","steps":[SC,EX,I(0),B(["studyq","study"]),B(["work","what"],["study"])]},
   {"titleFr":"Les projets d'avenir","steps":[W(["studyq","study","what"]),B(["french","russian"],["work","what"]),I(1),B(["become","translator"],["french"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"nina","fr":["Deux verbes pour « étudier » : « учиться » (faire des études, aller à l'université) et « изучать » + la matière (étudier le russe).","« Я учусь в университете » / « Я изучаю русский язык ». Attention : учусь, учишься, учится… ont un petit « -ся » à la fin."]},
   {"by":"nina","fr":["Pour un métier qu'on veut faire : « быть » + le violet : « быть переводчиком », « быть врачом », « быть учителем ».","Mais au présent, toujours sans verbe : « я врач »."]}],
 explore={"type":"person","speaker":"luka","verb":"учиться","frame":"___ {V} в университете.","frameFr":"___ étudier à l'université.","color":"#8e44ad","hintFr":"Change la personne et écoute la fin du verbe (avec -ся).","words":[
   {"tile":"я","formAcc":"уч+усь","fr":"je","phraseFr":"J'étudie à l'université."},{"tile":"ты","formAcc":"уч+ишься","fr":"tu","phraseFr":"Tu étudies à l'université."},
   {"tile":"она","formAcc":"уч+ится","fr":"elle","phraseFr":"Elle étudie à l'université."},{"tile":"мы","formAcc":"уч+имся","fr":"nous","phraseFr":"Nous étudions à l'université."},
   {"tile":"вы","formAcc":"уч+итесь","fr":"vous","phraseFr":"Vous étudiez à l'université."},{"tile":"они","formAcc":"уч+атся","fr":"ils, elles","phraseFr":"Ils étudient à l'université."}]},
 tasks=[{"type":"pick","fr":"Dis : « Elle étudie à l'université. »","answer":"она"},{"type":"pick","fr":"Dis : « Nous étudions à l'université. »","answer":"мы"}],
 cando=["parler de tes études","dire quelle langue tu étudies","dire ce que tu veux devenir"],
 unlocks=[],
 glossary=G({"тоже":"aussi","здесь":"ici","учишься":"(tu) étudies","учусь":"(j')étudie","учится":"(il, elle) étudie","учимся":"(nous) étudions","учитесь":"(vous) étudiez","учатся":"(ils) étudient","университете":"université (après в)","работаю":"(je) travaille","магазине":"magasin (après в)","магазин":"magasin","изучаешь":"(tu) étudies","изучаю":"(j')étudie","французский":"français (adj.)","французски":"(forme incomplète)","язык":"langue","языком":"langue (après с, быть)","правда":"vrai, vérité","русский":"russe","кем":"qui (après быть)","кто":"qui","хочешь":"(tu) veux","хочу":"(je) veux","быть":"être","переводчиком":"traducteur (après быть)","переводчик":"traducteur","она":"elle","мы":"nous","они":"ils, elles","нина":"Nina (prénom)"}),
 combos=[C("Я не хочу быть переводчиком.","Je ne veux pas être traducteur.",["кем"]),
   C("Моя сестра уч+ится в Париже.","Ma sœur étudie à Paris.",["учусь"],["моя сестра учится в париже","в париже учится моя сестра"]),
   C("Я изучаю русский язык, а ты?","J'étudie le russe, et toi ?",["изучаешь"])])

# ---------------- 30. Julie arrive ----------------
lesson(id="30-julie", order=30, titleFr="Julie arrive !", titleRu="Жюли приехала!", emoji="🌷",
 sceneFr="Au printemps, Julie, la sœur de Luka, vient le voir à Saint-Pétersbourg. Elle ne parle pas russe : Luka traduit !",
 dialogue=[D("luka","М+аша, познакомься: это моя сестра Ж+юли.","Macha, je te présente ma sœur Julie."),
   D("masha","Очень приятно! Добро пожаловать в Петербург!","Enchantée ! Bienvenue à Saint-Pétersbourg !"),
   D("luka","Она не говорит по-р+усски. Я переведу.","Elle ne parle pas russe. Je vais traduire."),
   D("masha","Л+ука, ты так хорошо говоришь по-р+усски!","Luka, tu parles si bien russe !"),
   D("luka","Спасибо! Я много учился.","Merci ! J'ai beaucoup étudié."),
   D("masha","Что вы хотите посмотреть в Петербурге?","Qu'est-ce que vous voulez voir à Saint-Pétersbourg ?"),
   D("luka","Эрмитаж, Неву и, конечно, наше кафе!","L'Ermitage, la Neva et, bien sûr, notre café !"),
   D("masha","Отлично! Пойдём вместе!","Parfait ! Allons-y ensemble !")],
 phrases=[
   ph("meet","luka","М+аша, познакомься: это моя сестра Ж+юли.","Macha, je te présente ma sœur Julie.","« Познакомься » = fais connaissance (à « ты »). La façon normale de présenter quelqu'un.","сестра",["сестры","брат"],None,"On présente : forme de base « сестра ». « Сестры », c'est après « нет »."),
   ph("welcome","masha","Добро пожаловать в Петербург!","Bienvenue à Saint-Pétersbourg !","Tu l'as entendu à Moscou ! « В Петербург » : on y arrive (sans -е).","петербург",["петербурге","москве"],None,"On y arrive : « в Петербург » (forme de base pour un masculin). « В Петербурге », c'est quand on y est."),
   ph("translate","luka","Она не говорит по-р+усски. Я переведу.","Elle ne parle pas russe. Je vais traduire.","« Она говорит » = elle parle. « Я переведу » = je traduirai.","говорит",["говорю","говоришь"],None,"Avec « она » : « говорит » (-ит)."),
   ph("sowell","masha","Л+ука, ты так хорошо говоришь по-р+усски!","Luka, tu parles si bien russe !","« Так » = si, tellement.","говоришь",["говорит","говорю"],["лука ты так хорошо говоришь по-русски"],"Avec « ты » : « говоришь » (-ишь)."),
   ph("studied","luka","Спасибо! Я много учился.","Merci ! J'ai beaucoup étudié.","« Много » = beaucoup. « Я учился » = j'ai étudié (homme). Une femme dirait « училась ».","много",["неву","вместе"]),
   ph("see","masha","Что вы хотите посмотреть в Петербурге?","Qu'est-ce que vous voulez voir à Saint-Pétersbourg ?","On y est : « в Петербурге » (-е).","петербурге",["петербург","эрмитаж"],["что вы хотите посмотреть в петербурге","что вы хотите в петербурге посмотреть"],"On y est : « в Петербурге » (-е), le vert du lieu."),
   ph("hermitage","luka","Эрмитаж, Неву и, конечно, наше кафе!","L'Ermitage, la Neva et, bien sûr, notre café !","« Эрмитаж » = le musée de l'Ermitage. « Нева » = le fleuve → « Неву » (on veut la voir : bleu). « Наше » = notre.","неву",["нева","неве"],None,"On veut voir la Neva : le bleu, « Неву » (-у)."),
   ph("together","masha","Отлично! Пойдём вместе!","Parfait ! Allons-y ensemble !","« Вместе » = ensemble.","вместе",["много","неву"])],
 parts=[{"titleFr":"Les présentations","steps":[SC,B(["meet","welcome"]),B(["translate","sowell"],["welcome"]),I(0)]},
   {"titleFr":"Visiter la ville","steps":[W(["meet","welcome","translate"]),B(["studied","see"],["sowell"]),EX,B(["hermitage","together"],["see"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Tu as remarqué ? Maintenant c'est toi qui traduis pour Julie ! Tu sais te présenter, présenter quelqu'un, parler de ta vie, de tes goûts, de ton passé et de tes projets.","« Она говорит » (elle parle), « ты говоришь » (tu parles), « я говорю » (je parle) : tu maîtrises les verbes au présent."]},
   {"by":"masha","fr":["Récapitulons les couleurs : forme de base (qui ? quoi ?), bleu (ce qu'on veut, où l'on va), vert (où l'on est), orange (après « нет », « без »), violet (après « с », « быть »).","Avec ces cinq couleurs et les mots que tu connais, tu peux construire des centaines de phrases : c'est ton puzzle russe. Браво, Лука — et bravo à toi !"]}],
 explore={"type":"case","speaker":"luka","case":"loct","frame":"Вчера мы были в ___.","frameFr":"Hier, nous étions ___.","color":"#2a9d8f","hintFr":"Mets chaque lieu après « в » (on y était) et regarde bien la fin du mot.","words":[
   {"tile":"музей","fr":"au musée","phraseFr":"Hier, nous étions au musée."},{"tile":"театр","fr":"au théâtre","phraseFr":"Hier, nous étions au théâtre."},
   {"tile":"парк","fr":"au parc","phraseFr":"Hier, nous étions au parc."},{"tile":"кафе","fr":"au café","phraseFr":"Hier, nous étions au café."}]},
 tasks=[{"type":"pick","fr":"Dis : « Hier, nous étions au musée. »","answer":"музей"},{"type":"pick","fr":"Dis : « Hier, nous étions au café. »","answer":"кафе"}],
 cando=["présenter quelqu'un de ta famille","servir d'interprète","proposer une visite"],
 unlocks=[{"case":"loct","gender":"masc","from":"музей","to":"музее"}],
 glossary=G({"познакомься":"fais connaissance","сестра":"sœur","сестры":"sœur (après нет)","брат":"frère","жюли":"Julie (prénom)","приятно":"agréable","добро":"bien (добро пожаловать = bienvenue)","пожаловать":"(добро пожаловать = bienvenue)","петербург":"Saint-Pétersbourg","петербурге":"Saint-Pétersbourg (on y est)","москве":"Moscou (après в)","она":"elle","говорит":"(il, elle) parle","говорю":"(je) parle","говоришь":"(tu) parles","по-русски":"en russe","переведу":"(je) traduirai","так":"si, tellement","много":"beaucoup","учился":"(j')ai étudié","вы":"vous","хотите":"(vous) voulez","посмотреть":"voir","эрмитаж":"l'Ermitage","неву":"la Neva (on la voit)","нева":"la Neva","неве":"la Neva (après на)","конечно":"bien sûr","наше":"notre","кафе":"café","отлично":"parfait","пойдём":"allons","пойдем":"allons","вместе":"ensemble","мы":"nous","были":"(nous) étions","музей":"musée","музее":"musée (après в)","театр":"théâtre","театре":"théâtre (après в)","парк":"parc","парке":"parc (après в)"}),
 combos=[C("Познакомься, это мой друг Ол+ег.","Je te présente mon ami Oleg.",["моя"]),
   C("Она хорошо говорит по-англ+ийски.","Elle parle bien anglais.",["говоришь"],["она хорошо говорит по-английски","она говорит по-английски хорошо"]),
   C("Завтра мы пойдём в Эрмитаж вместе.","Demain, nous irons ensemble à l'Ermitage.",["много"],["завтра мы пойдём в эрмитаж вместе","завтра мы вместе пойдём в эрмитаж","мы пойдём в эрмитаж вместе завтра"])])
print("ok")
