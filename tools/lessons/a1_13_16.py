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
COMMON={"я":"je, moi","ты":"tu","вы":"vous","да":"oui","нет":"non","а":"et, mais","и":"et","это":"c'est, voici","не":"ne… pas","в":"dans, à","на":"sur, en","что":"quoi, que","как":"comment, comme","где":"où","очень":"très","спасибо":"merci","пожалуйста":"s'il te plaît / je t'en prie","хорошо":"bien, d'accord","привет":"salut","лука":"Luka (prénom)","маша":"Macha (prénom)","олег":"Oleg (prénom)","анна":"Anna (prénom)","у":"chez","меня":"moi (у меня = j'ai)","тебя":"toi (у тебя = tu as)","есть":"il y a","мой":"mon","моя":"ma","мне":"à moi","тоже":"aussi","сегодня":"aujourd'hui","завтра":"demain","вчера":"hier","потом":"puis, ensuite","давай":"allons-y, faisons"}
def G(d): return {**COMMON, **d}
def C(ru, fr, extra, orders=None, note=""):
    d={"ru":ru,"fr":fr,"extra":extra}
    if orders: d["orders"]=orders
    if note: d["noteFr"]=note
    return d

# ---------------- 13. Demain (futur) ----------------
lesson(id="13-demain", order=13, titleFr="Les projets", titleRu="Планы", emoji="📅",
 sceneFr="Vendredi, Oleg appelle Luka pour parler du week-end qui arrive.",
 dialogue=[D("oleg","Привет, Л+ука! Что ты будешь делать завтра?","Salut, Luka ! Qu'est-ce que tu vas faire demain ?"),
   D("luka","Утром я буду учить русский.","Le matin, je vais étudier le russe."),
   D("luka","А потом я буду гулять в парке.","Et après, je vais me promener au parc."),
   D("oleg","А вечером? Ты будешь дома?","Et le soir ? Tu seras à la maison ?"),
   D("luka","Не знаю. А что?","Je ne sais pas. Pourquoi ?"),
   D("oleg","Мы будем играть в футбол. Хочешь с нами?","On va jouer au foot. Tu veux venir avec nous ?"),
   D("luka","Конечно хочу! Где?","Bien sûr que je veux ! Où ?"),
   D("oleg","В парке, в семь часов.","Au parc, à sept heures.")],
 phrases=[
   ph("plans","oleg","Что ты будешь делать завтра?","Qu'est-ce que tu vas faire demain ?","Le futur : « будешь » + verbe à l'infinitif. « Будешь делать » = tu vas faire.","будешь",["буду","завтра"],["что ты будешь делать завтра","что ты завтра будешь делать","завтра что ты будешь делать"],"Avec « ты » : « будешь ». « Буду », c'est pour « я »."),
   ph("study","luka","Утром я буду учить русский.","Le matin, je vais étudier le russe.","« Я буду » + infinitif = je vais (faire). « Учить » = étudier, apprendre.","буду",["будешь","завтра"],["утром я буду учить русский","я буду учить русский утром"],"Avec « я » : « буду »."),
   ph("walk","luka","А потом я буду гулять в парке.","Et après, je vais me promener au parc.","« Гулять » = se promener. « В парке » : tu connais ce vert.","гулять",["гуляю","парк"],["а потом я буду гулять в парке","а потом я буду в парке гулять"],"Après « буду », le verbe reste à l'infinitif (-ть) : « буду гулять »."),
   ph("home","oleg","А вечером? Ты будешь дома?","Et le soir ? Tu seras à la maison ?","« Ты будешь дома ? » = tu seras à la maison ? « Быть » au futur, tout seul.","дома",["парк","завтра"]),
   ph("dunno","luka","Не знаю. А что?","Je ne sais pas. Pourquoi ?","« Не знаю » = je ne sais pas. « А что ? » = pourquoi ? (mot à mot : « et quoi ? »).","знаю",["знаешь","буду"],None,"Avec « я » : « знаю » (-ю)."),
   ph("football","oleg","Мы будем играть в футбол. Хочешь с нами?","On va jouer au foot. Tu veux venir avec nous ?","« Мы будем » = nous allons. « Играть в футбол » = jouer au foot. « С нами » = avec nous.","будем",["буду","играть"],None,"Avec « мы » : « будем »."),
   ph("sure","luka","Конечно хочу! Где?","Bien sûr que je veux ! Où ?","« Конечно » = bien sûr.","конечно",["завтра","дома"]),
   ph("seven","oleg","В парке, в семь часов.","Au parc, à sept heures.","« В семь часов » = à sept heures.","семь",["где","дома"])],
 parts=[{"titleFr":"Demain","steps":[SC,EX,I(0),B(["plans","study"]),B(["walk","home"],["study"])]},
   {"titleFr":"Une proposition","steps":[W(["plans","study","walk"]),B(["dunno","football"],["walk","home"]),B(["sure","seven"],["football"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"oleg","fr":["Le futur, c'est facile : « буду » + le verbe à l'infinitif (avec -ть). « Я буду работать » = je vais travailler.","Seul « буду » change : я буду, ты будешь, он будет, мы будем, вы будете, они будут.","Tu connais déjà « я буду » du restaurant : « я буду суп » = je vais prendre une soupe !"]},
   {"by":"oleg","fr":["Maintenant tu sais parler du passé (я работал), du présent (я работаю) et du futur (я буду работать).","Avec ces trois-là, tu peux déjà raconter presque toute ta vie !"]}],
 explore={"type":"plain","speaker":"luka","frame":"Завтра я буду ___.","frameFr":"Demain, je vais ___.","color":"#8e44ad","hintFr":"Mets chaque verbe après « буду » et écoute.","words":[
   {"tile":"работать","fr":"travailler","phraseFr":"Demain, je vais travailler."},{"tile":"отдыхать","fr":"me reposer","phraseFr":"Demain, je vais me reposer."},
   {"tile":"читать","fr":"lire","phraseFr":"Demain, je vais lire."},{"tile":"гулять","fr":"me promener","phraseFr":"Demain, je vais me promener."}]},
 tasks=[{"type":"pick","fr":"Dis : « Demain, je vais lire. »","answer":"читать"},{"type":"pick","fr":"Dis : « Demain, je vais travailler. »","answer":"работать"}],
 cando=["parler de tes projets","parler au futur","accepter une proposition"],
 unlocks=[],
 glossary=G({"будешь":"(tu) seras","буду":"(je) serai","будем":"(nous) serons","делать":"faire","утром":"le matin","учить":"étudier, apprendre","русский":"le russe","гулять":"se promener","гуляю":"(je) me promène","парке":"parc (après в)","парк":"parc","вечером":"le soir","дома":"à la maison","знаю":"(je) sais","знаешь":"(tu) sais","мы":"nous","играть":"jouer","футбол":"football","хочешь":"(tu) veux","с":"avec","нами":"nous (с нами = avec nous)","конечно":"bien sûr","хочу":"(je) veux","семь":"sept","часов":"heures","работать":"travailler","отдыхать":"se reposer","читать":"lire"}),
 combos=[C("Завтра я буду работать дома.","Demain, je vais travailler à la maison.",["работаю"],["завтра я буду работать дома","завтра я буду дома работать","я буду работать дома завтра"]),
   C("Ты будешь гулять в парке?","Tu vas te promener au parc ?",["буду"],["ты будешь гулять в парке","ты будешь в парке гулять"]),
   C("Я не знаю, где банк.","Je ne sais pas où est la banque.",["буду"])])

# ---------------- 14. Chez le médecin ----------------
lesson(id="14-medecin", order=14, titleFr="Je suis malade", titleRu="Я болею", emoji="🤒",
 sceneFr="Le lendemain du foot, Luka ne se sent pas bien. Il frappe chez sa voisine Macha… qui est médecin !",
 dialogue=[D("masha","Л+ука? Что случилось?","Luka ? Qu'est-ce qui s'est passé ?"),
   D("luka","Маша, мне плохо.","Macha, je ne me sens pas bien."),
   D("masha","Что у тебя болит?","Où est-ce que tu as mal ?"),
   D("luka","У меня болит голова. И горло тоже.","J'ai mal à la tête. Et à la gorge aussi."),
   D("masha","У тебя есть температура?","Tu as de la fièvre ?"),
   D("luka","Да, тридцать восемь.","Oui, trente-huit."),
   D("masha","Это грипп. Пей чай и отдыхай.","C'est la grippe. Bois du thé et repose-toi."),
   D("luka","Спасибо, доктор!","Merci, docteur !")],
 phrases=[
   ph("what","masha","Что случилось?","Qu'est-ce qui s'est passé ?","« Что случилось ? » = qu'est-ce qui s'est passé ? Très courant.","случилось",["болит","плохо"]),
   ph("bad","luka","Маша, мне плохо.","Macha, je ne me sens pas bien.","« Мне плохо » = je me sens mal (mot à mot : « à moi, c'est mal »).","плохо",["хорошо","болит"],None,"« Мне плохо » = je me sens mal. « Мне хорошо », ce serait « je me sens bien »."),
   ph("hurt","masha","Что у тебя болит?","Où est-ce que tu as mal ?","Mot à mot : « qu'est-ce qui te fait mal ? ». « Болит » = fait mal.","болит",["плохо","горло"],["что у тебя болит","у тебя что болит"]),
   ph("head","luka","У меня болит голова.","J'ai mal à la tête.","Mot à mot : « chez moi, la tête fait mal ». La partie du corps reste à la forme de base.","голова",["голову","плохо"],["у меня болит голова","голова у меня болит","у меня голова болит"],"C'est la tête qui fait l'action (elle fait mal) : forme de base « голова », sans -у."),
   ph("throat","luka","И горло тоже.","Et à la gorge aussi.","« Горло » = la gorge. « Тоже » = aussi.","тоже",["болит","есть"]),
   ph("fever","masha","У тебя есть температура?","Tu as de la fièvre ?","« Температура » = fièvre (mot à mot : température).","температура",["голова","горло"],["у тебя есть температура","температура у тебя есть","есть у тебя температура"]),
   ph("advice","masha","Пей чай и отдыхай.","Bois du thé et repose-toi.","L'impératif avec « ты » : « пей » (bois), « отдыхай » (repose-toi).","отдыхай",["отдыхаю","плохо"],["пей чай и отдыхай","отдыхай и пей чай"],"Pour donner un conseil à « ты » : « отдыхай » (-й). « Отдыхаю », c'est « je me repose »."),
   ph("doctor","luka","Спасибо, доктор!","Merci, docteur !","« Доктор » = docteur, comme en français.")],
 parts=[{"titleFr":"Ça ne va pas","steps":[SC,B(["what","bad"]),EX,I(0),B(["hurt","head"],["bad"])]},
   {"titleFr":"Les conseils du médecin","steps":[W(["bad","hurt","head"]),B(["throat","fever"],["head"]),B(["advice","doctor"],["fever","throat"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Pour dire où tu as mal : « у меня болит… » + la partie du corps, à la forme de base. « У меня болит голова » = j'ai mal à la tête.","Tu reconnais « у меня » ? C'est le même que dans « у меня есть » (j'ai)."]},
   {"by":"masha","fr":["Pour donner un conseil ou un ordre à un ami : « пей » (bois), « отдыхай » (repose-toi), « слушай » (écoute).","Avec « вы », on ajoute -те : « отдыхайте », « пейте ». Tu connais déjà « говорите медленнее » !"]}],
 explore={"type":"plain","speaker":"luka","frame":"У меня болит ___.","frameFr":"J'ai mal ___.","color":"#5c677d","hintFr":"Mets chaque partie du corps dans la phrase et écoute.","words":[
   {"tile":"голова","fr":"à la tête","phraseFr":"J'ai mal à la tête."},{"tile":"горло","fr":"à la gorge","phraseFr":"J'ai mal à la gorge."},
   {"tile":"живот","fr":"au ventre","phraseFr":"J'ai mal au ventre."},{"tile":"зуб","fr":"à une dent","phraseFr":"J'ai mal à une dent."}]},
 tasks=[{"type":"pick","fr":"Dis que tu as mal au ventre.","answer":"живот"},{"type":"pick","fr":"Dis que tu as mal à une dent.","answer":"зуб"}],
 cando=["dire que tu ne te sens pas bien","dire où tu as mal","comprendre un conseil simple"],
 unlocks=[],
 glossary=G({"случилось":"(s'est) passé","плохо":"mal","болит":"fait mal","голова":"tête","голову":"tête (après хочу, люблю…)","горло":"gorge","тоже":"aussi","температура":"fièvre, température","тридцать":"trente","восемь":"huit","грипп":"grippe","пей":"bois !","чай":"thé","отдыхай":"repose-toi !","отдыхаю":"(je) me repose","доктор":"docteur","живот":"ventre","зуб":"dent"}),
 combos=[C("Маша, у меня болит живот.","Macha, j'ai mal au ventre.",["плохо"],["маша у меня болит живот","маша у меня живот болит"]),
   C("Мне плохо. Я буду отдыхать дома.","Je ne me sens pas bien. Je vais me reposer à la maison.",["отдыхай"]),
   C("Говорите медленнее, доктор!","Parlez plus lentement, docteur !",["говорю"])])

# ---------------- 15. Une invitation ----------------
lesson(id="15-invitation", order=15, titleFr="Une invitation", titleRu="Приглашение", emoji="🎭",
 sceneFr="Une semaine plus tard, Luka va mieux. Pour remercier Macha, il veut l'inviter au théâtre.",
 dialogue=[D("luka","Маша, ты свободна в субботу?","Macha, tu es libre samedi ?"),
   D("masha","Да, а что?","Oui, pourquoi ?"),
   D("luka","Давай пойдём в театр!","Allons au théâtre !"),
   D("masha","С удовольствием! А что там идёт?","Avec plaisir ! Et qu'est-ce qui se joue ?"),
   D("luka","«Евгений Онегин». Это опера.","« Eugène Onéguine ». C'est un opéra."),
   D("masha","Отлично! Во сколько?","Parfait ! À quelle heure ?"),
   D("luka","В семь. Я куплю билеты.","À sept heures. J'achèterai les billets."),
   D("masha","Спасибо, Л+ука! До субботы!","Merci, Luka ! À samedi !")],
 phrases=[
   ph("free","luka","Маша, ты свободна в субботу?","Macha, tu es libre samedi ?","« Свободна » = libre (pour une femme). Pour un homme : « свободен ».","свободна",["свободен","театр"],["маша ты свободна в субботу","маша в субботу ты свободна"],"Macha est une femme : « свободна » (-а). « Свободен », c'est pour un homme."),
   ph("why","masha","Да, а что?","Oui, pourquoi ?","Tu connais « а что ? » = pourquoi ?"),
   ph("letsgo","luka","Давай пойдём в театр!","Allons au théâtre !","« Давай пойдём… » = allons… ! Pour aller VERS : « в театр », sans -е.","театр",["театре","опера"],["давай пойдём в театр"],"On va VERS le théâtre : « в театр ». « В театре » (-е), c'est quand on y est déjà."),
   ph("pleasure","masha","С удовольствием!","Avec plaisir !","« С удовольствием » = avec plaisir. La réponse parfaite à une invitation.","удовольствием",["театр","билеты"]),
   ph("opera","luka","Это опера.","C'est un opéra.","« Опера » = opéra. « Евгений Онегин » est un opéra très célèbre de Tchaïkovski.","опера",["театр","билеты"]),
   ph("when","masha","Отлично! Во сколько?","Parfait ! À quelle heure ?","« Отлично » = parfait, excellent. « Во сколько ? » = à quelle heure ?","отлично",["театр","субботы"]),
   ph("tickets","luka","В семь. Я куплю билеты.","À sept heures. J'achèterai les billets.","« Куплю » = j'achèterai. « Билеты » = les billets.","билеты",["театр","опера"],None),
   ph("seeyou","masha","До субботы!","À samedi !","« До субботы » = à samedi (jusqu'à samedi). Comme « до свидания » !","субботы",["субботу","театр"],None,"Après « до » (jusqu'à) : « до субботы ». Retiens-le comme « до свидания ».")],
 parts=[{"titleFr":"Inviter","steps":[SC,B(["free","why"]),EX,I(0),B(["letsgo","pleasure"],["free"])]},
   {"titleFr":"Se mettre d'accord","steps":[W(["free","letsgo","pleasure"]),B(["opera","when"],["letsgo"]),B(["tickets","seeyou"],["when","pleasure"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Pour aller VERS un lieu, on utilise le bleu, comme pour ce qu'on veut : « в театр », « в кино », « в библиотеку ».","Et pour dire où l'on EST, le vert : « в театре », « в библиотеке ». Bleu = on y va, vert = on y est !"]},
   {"by":"masha","fr":["Pour inviter : « Давай пойдём… ! » (allons…). Pour accepter : « С удовольствием ! ». Pour refuser gentiment : « Извини, я не могу. »","« Свободен » (homme) / « свободна » (femme) = libre : encore le genre !"]}],
 explore={"type":"case","speaker":"luka","case":"accs","frame":"Давай пойдём в ___!","frameFr":"Allons ___ !","color":"#3a86ff","hintFr":"Mets chaque lieu après « в » (on y va) et regarde bien la fin du mot.","words":[
   {"tile":"театр","fr":"au théâtre","phraseFr":"Allons au théâtre !"},{"tile":"кино","fr":"au cinéma","phraseFr":"Allons au cinéma !"},
   {"tile":"библиотека","fr":"à la bibliothèque","phraseFr":"Allons à la bibliothèque !"},{"tile":"парк","fr":"au parc","phraseFr":"Allons au parc !"}]},
 tasks=[{"type":"pick","fr":"Propose d'aller à la bibliothèque.","answer":"библиотека"},{"type":"pick","fr":"Propose d'aller au cinéma.","answer":"кино"}],
 cando=["inviter quelqu'un","accepter une invitation","fixer un rendez-vous"],
 unlocks=[{"case":"accs","gender":"femn","from":"библиотека","to":"библиотеку"}],
 glossary=G({"свободна":"libre (femme)","свободен":"libre (homme)","субботу":"samedi (в субботу)","субботы":"samedi (до субботы = à samedi)","пойдём":"allons","пойдем":"allons","театр":"théâtre","театре":"théâtre (après в, on y est)","с":"avec","удовольствием":"plaisir (с удовольствием = avec plaisir)","там":"là-bas","идёт":"se joue, passe","идет":"se joue, passe","евгений":"Eugène","онегин":"Onéguine","опера":"opéra","отлично":"parfait","во":"à (во сколько = à quelle heure)","сколько":"combien","семь":"sept","куплю":"(j')achèterai","билеты":"billets","до":"jusqu'à","кино":"cinéma","библиотеку":"bibliothèque (vers)","библиотека":"bibliothèque","парк":"parc"}),
 combos=[C("Давай пойдём в кино в субботу!","Allons au cinéma samedi !",["театре"],["давай пойдём в кино в субботу","давай в субботу пойдём в кино","в субботу давай пойдём в кино"]),
   C("Ты свободна завтра?","Tu es libre demain ? (à une femme)",["субботу"],["ты свободна завтра","завтра ты свободна"]),
   C("С удовольствием! Я куплю пиццу.","Avec plaisir ! J'achèterai une pizza.",["пицца"])])

# ---------------- 16. L'hiver arrive ----------------
lesson(id="16-hiver", order=16, titleFr="L'hiver arrive", titleRu="Зима", emoji="❄️",
 sceneFr="Novembre à Saint-Pétersbourg. En sortant du théâtre, Luka découvre la neige… et le froid russe.",
 dialogue=[D("luka","Ой, как холодно!","Oh, qu'il fait froid !"),
   D("masha","Да, сегодня минус десять.","Oui, aujourd'hui il fait moins dix."),
   D("luka","Минус десять? А во Франции сейчас тепло.","Moins dix ? Et en France, en ce moment, il fait doux."),
   D("masha","Где твоя шапка?","Où est ton bonnet ?"),
   D("luka","У меня нет шапки.","Je n'ai pas de bonnet."),
   D("masha","Завтра надо купить шапку!","Demain, il faut acheter un bonnet !"),
   D("luka","Хорошо. А ты любишь зиму?","D'accord. Et toi, tu aimes l'hiver ?"),
   D("masha","Очень люблю! Зимой красиво.","J'adore ! En hiver, c'est beau.")],
 phrases=[
   ph("cold","luka","Ой, как холодно!","Oh, qu'il fait froid !","« Холодно » = il fait froid. Pas de « il fait » en russe : un seul mot suffit !","холодно",["тепло","шапка"],None,"Il fait froid : « холодно ». « Тепло » veut dire « il fait doux »."),
   ph("minus","masha","Да, сегодня минус десять.","Oui, aujourd'hui il fait moins dix.","« Минус десять » = moins dix. « Сегодня » = aujourd'hui.","десять",["шапку","зиму"]),
   ph("warm","luka","А во Франции сейчас тепло.","Et en France, en ce moment, il fait doux.","« Во Франции » = en France (« во » devant certains sons, pour que ce soit plus facile à dire). « Тепло » = il fait doux, chaud.","франции",["франция","шапки"],["а во франции сейчас тепло","а сейчас во франции тепло"],"Pour dire où : « во Франции ». Tu connais « из Франции » depuis la première leçon !"),
   ph("hat","masha","Где твоя шапка?","Où est ton bonnet ?","« Твоя » = ta (« твой » = ton). « Шапка » = bonnet.","твоя",["твой","моя"],["где твоя шапка"],"« Шапка » est féminin (-а) : « твоя ». « Твой », c'est pour un mot masculin."),
   ph("nohat","luka","У меня нет шапки.","Je n'ai pas de bonnet.","« У меня нет… » = je n'ai pas de… Le mot change : « шапка » → « нет шапки ». Retiens-le pour l'instant.","нет",["есть","надо"],None,"« У меня нет » = je n'ai pas. « У меня есть », ce serait « j'ai »."),
   ph("buy","masha","Завтра надо купить шапку!","Demain, il faut acheter un bonnet !","« Надо » = il faut. « Купить » = acheter. Le bonnet est ce qu'on achète : « шапку » (-у).","шапку",["шапка","шапки"],["завтра надо купить шапку","надо купить шапку завтра"],"On achète le bonnet : c'est le bleu, « шапку » (-у), comme après « хочу »."),
   ph("winter","luka","А ты любишь зиму?","Et toi, tu aimes l'hiver ?","« Зима » = hiver → « люблю зиму ». Encore le bleu !","зиму",["зима","зимой"],["а ты любишь зиму"],"Après « любишь », « зима » → « зиму » (-у)."),
   ph("beautiful","masha","Очень люблю! Зимой красиво.","J'adore ! En hiver, c'est beau.","« Зимой » = en hiver (comme « утром », « вечером »). « Красиво » = c'est beau.","красиво",["холодно","десять"])],
 parts=[{"titleFr":"Le froid","steps":[SC,EX,I(0),B(["cold","minus"]),B(["warm","hat"],["cold"])]},
   {"titleFr":"Un bonnet !","steps":[W(["cold","minus","hat"]),B(["nohat","buy"],["hat","warm"]),B(["winter","beautiful"],["buy"]),I(1)]},
   {"titleFr":"Joue la scène","steps":FIN}],
 insights=[{"by":"masha","fr":["Pour la météo, un seul mot suffit : « холодно » (il fait froid), « тепло » (il fait doux), « жарко » (il fait chaud).","Et pour le passé : « было холодно » (il faisait froid). Pour le futur : « будет холодно »."]},
   {"by":"masha","fr":["Bravo, tu as fait un vrai tour de la vie en Russie : te présenter, commander, demander ton chemin, faire des courses, parler de ta famille, de ta journée, de tes projets…","Et tu as vu que les phrases se construisent comme un puzzle : tu prends des morceaux que tu connais, et tu dis quelque chose de nouveau !"]}],
 explore={"type":"plain","speaker":"luka","frame":"Сегодня ___.","frameFr":"Aujourd'hui, il fait ___.","color":"#5c677d","hintFr":"Mets chaque mot dans la phrase et écoute.","words":[
   {"tile":"холодно","fr":"froid","phraseFr":"Aujourd'hui, il fait froid."},{"tile":"тепло","fr":"doux","phraseFr":"Aujourd'hui, il fait doux."},
   {"tile":"жарко","fr":"chaud","phraseFr":"Aujourd'hui, il fait chaud."},{"tile":"красиво","fr":"beau (c'est beau)","phraseFr":"Aujourd'hui, c'est beau."}]},
 tasks=[{"type":"pick","fr":"Dis qu'il fait chaud aujourd'hui.","answer":"жарко"},{"type":"pick","fr":"Dis qu'il fait froid aujourd'hui.","answer":"холодно"}],
 cando=["parler de la météo","dire « il faut »","dire « je n'ai pas de… »"],
 unlocks=[{"case":"accs","gender":"femn","from":"зима","to":"зиму"}],
 glossary=G({"ой":"oh, aïe","холодно":"il fait froid","тепло":"il fait doux","минус":"moins","десять":"dix","во":"en, dans (devant certains sons)","франции":"France","франция":"France","сейчас":"maintenant","твоя":"ta","твой":"ton","шапка":"bonnet","шапки":"bonnet (après нет)","шапку":"bonnet (après купить)","надо":"il faut","купить":"acheter","любишь":"(tu) aimes","зиму":"hiver (après люблю)","зима":"hiver","зимой":"en hiver","люблю":"(j')aime","красиво":"c'est beau","жарко":"il fait chaud"}),
 combos=[C("Вчера было холодно.","Hier, il faisait froid.",["тепло"],["вчера было холодно","было холодно вчера"]),
   C("Где твоя собака?","Où est ton chien ?",["моя"]),
   C("Завтра надо купить билеты.","Demain, il faut acheter les billets.",["куплю"],["завтра надо купить билеты","надо купить билеты завтра"]),
   C("Зимой холодно, но красиво.","En hiver, il fait froid, mais c'est beau.",["тепло"]) ])
print("ok")
