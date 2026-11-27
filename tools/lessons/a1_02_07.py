import json, pathlib
OUT=pathlib.Path(''+str(pathlib.Path(__file__).resolve().parents[2]/'content'/'levels')+'')
def ph(id, speaker, ru, fr, note, gap=None, dis=None, orders=None, why=None):
    d={"id":id,"speaker":speaker,"ru":ru,"fr":fr,"noteFr":note}
    if gap: d["gap"]={"word":gap,"distractors":dis}; 
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

# ---------------- 2. Se présenter ----------------
lesson(id="02-presenter", order=2, titleFr="Se présenter", titleRu="О себе", emoji="🙋",
 sceneFr="Suite de la rencontre dans l'escalier : Macha veut en savoir un peu plus sur son nouveau voisin.",
 dialogue=[D("masha","Вы студент?","Vous êtes étudiant ?"),
   D("luka","Да, я студент. А вы?","Oui, je suis étudiant. Et vous ?"),
   D("masha","Я врач.","Je suis médecin."),
   D("masha","Вы говорите по-р+усски?","Vous parlez russe ?"),
   D("luka","Немного. Я говорю по-франц+узски и по-англ+ийски.","Un peu. Je parle français et anglais."),
   D("masha","Вы хорошо говорите!","Vous parlez bien !"),
   D("luka","Спасибо!","Merci !"),
   D("masha","До свидания, Л+ука!","Au revoir, Luka !"),
   D("luka","До свидания!","Au revoir !")],
 phrases=[
   ph("student","luka","Да, я студент. А вы?","Oui, je suis étudiant. Et vous ?","Toujours pas de verbe « être » : « я студент » = « je suis étudiant ». « А вы ? » = « et vous ? », pour renvoyer la question.","студент",["спасибо","до"],["да я студент а вы"]),
   ph("doctor","masha","Я врач.","Je suis médecin.","« Врач » = médecin. Macha est une femme, mais on dit aussi « врач » : ce mot ne change pas.","врач",["спасибо","до"]),
   ph("speakru","masha","Вы говорите по-р+усски?","Vous parlez russe ?","« По-русски » = « en russe ». Mot à mot : « vous parlez en russe ? ».","говорите",["говорю","спасибо"],["вы говорите по-русски","по-русски вы говорите","вы по-русски говорите"],"Avec « вы », le verbe finit en -ите : « вы говорите ». « Говорю », c'est pour « я »."),
   ph("little","luka","Немного.","Un peu.","« Немного » = un peu. La réponse la plus utile quand on apprend le russe !"),
   ph("speakfr","luka","Я говорю по-франц+узски и по-англ+ийски.","Je parle français et anglais.","« И » = « et ». « По-французски » = en français, « по-английски » = en anglais.","говорю",["говорите","спасибо"],["я говорю по-французски и по-английски","я говорю по-английски и по-французски","по-французски и по-английски я говорю"],"Avec « я », le verbe finit en -ю : « я говорю ». « Говорите », c'est pour « вы »."),
   ph("well","masha","Вы хорошо говорите!","Vous parlez bien !","« Хорошо » = bien.","хорошо",["спасибо","студент"],["вы хорошо говорите","вы говорите хорошо"]),
   ph("thanks","luka","Спасибо!","Merci !","Le « merci » russe, pour toutes les situations."),
   ph("bye","masha","До свидания!","Au revoir !","Mot à mot : « jusqu'au revoir ». Le « о » de « до » se prononce presque « a » : « dasvidaniya ».","свидания",["спасибо","хорошо"])],
 parts=[{"titleFr":"Dire ce que tu fais","steps":[SC,B(["student","doctor"]),EX,I(0)]},
   {"titleFr":"Les langues que tu parles","steps":[W(["student","doctor"]),B(["speakru","little"],["student"]),I(1),B(["speakfr","well"],["speakru","little"]),B(["thanks","bye"],["speakfr","well"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Pour dire ton métier, c'est comme pour « я француз » : pas de verbe « être ». « Я врач » = « je suis médecin ».","Certains métiers changent pour une femme : « учитель » → « учительница », comme « студент » → « студентка ». D'autres restent pareils : une femme dit aussi « я врач », « я инженер »."]},
   {"by":"masha","fr":["Le verbe change selon la personne, comme en français : « я говорю » (je parle), « вы говорите » (vous parlez).","Écoute la fin du mot : -ю pour « я », -ите pour « вы ». C'est elle qui dit qui parle.","« По-русски », « по-французски » = « en russe », « en français »."]}],
 explore={"type":"plain","speaker":"luka","frame":"Я ___.","frameFr":"Je suis ___.","color":"#5c677d","hintFr":"Mets chaque métier dans la phrase et écoute.","words":[
   {"tile":"врач","fr":"médecin","phraseFr":"Je suis médecin."},
   {"tile":"инженер","fr":"ingénieur","phraseFr":"Je suis ingénieur."},
   {"tile":"учитель","fr":"professeur","phraseFr":"Je suis professeur."},
   {"tile":"учительница","fr":"professeure","phraseFr":"Je suis professeure."}]},
 tasks=[{"type":"pick","fr":"Dis : « Je suis professeure. »","answer":"учительница"},{"type":"pick","fr":"Dis : « Je suis ingénieur. »","answer":"инженер"}],
 cando=["dire ce que tu fais dans la vie","dire quelles langues tu parles","dire au revoir"],
 unlocks=[{"verb":"говорить","persons":["я","вы"]}],
 glossary={"вы":"vous","студент":"étudiant","да":"oui","я":"je, moi","а":"et, mais","врач":"médecin","говорите":"(vous) parlez","по-русски":"en russe","немного":"un peu","говорю":"(je) parle","по-французски":"en français","и":"et","по-английски":"en anglais","хорошо":"bien","спасибо":"merci","до":"jusqu'à","свидания":"revoir (до свидания = au revoir)","лука":"Luka (prénom)","инженер":"ingénieur","учитель":"professeur","учительница":"professeure"})

# ---------------- 3. Au café ----------------
lesson(id="03-cafe", order=3, titleFr="Au café", titleRu="В кафе", emoji="☕",
 sceneFr="Le lendemain matin, Luka entre dans le petit café au coin de sa rue. Derrière le comptoir, Anna lui sourit.",
 learner="luka",
 dialogue=[D("anna","Здравствуйте! Что вы хотите?","Bonjour ! Qu'est-ce que vous désirez ?"),
   D("luka","Здравствуйте! Я хочу кофе, пожалуйста.","Bonjour ! Je voudrais un café, s'il vous plaît."),
   D("anna","Вы француз?","Vous êtes français ?"),
   D("luka","Да, я из Франции.","Oui, je viens de France."),
   D("anna","Что-нибудь ещё?","Autre chose ?"),
   D("luka","Да, я хочу булочку.","Oui, je voudrais une brioche."),
   D("anna","Вот, пожалуйста.","Voilà."),
   D("luka","Спасибо!","Merci !"),
   D("anna","Пожалуйста!","Je vous en prie !")],
 phrases=[
   ph("want","anna","Что вы хотите?","Qu'est-ce que vous désirez ?","« Что » = quoi, « хотите » = (vous) voulez. Mot à mot : « quoi vous voulez ? ».","хотите",["хочу","спасибо"],["что вы хотите"],"Avec « вы », c'est « хотите ». « Хочу », c'est pour « я »."),
   ph("coffee","luka","Я хочу кофе, пожалуйста.","Je voudrais un café, s'il vous plaît.","« Я хочу » = je veux. Avec « пожалуйста », c'est tout à fait poli en russe.","хочу",["хотите","спасибо"],["я хочу кофе пожалуйста","пожалуйста я хочу кофе"],"Avec « я », c'est « хочу ». « Хотите », c'est pour « вы »."),
   ph("more","anna","Что-нибудь ещё?","Autre chose ?","Mot à mot : « quelque chose encore ? ». On l'entend dans tous les cafés et magasins.","ещё",["вот","хочу"]),
   ph("bun","luka","Да, я хочу булочку.","Oui, je voudrais une brioche.","« Булочка » = une brioche. Après « хочу », elle devient « булочку ».","булочку",["булочка","спасибо"],["да я хочу булочку"],"Après « хочу », le -а final devient -у : « булочка » → « булочку »."),
   ph("here","anna","Вот, пожалуйста.","Voilà.","« Вот » = voici, voilà. On ajoute souvent « пожалуйста » en tendant quelque chose.","вот",["хотите","спасибо"]),
   ph("thanks","luka","Спасибо!","Merci !","Tu le connais déjà !"),
   ph("welcome","anna","Пожалуйста!","Je vous en prie !","« Пожалуйста » veut dire « s'il vous plaît », mais aussi « je vous en prie » en réponse à « спасибо ».")],
 parts=[{"titleFr":"Commander","steps":[SC,B(["want","coffee"]),EX,I(0),B(["more","bun"],["want","coffee"])]},
   {"titleFr":"Remercier","steps":[W(["want","coffee","more","bun"]),B(["here","thanks","welcome"],["more","bun"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"anna","fr":["Tu as vu ? Après « хочу » (je veux), « вода » devient « воду » et « булочка » devient « булочку » : le -а final se change en -у.","« Чай » ne bouge pas : c'est un mot masculin, et ici les masculins restent tels quels.","Ce bleu, tu le reverras chaque fois qu'un mot désigne la chose qu'on veut, qu'on prend ou qu'on aime."]},
   {"by":"anna","fr":["« Пожалуйста » a deux sens : « s'il vous plaît » quand tu demandes, et « je vous en prie » quand tu réponds à « спасибо ».","Et « вот » = « voilà », quand on tend quelque chose."]}],
 explore={"type":"case","speaker":"luka","case":"accs","frame":"Я хочу ___.","frameFr":"Je voudrais ___.","color":"#3a86ff","hintFr":"Mets chaque mot après « хочу » et regarde bien la fin du mot.","words":[
   {"tile":"вода","fr":"l'eau","phraseFr":"Je voudrais de l'eau."},
   {"tile":"булочка","fr":"une brioche","phraseFr":"Je voudrais une brioche."},
   {"tile":"чай","fr":"le thé","phraseFr":"Je voudrais du thé."},
   {"tile":"пицца","fr":"une pizza","phraseFr":"Je voudrais une pizza."}]},
 tasks=[{"type":"pick","fr":"Commande une pizza.","answer":"пицца"},{"type":"pick","fr":"Demande de l'eau.","answer":"вода"}],
 cando=["commander au café","dire merci et répondre à un merci"],
 unlocks=[{"case":"accs","gender":"femn","from":"вода","to":"воду"},{"case":"accs","gender":"masc","from":"чай","to":"чай"}],
 glossary={"здравствуйте":"bonjour (poli)","что":"quoi, que","вы":"vous","хотите":"(vous) voulez","я":"je, moi","хочу":"(je) veux","кофе":"café","пожалуйста":"s'il vous plaît / je vous en prie","француз":"Français","да":"oui","из":"de (provenance)","франции":"France","что-нибудь":"quelque chose","ещё":"encore","булочку":"brioche (après хочу)","булочка":"brioche","вот":"voici, voilà","спасибо":"merci","вода":"eau","воду":"eau (après хочу)","чай":"thé","пицца":"pizza"})

# ---------------- 4. Je ne comprends pas ----------------
lesson(id="04-comprendre", order=4, titleFr="Je ne comprends pas", titleRu="Я не понимаю", emoji="🤔",
 sceneFr="En sortant du café, un passant pressé demande son chemin à Luka. Il parle vite… beaucoup trop vite.",
 dialogue=[D("oleg","Извините, где здесь банк?","Excusez-moi, où est la banque, par ici ?"),
   D("luka","Извините, я не понимаю.","Pardon, je ne comprends pas."),
   D("oleg","Где здесь банк?","Où est la banque, par ici ?"),
   D("luka","Говорите медленнее, пожалуйста.","Parlez plus lentement, s'il vous plaît."),
   D("oleg","Вы говорите по-р+усски?","Vous parlez russe ?"),
   D("luka","Немного. Я понимаю, но плохо.","Un peu. Je comprends, mais mal."),
   D("oleg","А по-англ+ийски?","Et anglais ?"),
   D("luka","Нет. Я говорю по-франц+узски.","Non. Je parle français."),
   D("oleg","Ничего! Банк там.","Ce n'est pas grave ! La banque est là-bas."),
   D("luka","Спасибо!","Merci !")],
 phrases=[
   ph("bank","oleg","Извините, где здесь банк?","Excusez-moi, où est la banque, par ici ?","« Где » = où, « здесь » = ici. Encore une phrase sans verbe « être ».","где",["спасибо","нет"],["извините где здесь банк","извините где банк здесь"]),
   ph("notund","luka","Извините, я не понимаю.","Pardon, je ne comprends pas.","« Не » devant le verbe = ne… pas. La phrase de survie n° 1 !","понимаю",["понимаете","банк"],["извините я не понимаю"],"Avec « я », c'est « понимаю » (-ю). « Понимаете », c'est pour « вы »."),
   ph("slower","luka","Говорите медленнее, пожалуйста.","Parlez plus lentement, s'il vous plaît.","« Говорите » = parlez, « медленнее » = plus lentement. La phrase de survie n° 2 !","медленнее",["банк","спасибо"],["говорите медленнее пожалуйста","пожалуйста говорите медленнее"]),
   ph("speakru","oleg","Вы говорите по-р+усски?","Vous parlez russe ?","Tu la connais déjà : Macha t'a posé la même question.","говорите",["говорю","банк"],["вы говорите по-русски","по-русски вы говорите","вы по-русски говорите"],"Avec « вы », le verbe finit en -ите : « вы говорите »."),
   ph("badly","luka","Немного. Я понимаю, но плохо.","Un peu. Je comprends, mais mal.","« Но » = mais, « плохо » = mal (le contraire de « хорошо »).","плохо",["банк","где"]),
   ph("english","oleg","А по-англ+ийски?","Et anglais ?","« А » = et (pour enchaîner sur autre chose)."),
   ph("no","luka","Нет. Я говорю по-франц+узски.","Non. Je parle français.","« Нет » = non.","нет",["где","как"]),
   ph("nevermind","oleg","Ничего! Банк там.","Ce n'est pas grave ! La banque est là-bas.","« Ничего » = mot à mot « rien » ; ici « ce n'est rien, pas grave ». « Там » = là-bas.","там",["не","как"])],
 parts=[{"titleFr":"Dire qu'on ne comprend pas","steps":[SC,B(["bank","notund"]),B(["slower","speakru"],["notund"])]},
   {"titleFr":"Comprendre et parler","steps":[W(["notund","slower","speakru"]),EX,I(0),B(["badly","english","no"],["slower","speakru"]),B(["nevermind"],["badly","no"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"oleg","fr":["Comme en français, la fin du verbe change avec la personne : « je comprends », « vous comprenez »…","Я понима-ю, ты понима-ешь, мы понима-ем, вы понима-ете : écoute surtout la fin violette, c'est elle qui dit qui parle.","« Вы » sert à vouvoyer quelqu'un ou à parler à plusieurs personnes, exactement comme « vous »."]},
   {"by":"oleg","fr":["Pour dire non, il suffit de mettre « не » devant le verbe : « я не понимаю » = « je ne comprends pas ».","Et pour répondre « non » tout court : « нет »."]}],
 explore={"type":"person","speaker":"luka","verb":"понимать","frame":"___ {V} по-р+усски.","frameFr":"___ comprendre le russe.","color":"#8e44ad","hintFr":"Change la personne et écoute la fin du verbe.","words":[
   {"tile":"я","fr":"je","phraseFr":"Je comprends le russe."},
   {"tile":"ты","fr":"tu","phraseFr":"Tu comprends le russe."},
   {"tile":"она","fr":"elle","phraseFr":"Elle comprend le russe."},
   {"tile":"мы","fr":"nous","phraseFr":"Nous comprenons le russe."},
   {"tile":"вы","fr":"vous","phraseFr":"Vous comprenez le russe."},
   {"tile":"они","fr":"ils, elles","phraseFr":"Ils comprennent le russe."}]},
 tasks=[{"type":"pick","fr":"Dis : « Vous comprenez le russe. »","answer":"вы"},{"type":"pick","fr":"Dis : « Nous comprenons le russe. »","answer":"мы"}],
 cando=["dire que tu ne comprends pas","demander de parler plus lentement","dire quelle langue tu parles"],
 unlocks=[{"verb":"понимать","persons":["я","ты","он","мы","вы","они"]}],
 glossary={"извините":"excusez-moi, pardon","где":"où","здесь":"ici","банк":"banque","я":"je, moi","не":"ne… pas","понимаю":"(je) comprends","понимаете":"(vous) comprenez","говорите":"parlez / (vous) parlez","медленнее":"plus lentement","пожалуйста":"s'il vous plaît","вы":"vous","по-русски":"en russe","немного":"un peu","но":"mais","плохо":"mal","а":"et, mais","по-английски":"en anglais","нет":"non","говорю":"(je) parle","по-французски":"en français","ничего":"pas grave (mot à mot : rien)","там":"là-bas","спасибо":"merci","ты":"tu","она":"elle","мы":"nous","они":"ils, elles","понимаешь":"(tu) comprends","понимает":"(il, elle) comprend","понимаем":"(nous) comprenons","понимают":"(ils) comprennent","как":"comment"})

# ---------------- 5. Où es-tu ? ----------------
lesson(id="05-ville", order=5, titleFr="Où es-tu ?", titleRu="Ты где?", emoji="🗺️",
 sceneFr="Luka se promène en ville quand son téléphone sonne : c'est Macha, sa voisine. Depuis leur rencontre, ils se tutoient.",
 dialogue=[D("masha","Алло, Л+ука! Ты где?","Allô, Luka ! Tu es où ?"),
   D("luka","Привет, М+аша! Я в парке.","Salut, Macha ! Je suis au parc."),
   D("masha","А я в кафе. Это близко.","Et moi, je suis au café. C'est tout près."),
   D("luka","Где кафе?","Où est le café ?"),
   D("masha","Прямо, потом направо.","Tout droit, puis à droite."),
   D("luka","Это далеко?","C'est loin ?"),
   D("masha","Нет, пять минут.","Non, cinq minutes."),
   D("luka","Хорошо, иду!","D'accord, j'arrive !")],
 phrases=[
   ph("where","masha","Алло, Л+ука! Ты где?","Allô, Luka ! Tu es où ?","« Ты » = tu : entre amis, on se tutoie. « Где » = où.","где",["парке","привет"]),
   ph("park","luka","Привет, М+аша! Я в парке.","Salut, Macha ! Je suis au parc.","« Привет » = salut (entre amis). « В парке » = au parc : « парк » devient « парке ».","парке",["парк","близко"],None,"Après « в » (pour dire où l'on est), on ajoute -е : « парк » → « в парке »."),
   ph("cafe","masha","А я в кафе. Это близко.","Et moi, je suis au café. C'est tout près.","« Кафе » ne change jamais. « Это » = c'est, « близко » = près.","близко",["привет","минут"]),
   ph("wherecafe","luka","Где кафе?","Où est le café ?","Toujours sans verbe « être » : « où café ? ».","где",["иду","хорошо"]),
   ph("direction","masha","Прямо, потом направо.","Tout droit, puis à droite.","« Прямо » = tout droit, « потом » = puis, « направо » = à droite.","направо",["парке","минут"],["прямо потом направо"]),
   ph("far","luka","Это далеко?","C'est loin ?","« Далеко » = loin, le contraire de « близко ».","далеко",["привет","иду"]),
   ph("five","masha","Нет, пять минут.","Non, cinq minutes.","« Пять » = cinq, « минут » = minutes.","пять",["где","иду"]),
   ph("coming","luka","Хорошо, иду!","D'accord, j'arrive !","« Хорошо » = bien, d'accord. « Иду » = (je) vais, j'arrive (à pied).","иду",["минут","парке"])],
 parts=[{"titleFr":"Dire où tu es","steps":[SC,EX,I(0),B(["where","park"]),B(["cafe","wherecafe"],["park"])]},
   {"titleFr":"Trouver le chemin","steps":[W(["where","park","cafe","wherecafe"]),B(["direction","far"],["cafe","wherecafe"]),B(["five","coming"],["direction","far"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Pour dire où tu es, on met « в » (dans, à) devant le lieu, et la fin du mot change : « парк » → « в парке ».","Le plus souvent, on ajoute -е ou on remplace la dernière voyelle par -е : « театр » → « в театре », « Москва » → « в Москве ».","Ce vert marque toujours le lieu où l'on se trouve. « Кафе » et « метро » sont des mots venus d'ailleurs : ils ne changent jamais."]},
   {"by":"masha","fr":["Entre amis, on dit « привет » (salut) et « ты » (tu). Avec un inconnu, c'est « здравствуйте » et « вы ».","Macha et Luka se connaissent maintenant : ils se tutoient !"]}],
 explore={"type":"case","speaker":"luka","case":"loct","frame":"Я в ___.","frameFr":"Je suis ___.","color":"#2a9d8f","hintFr":"Mets chaque lieu après « в » et regarde bien la fin du mot.","words":[
   {"tile":"парк","fr":"le parc","phraseFr":"Je suis au parc."},
   {"tile":"Москва","fr":"Moscou","phraseFr":"Je suis à Moscou."},
   {"tile":"гостиница","fr":"l'hôtel","phraseFr":"Je suis à l'hôtel."},
   {"tile":"театр","fr":"le théâtre","phraseFr":"Je suis au théâtre."}]},
 tasks=[{"type":"pick","fr":"Dis que tu es à l'hôtel.","answer":"гостиница"},{"type":"pick","fr":"Dis que tu es à Moscou.","answer":"Москва"}],
 cando=["dire où tu es","demander si c'est loin","comprendre un chemin simple"],
 unlocks=[{"case":"loct","gender":"masc","from":"парк","to":"парке"},{"case":"loct","gender":"femn","from":"Москва","to":"Москве"}],
 glossary={"алло":"allô","лука":"Luka (prénom)","ты":"tu","где":"où","привет":"salut","маша":"Macha (prénom)","я":"je, moi","в":"dans, à","парке":"parc (après в)","парк":"parc","а":"et, mais","кафе":"café","это":"c'est, ce","близко":"près","прямо":"tout droit","потом":"puis, ensuite","направо":"à droite","далеко":"loin","нет":"non","пять":"cinq","минут":"minutes","хорошо":"bien, d'accord","иду":"(je) vais, j'arrive","москва":"Moscou","гостиница":"hôtel","театр":"théâtre"})

# ---------------- 6. Au magasin ----------------
lesson(id="06-magasin", order=6, titleFr="Au magasin", titleRu="В магазине", emoji="🛒",
 sceneFr="Avant de rejoindre Macha, Luka fait quelques courses dans la petite épicerie du quartier. Nina tient la caisse.",
 dialogue=[D("nina","Здравствуйте! Я вас слушаю.","Bonjour ! Je vous écoute."),
   D("luka","Здравствуйте! У вас есть хлеб?","Bonjour ! Vous avez du pain ?"),
   D("nina","Да, есть.","Oui, il y en a."),
   D("luka","Дайте, пожалуйста, хлеб и молоко.","Donnez-moi du pain et du lait, s'il vous plaît."),
   D("nina","Что-нибудь ещё?","Autre chose ?"),
   D("luka","Да, дайте рыбу. Сколько стоит рыба?","Oui, donnez-moi du poisson. Combien coûte le poisson ?"),
   D("nina","Триста рублей.","Trois cents roubles."),
   D("luka","Хорошо. Вот, пожалуйста.","D'accord. Voilà."),
   D("nina","Спасибо! До свидания!","Merci ! Au revoir !"),
   D("luka","До свидания!","Au revoir !")],
 phrases=[
   ph("listen","nina","Здравствуйте! Я вас слушаю.","Bonjour ! Je vous écoute.","Ce que disent souvent les vendeurs : « je vous écoute » = « que puis-je pour vous ? ».","слушаю",["хлеб","стоит"]),
   ph("have","luka","У вас есть хлеб?","Vous avez du pain ?","« У вас есть…? » = « Vous avez… ? ». Mot à mot : « chez vous, il y a… ? ». Très pratique dans les magasins.","есть",["дайте","стоит"],["у вас есть хлеб","хлеб у вас есть","есть у вас хлеб"]),
   ph("yes","nina","Да, есть.","Oui, il y en a.","« Есть » = il y a. On répond simplement « да, есть »."),
   ph("give","luka","Дайте, пожалуйста, хлеб и молоко.","Donnez-moi du pain et du lait, s'il vous plaît.","« Дайте » = donnez. « Хлеб » (masculin) et « молоко » (neutre) ne changent pas ici.","дайте",["сколько","стоит"],["дайте пожалуйста хлеб и молоко","дайте хлеб и молоко пожалуйста","пожалуйста дайте хлеб и молоко"]),
   ph("fish","luka","Да, дайте рыбу.","Oui, donnez-moi du poisson.","Après « дайте », c'est comme après « хочу » : « рыба » → « рыбу ».","рыбу",["рыба","стоит"],["да дайте рыбу"],"Après « дайте », le -а final devient -у : « рыба » → « рыбу »."),
   ph("price","luka","Сколько стоит рыба?","Combien coûte le poisson ?","« Сколько стоит…? » = combien coûte… ? Ici, le poisson fait l'action (il coûte) : il garde sa forme de base, « рыба ».","рыба",["рыбу","дайте"],["сколько стоит рыба","рыба сколько стоит"],"Ici, « рыба » fait l'action (c'est elle qui coûte) : pas de -у. « Рыбу », c'est après « дайте » ou « хочу »."),
   ph("rubles","nina","Триста рублей.","Trois cents roubles.","« Триста » = trois cents, « рублей » = roubles."),
   ph("ok","luka","Хорошо. Вот, пожалуйста.","D'accord. Voilà.","Tu connais déjà tous ces mots !","вот",["сколько","стоит"]),
   ph("bye","luka","До свидания!","Au revoir !","Tu le connais depuis ta rencontre avec Macha.")],
 parts=[{"titleFr":"Demander","steps":[SC,B(["listen","have"]),B(["give","yes"],["have"])]},
   {"titleFr":"Combien ça coûte ?","steps":[W(["have","give","yes"]),EX,I(0),B(["fish","price"],["give"]),B(["rubles","ok","bye"],["fish","price"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"nina","fr":["Tu reconnais ce bleu ? Après « дайте » (donnez), c'est comme après « хочу » : « рыба » → « рыбу », « газета » → « газету ».","« Хлеб » (masculin) et « молоко » (neutre) ne changent pas.","Le russe a trois genres : masculin (souvent une consonne à la fin), féminin (-а, -я) et neutre (-о, -е)."]},
   {"by":"nina","fr":["Mais attention : dans « Сколько стоит рыба ? », c'est le poisson qui coûte. Il fait l'action, donc il reste « рыба ».","La règle simple : -у pour la chose qu'on veut, qu'on prend, qu'on demande. La forme de base pour ce qui fait l'action."]}],
 explore={"type":"case","speaker":"luka","case":"accs","frame":"Дайте, пожалуйста, ___.","frameFr":"Donnez-moi ___, s'il vous plaît.","color":"#3a86ff","hintFr":"Mets chaque mot après « дайте » et regarde bien la fin du mot.","words":[
   {"tile":"хлеб","fr":"le pain","phraseFr":"Donnez-moi du pain, s'il vous plaît."},
   {"tile":"молоко","fr":"le lait","phraseFr":"Donnez-moi du lait, s'il vous plaît."},
   {"tile":"рыба","fr":"le poisson","phraseFr":"Donnez-moi du poisson, s'il vous plaît."},
   {"tile":"газета","fr":"un journal","phraseFr":"Donnez-moi un journal, s'il vous plaît."}]},
 tasks=[{"type":"pick","fr":"Demande un journal.","answer":"газета"},{"type":"pick","fr":"Demande du lait.","answer":"молоко"}],
 cando=["demander si un produit est là","demander quelque chose poliment","demander le prix"],
 unlocks=[{"case":"accs","gender":"neut","from":"молоко","to":"молоко"},{"case":"accs","gender":"femn","from":"рыба","to":"рыбу"}],
 glossary={"здравствуйте":"bonjour (poli)","я":"je, moi","вас":"vous","слушаю":"(j')écoute","у":"chez (у вас есть = vous avez)","есть":"il y a","хлеб":"pain","да":"oui","дайте":"donnez","пожалуйста":"s'il vous plaît","и":"et","молоко":"lait","что-нибудь":"quelque chose","ещё":"encore","рыбу":"poisson (après дайте)","рыба":"poisson","сколько":"combien","стоит":"coûte","триста":"trois cents","рублей":"roubles","хорошо":"bien, d'accord","вот":"voici, voilà","спасибо":"merci","до":"jusqu'à","свидания":"revoir (до свидания = au revoir)","газета":"journal"})

# ---------------- 7. Chez des amis ----------------
lesson(id="07-amis", order=7, titleFr="Chez des amis", titleRu="В гостях", emoji="🍽️",
 sceneFr="Le soir, Macha invite Luka à dîner. Son ami Oleg est là aussi… et Luka a l'impression de l'avoir déjà vu quelque part.",
 dialogue=[D("masha","Л+ука, это мой друг Ол+ег.","Luka, voici mon ami Oleg."),
   D("oleg","Привет! Мы знакомы! Банк, да?","Salut ! On se connaît ! La banque, c'est ça ?"),
   D("luka","Да! Очень приятно, Ол+ег.","Oui ! Enchanté, Oleg."),
   D("oleg","Где ты живёшь, Л+ука?","Où est-ce que tu habites, Luka ?"),
   D("luka","Сейчас я живу в Петерб+урге. А дома я живу в Ли+оне.","En ce moment, j'habite à Saint-Pétersbourg. Mais chez moi, j'habite à Lyon."),
   D("oleg","Как интересно! Что ты любишь?","Comme c'est intéressant ! Qu'est-ce que tu aimes ?"),
   D("luka","Я люблю музыку и кино.","J'aime la musique et le cinéma."),
   D("masha","А я люблю книги.","Et moi, j'aime les livres."),
   D("oleg","Давайте ужинать!","À table !")],
 phrases=[
   ph("friend","masha","Л+ука, это мой друг Ол+ег.","Luka, voici mon ami Oleg.","« Это » = voici, c'est. « Мой друг » = mon ami.","друг",["кино","живу"]),
   ph("known","oleg","Привет! Мы знакомы!","Salut ! On se connaît !","« Мы знакомы » = nous nous connaissons. C'est le passant de la banque !","знакомы",["живу","люблю"]),
   ph("nice","luka","Да! Очень приятно, Ол+ег.","Oui ! Enchanté, Oleg.","Tu connais « очень приятно » depuis ta rencontre avec Macha.","приятно",["живу","люблю"]),
   ph("livewhere","oleg","Где ты живёшь, Л+ука?","Où est-ce que tu habites, Luka ?","Entre amis, on se tutoie : « ты живёшь » (tu habites).","живёшь",["живу","кино"],["где ты живёшь лука","лука где ты живёшь"],"Avec « ты », le verbe finit en -ёшь : « ты живёшь ». « Живу », c'est pour « я »."),
   ph("livespb","luka","Сейчас я живу в Петерб+урге.","En ce moment, j'habite à Saint-Pétersbourg.","« Сейчас » = maintenant, en ce moment. Les Russes disent souvent « Петербург » tout court.","петербурге",["петербург","люблю"],["сейчас я живу в петербурге","я сейчас живу в петербурге","я живу в петербурге сейчас"],"Après « в » (pour dire où l'on est), « Петербург » devient « в Петербурге »."),
   ph("livelyon","luka","А дома я живу в Ли+оне.","Mais chez moi, j'habite à Lyon.","« Дома » = à la maison, chez moi.","лионе",["лион","люблю"],["а дома я живу в лионе","а я дома живу в лионе"],"Après « в » (pour dire où l'on est), « Лион » devient « в Лионе »."),
   ph("like","oleg","Как интересно! Что ты любишь?","Comme c'est intéressant ! Qu'est-ce que tu aimes ?","« Интересно » = intéressant. « Любишь » = (tu) aimes.","любишь",["люблю","живу"],None,"Avec « ты », c'est « любишь ». « Люблю », c'est pour « я »."),
   ph("music","luka","Я люблю музыку и кино.","J'aime la musique et le cinéma.","Après « люблю », c'est comme après « хочу » : « музыка » → « музыку ». « Кино » ne change jamais.","музыку",["музыка","живу"],["я люблю музыку и кино","я люблю кино и музыку"],"Après « люблю », le -а final devient -у : « музыка » → « музыку »."),
   ph("books","masha","А я люблю книги.","Et moi, j'aime les livres.","« Книги » = des livres.","люблю",["любишь","живу"],None,"Avec « я », c'est « люблю ». « Любишь », c'est pour « ты »."),
   ph("dinner","oleg","Давайте ужинать!","À table !","Mot à mot : « allons dîner ! ».")],
 parts=[{"titleFr":"Retrouvailles","steps":[SC,B(["friend","known"]),B(["nice","livewhere"],["known"])]},
   {"titleFr":"Où tu habites, ce que tu aimes","steps":[W(["friend","nice","livewhere"]),EX,I(0),B(["livespb","livelyon"],["livewhere"]),B(["like","music","books"],["livespb","livelyon"]),I(1),B(["dinner"],["music","books"])]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Tu connais déjà ce vert : « в парке ». C'est pareil pour les villes : « в Лионе », « в Париже ».","Les mots en -ия sont un peu spéciaux : « Россия » → « в России »."]},
   {"by":"masha","fr":["« Люблю » (j'aime) fonctionne comme « хочу » : « музыка » → « я люблю музыку ». En bleu !","À la banque, Oleg disait « вы » à Luka. Maintenant ils sont amis : « ты живёшь », « ты любишь »."]}],
 explore={"type":"case","speaker":"luka","case":"loct","frame":"Я живу в ___.","frameFr":"J'habite ___.","color":"#2a9d8f","hintFr":"Mets chaque ville après « в » et regarde bien la fin du mot.","words":[
   {"tile":"Ли+он","fr":"Lyon","phraseFr":"J'habite à Lyon."},
   {"tile":"Париж","fr":"Paris","phraseFr":"J'habite à Paris."},
   {"tile":"Марс+ель","formAcc":"Марс+еле","fr":"Marseille","phraseFr":"J'habite à Marseille."},
   {"tile":"Россия","fr":"la Russie","phraseFr":"J'habite en Russie."}]},
 tasks=[{"type":"pick","fr":"Dis que tu habites à Paris.","answer":"Париж"},{"type":"pick","fr":"Dis que tu habites en Russie.","answer":"Россия"}],
 cando=["présenter quelqu'un","dire où tu habites","dire ce que tu aimes"],
 unlocks=[{"case":"loct","gender":"masc","from":"Лион","to":"Лионе"},{"case":"loct","gender":"femn","from":"Россия","to":"России"},{"case":"accs","gender":"femn","from":"музыка","to":"музыку"},{"verb":"жить","persons":["я","ты"]},{"verb":"любить","persons":["я","ты"]}],
 glossary={"лука":"Luka (prénom)","это":"voici, c'est","мой":"mon","друг":"ami","олег":"Oleg (prénom)","привет":"salut","мы":"nous","знакомы":"(nous) nous connaissons","банк":"banque","да":"oui","очень":"très","приятно":"agréable","где":"où","ты":"tu","живёшь":"(tu) habites","живешь":"(tu) habites","сейчас":"maintenant","я":"je, moi","живу":"(j')habite","в":"dans, à","петербурге":"Saint-Pétersbourg (après в)","петербург":"Saint-Pétersbourg","а":"et, mais","дома":"à la maison","лионе":"Lyon (après в)","лион":"Lyon","как":"comme, comment","интересно":"intéressant","что":"quoi, que","любишь":"(tu) aimes","люблю":"(j')aime","музыку":"musique (après люблю)","музыка":"musique","и":"et","кино":"cinéma","книги":"livres","давайте":"allons, faisons","ужинать":"dîner","кино":"cinéma","париж":"Paris","марсель":"Marseille","россия":"Russie"})
print("ok")
