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
    (OUT/f"{kw['id']}.json").write_text(json.dumps(kw,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
COMMON={"я":"je, moi","ты":"tu","вы":"vous","да":"oui","нет":"non","а":"et, mais","и":"et","это":"c'est, voici","не":"ne… pas","в":"dans, à","на":"sur, en","что":"quoi, que","как":"comment, comme","где":"où","очень":"très","спасибо":"merci","пожалуйста":"s'il te plaît / je t'en prie","хорошо":"bien, d'accord","привет":"salut","лука":"Luka (prénom)","маша":"Macha (prénom)","олег":"Oleg (prénom)","анна":"Anna (prénom)","у":"chez","меня":"moi (у меня = j'ai)","тебя":"toi (у тебя = tu as)","есть":"il y a","мой":"mon","моя":"ma","мне":"à moi","тоже":"aussi","сегодня":"aujourd'hui","завтра":"demain","вчера":"hier","потом":"puis, ensuite","давай":"allons-y, faisons"}
def G(d): return {**COMMON, **d}

# ---------------- 8. Ma famille ----------------
lesson(id="08-famille", order=8, titleFr="Ma famille", titleRu="Моя семья", emoji="👨‍👩‍👧",
 sceneFr="Au dîner, Macha demande à Luka s'il a de la famille en France. Luka sort son téléphone pour montrer des photos.",
 dialogue=[D("masha","Л+ука, у тебя есть брат или сестра?","Luka, tu as un frère ou une sœur ?"),
   D("luka","Да, у меня есть сестра.","Oui, j'ai une sœur."),
   D("luka","Вот фото. Это моя сестра. Её зовут Ж+юли.","Voici une photo. C'est ma sœur. Elle s'appelle Julie."),
   D("masha","Какая красивая! А это кто?","Qu'elle est belle ! Et ça, c'est qui ?"),
   D("luka","Это мой папа, а это моя мама.","C'est mon père, et ça, c'est ma mère."),
   D("masha","А у меня есть брат. Он живёт в Москве.","Et moi, j'ai un frère. Il habite à Moscou."),
   D("luka","Как его зовут?","Comment il s'appelle ?"),
   D("masha","Его зовут Ант+он.","Il s'appelle Anton.")],
 phrases=[
   ph("haveq","masha","У тебя есть брат или сестра?","Tu as un frère ou une sœur ?","« У тебя есть…? » = « tu as… ? » (mot à mot : « chez toi, il y a… ? »). « Или » = ou.","или",["тоже","вот"],["у тебя есть брат или сестра","у тебя есть сестра или брат"]),
   ph("havesis","luka","Да, у меня есть сестра.","Oui, j'ai une sœur.","« У меня есть » = « j'ai ». Pas de verbe « avoir » : on dit « chez moi, il y a ».","меня",["тебя","мой"],["да у меня есть сестра"],"« У меня » = chez moi → j'ai. « У тебя », c'est « tu as »."),
   ph("mysis","luka","Это моя сестра.","C'est ma sœur.","« Сестра » est féminin (-а), donc « моя ».","моя",["мой","кто"],None,"« Сестра » finit par -а : c'est féminin, donc « моя » (ma)."),
   ph("hername","luka","Её зовут Ж+юли.","Elle s'appelle Julie.","Comme « меня зовут », avec « её » (elle) : « on l'appelle Julie ».","её",["его","вот"],None,"Pour une femme : « её зовут ». « Его », c'est pour un homme."),
   ph("who","masha","А это кто?","Et ça, c'est qui ?","« Кто » = qui.","кто",["моя","или"]),
   ph("parents","luka","Это мой папа, а это моя мама.","C'est mon père, et ça, c'est ma mère.","« Папа » finit par -а mais c'est un homme : on dit « мой папа ». Le sens l'emporte !","мой",["моя","кто"],None,"« Папа » est un homme, donc « мой », même avec -а à la fin."),
   ph("brother","masha","А у меня есть брат. Он живёт в Москве.","Et moi, j'ai un frère. Il habite à Moscou.","« Он » = il. « В Москве » : tu connais ce vert (le lieu).","москве",["москва","брат"],None,"Après « в » pour dire où l'on est : « Москва » → « в Москве »."),
   ph("hisname","luka","Как его зовут?","Comment il s'appelle ?","Pour un homme : « его зовут ». Attention, « его » se prononce « ïévo ».","его",["её","кто"],["как его зовут","как зовут его"],"Pour un homme : « его зовут ». « Её », c'est pour une femme.")],
 parts=[{"titleFr":"Frères et sœurs","steps":[SC,EX,I(0),B(["haveq","havesis"]),I(1),B(["mysis","hername"],["havesis"])]},
   {"titleFr":"Les parents","steps":[W(["haveq","havesis","mysis"]),B(["who","parents"],["mysis","hername"]),B(["brother","hisname"],["parents","hername"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Pour dire « j'ai », le russe dit « chez moi, il y a » : « у меня есть ».","« У меня есть брат » = j'ai un frère. « У тебя есть… ? » = tu as… ?"]},
   {"by":"masha","fr":["« Мой » (mon) et « моя » (ma) suivent le genre, comme en français : « мой брат », « моя сестра ».","Et pour le prénom de quelqu'un d'autre : « его зовут » (il s'appelle), « её зовут » (elle s'appelle)."]}],
 explore={"type":"plain","speaker":"luka","frame":"У меня есть ___.","frameFr":"J'ai ___.","color":"#5c677d","hintFr":"Mets chaque mot dans la phrase et écoute.","words":[
   {"tile":"брат","fr":"un frère","phraseFr":"J'ai un frère."},{"tile":"сестра","fr":"une sœur","phraseFr":"J'ai une sœur."},
   {"tile":"собака","fr":"un chien","phraseFr":"J'ai un chien."},{"tile":"кошка","fr":"un chat","phraseFr":"J'ai un chat."}]},
 tasks=[{"type":"pick","fr":"Dis : « J'ai un chien. »","answer":"собака"},{"type":"pick","fr":"Dis : « J'ai une sœur. »","answer":"сестра"}],
 cando=["parler de ta famille","dire « j'ai »","dire comment s'appelle quelqu'un"],
 unlocks=[{"case":"loct","gender":"femn","from":"Москва","to":"Москве"}],
 glossary=G({"брат":"frère","или":"ou","сестра":"sœur","вот":"voici, voilà","фото":"photo","её":"elle, la (её зовут = elle s'appelle)","зовут":"(on) appelle","жюли":"Julie","какая":"quelle, comme","красивая":"belle","кто":"qui","папа":"papa, père","мама":"maman, mère","он":"il","живёт":"(il) habite","живет":"(il) habite","москве":"Moscou (après в)","москва":"Moscou","его":"lui, le (его зовут = il s'appelle)","антон":"Anton","собака":"chien","кошка":"chat"}))

# ---------------- 9. Ma journée ----------------
lesson(id="09-journee", order=9, titleFr="Ma journée", titleRu="Мой день", emoji="⏰",
 sceneFr="Quelques jours plus tard, Oleg croise Luka dans la rue et lui demande comment se passent ses journées.",
 dialogue=[D("oleg","Привет, Л+ука! Что ты делаешь днём?","Salut, Luka ! Qu'est-ce que tu fais dans la journée ?"),
   D("luka","Утром я учу русский.","Le matin, j'apprends le russe."),
   D("luka","Днём я работаю.","L'après-midi, je travaille."),
   D("oleg","А где ты работаешь?","Et où est-ce que tu travailles ?"),
   D("luka","Я работаю в кафе. А ты?","Je travaille dans un café. Et toi ?"),
   D("oleg","Я работаю в банке.","Je travaille dans une banque."),
   D("luka","А что ты делаешь вечером?","Et qu'est-ce que tu fais le soir ?"),
   D("oleg","Вечером я отдыхаю: читаю или смотрю фильмы.","Le soir, je me repose : je lis ou je regarde des films.")],
 phrases=[
   ph("whatdo","oleg","Что ты делаешь днём?","Qu'est-ce que tu fais dans la journée ?","« Делаешь » = (tu) fais. « Днём » = dans la journée, l'après-midi.","делаешь",["делаю","утром"],["что ты делаешь днём","что ты днём делаешь"],"Avec « ты », le verbe finit en -ешь : « ты делаешь ». « Делаю », c'est pour « я »."),
   ph("morning","luka","Утром я учу русский.","Le matin, j'apprends le russe.","« Утром » = le matin. « Учу » = (j')apprends.","утром",["кафе","банке"],["утром я учу русский","я учу русский утром"]),
   ph("work","luka","Днём я работаю.","L'après-midi, je travaille.","« Работаю » = (je) travaille. Encore la fin -ю pour « я » !","работаю",["работаешь","кафе"],["днём я работаю","я работаю днём"],"Avec « я », le verbe finit en -ю : « я работаю »."),
   ph("wherework","oleg","А где ты работаешь?","Et où est-ce que tu travailles ?","« Где » = où. « Ты работаешь » = tu travailles.","работаешь",["работаю","вечером"],["а где ты работаешь"],"Avec « ты » : « работаешь » (-ешь)."),
   ph("cafe","luka","Я работаю в кафе. А ты?","Je travaille dans un café. Et toi ?","« Кафе » ne change jamais. « А ты ? » = et toi ?","кафе",["кафею","утром"]),
   ph("bank","oleg","Я работаю в банке.","Je travaille dans une banque.","« Банк » → « в банке » : le vert du lieu, comme « в парке ».","банке",["банк","вечером"],["я работаю в банке","в банке я работаю"],"Pour dire où : « в » + -е. « Банк » → « в банке »."),
   ph("evening","luka","А что ты делаешь вечером?","Et qu'est-ce que tu fais le soir ?","« Вечером » = le soir. Matin, journée, soir : утром, днём, вечером.","вечером",["банке","работаю"],["а что ты делаешь вечером","а что ты вечером делаешь"]),
   ph("rest","oleg","Вечером я отдыхаю: читаю или смотрю фильмы.","Le soir, je me repose : je lis ou je regarde des films.","« Отдыхаю » = je me repose, « читаю » = je lis, « смотрю » = je regarde.","отдыхаю",["отдыхаешь","банке"],None,"Avec « я » : « отдыхаю » (-ю).")],
 parts=[{"titleFr":"Le matin et la journée","steps":[SC,B(["whatdo","morning"]),EX,I(0),B(["work","wherework"],["whatdo","morning"])]},
   {"titleFr":"Le travail et le soir","steps":[W(["whatdo","work","wherework"]),B(["cafe","bank"],["wherework"]),B(["evening","rest"],["cafe","bank"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"oleg","fr":["Beaucoup de verbes russes marchent comme « работать » (travailler) : on enlève -ть et on ajoute la fin de la personne.","Я работа-ю, ты работа-ешь, он работа-ет, мы работа-ем, вы работа-ете, они работа-ют. Retiens surtout -ю (je) et -ешь (tu) : ce sont les plus utiles pour parler."]},
   {"by":"oleg","fr":["Pour dire quand : « утром » (le matin), « днём » (dans la journée), « вечером » (le soir).","Pas besoin de préposition : le mot seul suffit. « Вечером я отдыхаю » = le soir, je me repose."]}],
 explore={"type":"person","speaker":"luka","verb":"работать","frame":"___ {V} в кафе.","frameFr":"___ travailler dans un café.","color":"#8e44ad","hintFr":"Change la personne et écoute la fin du verbe.","words":[
   {"tile":"я","fr":"je","phraseFr":"Je travaille dans un café."},{"tile":"ты","fr":"tu","phraseFr":"Tu travailles dans un café."},
   {"tile":"он","fr":"il","phraseFr":"Il travaille dans un café."},{"tile":"мы","fr":"nous","phraseFr":"Nous travaillons dans un café."},
   {"tile":"вы","fr":"vous","phraseFr":"Vous travaillez dans un café."},{"tile":"они","fr":"ils, elles","phraseFr":"Ils travaillent dans un café."}]},
 tasks=[{"type":"pick","fr":"Dis : « Tu travailles dans un café. »","answer":"ты"},{"type":"pick","fr":"Dis : « Ils travaillent dans un café. »","answer":"они"}],
 cando=["raconter ta journée","dire où tu travailles","dire ce que tu fais le soir"],
 unlocks=[{"case":"loct","gender":"masc","from":"банк","to":"банке"}],
 glossary=G({"делаешь":"(tu) fais","делаю":"(je) fais","днём":"dans la journée","днем":"dans la journée","утром":"le matin","учу":"(j')apprends","русский":"le russe","работаю":"(je) travaille","работаешь":"(tu) travailles","работает":"(il) travaille","работаем":"(nous) travaillons","работаете":"(vous) travaillez","работают":"(ils) travaillent","кафе":"café","банке":"banque (après в)","банк":"banque","вечером":"le soir","отдыхаю":"(je) me repose","отдыхаешь":"(tu) te reposes","читаю":"(je) lis","или":"ou","смотрю":"(je) regarde","фильмы":"films","он":"il","мы":"nous","они":"ils, elles","кафею":"(forme inexistante)"}))

# ---------------- 10. Au restaurant ----------------
lesson(id="10-restaurant", order=10, titleFr="Au restaurant", titleRu="В ресторане", emoji="🍲",
 sceneFr="Vendredi soir, Luka et Macha dînent au restaurant. La serveuse, c'est Anna, du café ! Elle y travaille le soir.",
 dialogue=[D("anna","Добрый вечер! Вот меню.","Bonsoir ! Voici le menu."),
   D("luka","Анна? Добрый вечер!","Anna ? Bonsoir !"),
   D("anna","Что вы будете?","Qu'est-ce que vous prenez ?"),
   D("masha","Я буду суп и рыбу.","Je vais prendre une soupe et du poisson."),
   D("luka","А я буду салат и курицу.","Et moi, je vais prendre une salade et du poulet."),
   D("anna","Что вы будете пить?","Qu'est-ce que vous allez boire ?"),
   D("luka","Воду, пожалуйста.","De l'eau, s'il vous plaît."),
   D("masha","Было очень вкусно! Счёт, пожалуйста.","C'était très bon ! L'addition, s'il vous plaît.")],
 phrases=[
   ph("evening","anna","Добрый вечер! Вот меню.","Bonsoir ! Voici le menu.","« Добрый вечер » = bonsoir (mot à mot : bonne soirée). « Меню » ne change jamais.","вечер",["меню","суп"]),
   ph("order","anna","Что вы будете?","Qu'est-ce que vous prenez ?","Au restaurant, « Что вы будете ? » = qu'est-ce que vous prenez ? (mot à mot : « que serez-vous ? »).","будете",["буду","суп"],["что вы будете"],"Avec « вы » : « будете ». « Буду », c'est pour « я »."),
   ph("soup","masha","Я буду суп и рыбу.","Je vais prendre une soupe et du poisson.","« Я буду… » = je vais prendre. Après « буду », c'est comme après « хочу » : « рыба » → « рыбу ».","рыбу",["рыба","меню"],["я буду суп и рыбу","я буду рыбу и суп"],"Après « я буду » (je prends), « рыба » → « рыбу », comme après « хочу »."),
   ph("chicken","luka","А я буду салат и курицу.","Et moi, je vais prendre une salade et du poulet.","« Курица » = poulet → « курицу ». « Салат » (masculin) ne change pas.","курицу",["курица","счёт"],["а я буду салат и курицу","а я буду курицу и салат"],"Après « буду », « курица » → « курицу » : le -а devient -у."),
   ph("drink","anna","Что вы будете пить?","Qu'est-ce que vous allez boire ?","« Пить » = boire.","пить",["суп","меню"],["что вы будете пить"]),
   ph("water","luka","Воду, пожалуйста.","De l'eau, s'il vous plaît.","Le verbe est sous-entendu (« je prends »), donc on garde « воду ».","воду",["вода","счёт"],None,"La phrase complète, c'est « я буду воду » : donc « воду », avec -у."),
   ph("tasty","masha","Было очень вкусно!","C'était très bon !","« Вкусно » = bon (pour la nourriture). « Было » = c'était.","вкусно",["меню","суп"]),
   ph("bill","masha","Счёт, пожалуйста.","L'addition, s'il vous plaît.","« Счёт » = l'addition. Très utile !","счёт",["суп","вечер"])],
 parts=[{"titleFr":"Commander","steps":[SC,B(["evening","order"]),EX,I(0),B(["soup","chicken"],["order"])]},
   {"titleFr":"Boire et payer","steps":[W(["order","soup","chicken"]),B(["drink","water"],["soup","chicken"]),B(["tasty","bill"],["drink","water"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anna","fr":["Au restaurant, pour commander, on dit « я буду… » (je vais prendre).","Après « буду », c'est le même bleu qu'après « хочу » : « рыба » → « рыбу », « курица » → « курицу ». « Суп » et « салат » (masculins) ne bougent pas."]},
   {"by":"anna","fr":["Les mots magiques du restaurant : « меню » (le menu), « счёт » (l'addition), « вкусно » (c'est bon).","« Добрый вечер » = bonsoir. Le matin, on dit « доброе утро », la journée « добрый день »."]}],
 explore={"type":"case","speaker":"luka","case":"accs","frame":"Я буду ___.","frameFr":"Je vais prendre ___.","color":"#3a86ff","hintFr":"Mets chaque plat après « я буду » et regarde bien la fin du mot.","words":[
   {"tile":"суп","fr":"une soupe","phraseFr":"Je vais prendre une soupe."},{"tile":"рыба","fr":"le poisson","phraseFr":"Je vais prendre du poisson."},
   {"tile":"салат","fr":"une salade","phraseFr":"Je vais prendre une salade."},{"tile":"курица","fr":"le poulet","phraseFr":"Je vais prendre du poulet."}]},
 tasks=[{"type":"pick","fr":"Commande du poulet.","answer":"курица"},{"type":"pick","fr":"Commande une soupe.","answer":"суп"}],
 cando=["commander au restaurant","dire que c'était bon","demander l'addition"],
 unlocks=[{"case":"accs","gender":"femn","from":"курица","to":"курицу"},{"case":"accs","gender":"masc","from":"суп","to":"суп"}],
 glossary=G({"добрый":"bon (добрый вечер = bonsoir)","вечер":"soir","вот":"voici, voilà","меню":"menu","будете":"(vous) serez / prendrez","буду":"(je) serai / prendrai","суп":"soupe","рыбу":"poisson (après буду)","рыба":"poisson","салат":"salade","курицу":"poulet (après буду)","курица":"poulet","пить":"boire","воду":"eau (après буду)","вода":"eau","было":"c'était","вкусно":"bon (au goût)","счёт":"addition","счет":"addition"}))

# ---------------- 11. En ville : le transport ----------------
lesson(id="11-transport", order=11, titleFr="Prendre le métro", titleRu="На метро", emoji="🚇",
 sceneFr="Lundi matin, Luka part à son cours de russe. Dans l'ascenseur, il retrouve Macha qui va à l'hôpital.",
 dialogue=[D("masha","Доброе утро, Л+ука! Куда ты идёшь?","Bonjour, Luka ! Où est-ce que tu vas ?"),
   D("luka","Доброе утро! Я иду на урок.","Bonjour ! Je vais à mon cours."),
   D("masha","Ты едешь на метро?","Tu y vas en métro ?"),
   D("luka","Нет, я еду на автобусе. А ты?","Non, j'y vais en bus. Et toi ?"),
   D("masha","Я еду в больницу. На метро.","Je vais à l'hôpital. En métro."),
   D("luka","Это далеко?","C'est loin ?"),
   D("masha","Нет, двадцать минут. Пока!","Non, vingt minutes. Salut !"),
   D("luka","Пока! Хорошего дня!","Salut ! Bonne journée !")],
 phrases=[
   ph("where","masha","Куда ты идёшь?","Où est-ce que tu vas ?","« Куда » = où (vers où on va). « Где » = où on est. « Идёшь » = (tu) vas, à pied.","куда",["где","пока"],["куда ты идёшь","ты куда идёшь"],"Pour une direction (aller vers) : « куда ». « Где », c'est pour l'endroit où l'on est."),
   ph("lesson","luka","Я иду на урок.","Je vais à mon cours.","« Иду » = (je) vais, à pied. « На урок » = au cours.","иду",["идёшь","пока"],["я иду на урок","на урок я иду"],"Avec « я » : « иду ». « Идёшь », c'est pour « ты »."),
   ph("metroq","masha","Ты едешь на метро?","Tu y vas en métro ?","« Ехать » = aller en véhicule : « ты едешь ». « На метро » = en métro.","едешь",["еду","куда"],["ты едешь на метро","на метро ты едешь"],"Avec « ты » : « едешь ». « Еду », c'est pour « я »."),
   ph("bus","luka","Нет, я еду на автобусе.","Non, j'y vais en bus.","« На автобусе » = en bus : « автобус » prend -е, comme pour un lieu.","автобусе",["автобус","метро"],["нет я еду на автобусе","нет на автобусе я еду"],"Avec « на » pour le moyen de transport : « автобус » → « на автобусе »."),
   ph("hospital","masha","Я еду в больницу.","Je vais à l'hôpital.","« Больница » = hôpital. Pour aller vers, « в » + -у : « в больницу ».","больницу",["больнице","автобусе"],["я еду в больницу","в больницу я еду"],"Pour aller VERS un lieu : « в больницу » (-у). « В больнице » (-е), c'est quand on y est déjà."),
   ph("far","luka","Это далеко?","C'est loin ?","Tu le connais déjà !","далеко",["пока","урок"]),
   ph("twenty","masha","Нет, двадцать минут. Пока!","Non, vingt minutes. Salut !","« Двадцать » = vingt. « Пока » = salut (pour partir), entre amis.","двадцать",["куда","урок"]),
   ph("niceday","luka","Пока! Хорошего дня!","Salut ! Bonne journée !","« Хорошего дня » = bonne journée.","дня",["урок","метро"])],
 parts=[{"titleFr":"Où vas-tu ?","steps":[SC,B(["where","lesson"]),I(0),B(["metroq","bus"],["where","lesson"])]},
   {"titleFr":"En métro, en bus","steps":[W(["where","lesson","metroq"]),EX,I(1),B(["hospital","far"],["metroq","bus"]),B(["twenty","niceday"],["hospital"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Le russe a deux verbes pour « aller » : « идти » à pied (я иду, ты идёшь) et « ехать » en véhicule (я еду, ты едешь).","Et deux « où » : « где » (où l'on est) et « куда » (où l'on va)."]},
   {"by":"masha","fr":["Pour le moyen de transport : « на » + le vert du lieu : « на автобусе », « на машине ». « Метро » et « такси » ne changent jamais.","Mais pour aller VERS un lieu, c'est le bleu : « я еду в больницу » (-у). Comparer : « я в больнице » = j'y suis."]}],
 explore={"type":"case","speaker":"luka","case":"loct","frame":"Я еду на ___.","frameFr":"J'y vais en ___.","color":"#2a9d8f","hintFr":"Mets chaque transport après « на » et regarde bien la fin du mot.","words":[
   {"tile":"метро","fr":"métro","phraseFr":"J'y vais en métro."},{"tile":"автобус","fr":"bus","phraseFr":"J'y vais en bus."},
   {"tile":"машина","fr":"voiture","phraseFr":"J'y vais en voiture."},{"tile":"такси","fr":"taxi","phraseFr":"J'y vais en taxi."}]},
 tasks=[{"type":"pick","fr":"Dis que tu y vas en voiture.","answer":"машина"},{"type":"pick","fr":"Dis que tu y vas en taxi.","answer":"такси"}],
 cando=["dire où tu vas","dire comment tu y vas","dire au revoir entre amis"],
 unlocks=[{"case":"loct","gender":"masc","from":"автобус","to":"автобусе"},{"case":"accs","gender":"femn","from":"больница","to":"больницу"}],
 glossary=G({"доброе":"bon (доброе утро = bonjour, le matin)","утро":"matin","куда":"où (vers où)","идёшь":"(tu) vas (à pied)","идешь":"(tu) vas (à pied)","иду":"(je) vais (à pied)","урок":"cours, leçon","едешь":"(tu) vas (en véhicule)","еду":"(je) vais (en véhicule)","метро":"métro","автобусе":"bus (après на)","автобус":"bus","больницу":"hôpital (vers)","больнице":"hôpital (dedans)","больница":"hôpital","далеко":"loin","двадцать":"vingt","минут":"minutes","пока":"salut (au revoir)","хорошего":"bon(ne)","дня":"journée (хорошего дня = bonne journée)","машина":"voiture","такси":"taxi"}))

# ---------------- 12. Le week-end (passé) ----------------
lesson(id="12-weekend", order=12, titleFr="Le week-end", titleRu="Выходные", emoji="🎬",
 sceneFr="Lundi soir, Luka passe au café. Anna lui demande comment s'est passé son week-end.",
 dialogue=[D("anna","Привет, Л+ука! Что ты делал в субботу?","Salut, Luka ! Qu'est-ce que tu as fait samedi ?"),
   D("luka","В субботу я был в музее.","Samedi, j'étais au musée."),
   D("anna","Один?","Tout seul ?"),
   D("luka","Нет, с Машей. А вечером мы смотрели фильм.","Non, avec Macha. Et le soir, on a regardé un film."),
   D("anna","А в воскресенье?","Et dimanche ?"),
   D("luka","В воскресенье я отдыхал дома. А ты?","Dimanche, je me suis reposé à la maison. Et toi ?"),
   D("anna","А я работала. Весь день!","Et moi, j'ai travaillé. Toute la journée !"),
   D("luka","Бедная Анна!","Pauvre Anna !")],
 phrases=[
   ph("whatdid","anna","Что ты делал в субботу?","Qu'est-ce que tu as fait samedi ?","Le passé : « делал » = (tu) as fait. « В субботу » = samedi.","делал",["делаешь","был"],["что ты делал в субботу","что ты в субботу делал"],"Ici on parle du passé (samedi dernier) : « делал ». « Делаешь », c'est le présent."),
   ph("museum","luka","В субботу я был в музее.","Samedi, j'étais au musée.","« Был » = j'étais (un homme). « В музее » : le vert du lieu.","был",["была","один"],["в субботу я был в музее","я был в музее в субботу"],"Luka est un homme : « я был ». Une femme dirait « я была »."),
   ph("alone","anna","Один?","Tout seul ?","« Один » = un, seul."),
   ph("withmasha","luka","Нет, с Машей.","Non, avec Macha.","« С » = avec. Après « с », le nom change : « Маша » → « с Машей ». Retiens-le tel quel pour l'instant.","с",["в","на"]),
   ph("film","luka","А вечером мы смотрели фильм.","Et le soir, on a regardé un film.","« Мы смотрели » = nous avons regardé. Au pluriel, le passé finit en -ли.","смотрели",["смотрел","дома"],["а вечером мы смотрели фильм","а мы вечером смотрели фильм"],"Avec « мы » (nous), le passé finit en -ли : « смотрели »."),
   ph("sunday","anna","А в воскресенье?","Et dimanche ?","« Воскресенье » = dimanche."),
   ph("rested","luka","В воскресенье я отдыхал дома.","Dimanche, je me suis reposé à la maison.","« Отдыхал » = je me suis reposé (homme). « Дома » = à la maison.","отдыхал",["отдыхала","музее"],["в воскресенье я отдыхал дома","я отдыхал дома в воскресенье"],"Luka est un homme : « отдыхал ». Une femme dirait « отдыхала »."),
   ph("worked","anna","А я работала. Весь день!","Et moi, j'ai travaillé. Toute la journée !","Anna est une femme : « работала » (avec -а). « Весь день » = toute la journée.","работала",["работал","дома"],None,"Anna est une femme, donc -ла : « я работала ». « Работал », c'est pour un homme.")],
 parts=[{"titleFr":"Samedi","steps":[SC,EX,I(0),B(["whatdid","museum"]),B(["alone","withmasha","film"],["museum"])]},
   {"titleFr":"Dimanche","steps":[W(["whatdid","museum","film"]),B(["sunday","rested"],["withmasha","film"]),B(["worked"],["rested","museum"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anna","fr":["Le passé russe est simple : on enlève -ть et on met -л. « Работать » → « работал ».","Mais il suit le genre ! Un homme dit « я работал », une femme « я работала ». Pour « nous » ou « vous » : « работали ».","Et « être » au passé : « был » (homme), « была » (femme), « были » (pluriel)."]},
   {"by":"anna","fr":["Les jours avec « в » : « в субботу » (samedi), « в воскресенье » (dimanche), « в понедельник » (lundi).","Tu remarques ? Il n'y a qu'un seul passé en russe pour « j'ai travaillé », « je travaillais »… Pratique !"]}],
 explore={"type":"plain","speaker":"luka","frame":"Вчера я ___.","frameFr":"Hier, je ___.","color":"#5c677d","hintFr":"Écoute la fin : -л pour un homme, -ла pour une femme.","words":[
   {"tile":"работал","fr":"ai travaillé (homme)","phraseFr":"Hier, j'ai travaillé. (un homme)"},{"tile":"работала","fr":"ai travaillé (femme)","phraseFr":"Hier, j'ai travaillé. (une femme)"},
   {"tile":"отдыхал","fr":"me suis reposé (homme)","phraseFr":"Hier, je me suis reposé."},{"tile":"отдыхала","fr":"me suis reposée (femme)","phraseFr":"Hier, je me suis reposée."}]},
 tasks=[{"type":"pick","fr":"Une femme dit : « Hier, j'ai travaillé. »","answer":"работала"},{"type":"pick","fr":"Un homme dit : « Hier, je me suis reposé. »","answer":"отдыхал"}],
 cando=["raconter ton week-end","parler au passé","dire avec qui tu étais"],
 unlocks=[{"case":"loct","gender":"neut","from":"музей","to":"музее"}],
 glossary=G({"делал":"(tu) as fait","делаешь":"(tu) fais","субботу":"samedi (в субботу)","был":"(j')étais (homme)","была":"(j')étais (femme)","музее":"musée (après в)","один":"seul, un","с":"avec","машей":"Macha (après с)","вечером":"le soir","мы":"nous","смотрели":"(nous) avons regardé","смотрел":"(il) a regardé","фильм":"film","воскресенье":"dimanche","отдыхал":"(je) me suis reposé","отдыхала":"(je) me suis reposée","дома":"à la maison","работала":"(j')ai travaillé (femme)","работал":"(j')ai travaillé (homme)","весь":"tout","день":"jour, journée","бедная":"pauvre","вчера":"hier"}))
print("ok")
