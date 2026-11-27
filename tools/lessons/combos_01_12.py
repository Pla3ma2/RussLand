import json, pathlib
L=pathlib.Path(''+str(pathlib.Path(__file__).resolve().parents[2]/'content'/'levels')+'')
def C(ru, fr, extra, orders=None, note=""):
    d={"ru":ru,"fr":fr,"extra":extra}
    if orders: d["orders"]=orders
    if note: d["noteFr"]=note
    return d
COMBOS={
"01-rencontre":[
 C("Вы француз?","Vous êtes français ?",["из"]),
 C("Я студентка из Франции.","Je suis étudiante, je viens de France.",["студент"],["я студентка из франции","я из франции я студентка"]),
 C("Как вас зовут? Вы студент?","Comment vous appelez-vous ? Vous êtes étudiant ?",["меня"])],
"02-presenter":[
 C("Я врач. А вы?","Je suis médecin. Et vous ?",["меня"]),
 C("Я учительница из Франции.","Je suis professeure, je viens de France.",["учитель"]),
 C("Вы говорите по-французски?","Vous parlez français ?",["говорю"],["вы говорите по-французски","по-французски вы говорите","вы по-французски говорите"]),
 C("Я немного говорю по-русски.","Je parle un peu russe.",["говорите"],["я немного говорю по-русски","я говорю немного по-русски","я говорю по-русски немного"])],
"03-cafe":[
 C("Вы хотите кофе?","Vous voulez un café ?",["хочу"]),
 C("Здравствуйте! Я хочу чай и пиццу.","Bonjour ! Je voudrais du thé et une pizza.",["пицца"],["здравствуйте я хочу чай и пиццу","здравствуйте я хочу пиццу и чай"]),
 C("Я хочу воду, пожалуйста.","Je voudrais de l'eau, s'il vous plaît.",["вода"],["я хочу воду пожалуйста","пожалуйста я хочу воду"])],
"04-comprendre":[
 C("Извините, вы говорите по-французски?","Excusez-moi, vous parlez français ?",["понимаю"]),
 C("Мы не понимаем.","Nous ne comprenons pas.",["понимаю"]),
 C("Я говорю по-русски, но плохо.","Je parle russe, mais mal.",["хорошо"])],
"05-ville":[
 C("Привет! Ты в кафе?","Salut ! Tu es au café ?",["где"],["привет ты в кафе","привет в кафе ты"]),
 C("Банк там, направо.","La banque est là-bas, à droite.",["парке"]),
 C("Извините, где здесь гостиница?","Excusez-moi, où est l'hôtel, par ici ?",["гостинице"],["извините где здесь гостиница","извините где гостиница здесь"]),
 C("Я в Москве. Это далеко!","Je suis à Moscou. C'est loin !",["москва"])],
"06-magasin":[
 C("У вас есть чай?","Vous avez du thé ?",["вот"],["у вас есть чай","чай у вас есть","есть у вас чай"]),
 C("Сколько стоит пицца?","Combien coûte la pizza ?",["пиццу"],["сколько стоит пицца","пицца сколько стоит"]),
 C("Дайте, пожалуйста, воду и булочку.","Donnez-moi de l'eau et une brioche, s'il vous plaît.",["вода"],["дайте пожалуйста воду и булочку","дайте воду и булочку пожалуйста","пожалуйста дайте воду и булочку","дайте пожалуйста булочку и воду"])],
"07-amis":[
 C("Ты любишь кофе?","Tu aimes le café ?",["люблю"],["ты любишь кофе","кофе ты любишь"]),
 C("Я люблю чай, но не люблю кофе.","J'aime le thé, mais je n'aime pas le café.",["любишь"]),
 C("Ты живёшь в России?","Tu habites en Russie ?",["россия"],["ты живёшь в россии","в россии ты живёшь"]),
 C("Я живу в Париже, а ты?","J'habite à Paris, et toi ?",["париж"])],
"08-famille":[
 C("У тебя есть собака?","Tu as un chien ?",["меня"],["у тебя есть собака","собака у тебя есть","есть у тебя собака"]),
 C("Это мой брат. Его зовут Олег.","C'est mon frère. Il s'appelle Oleg.",["моя"]),
 C("Моя мама живёт в Лионе.","Ma mère habite à Lyon.",["мой"],["моя мама живёт в лионе","в лионе живёт моя мама"])],
"09-journee":[
 C("Мой папа работает в банке.","Mon père travaille dans une banque.",["работаю"],["мой папа работает в банке","в банке работает мой папа"]),
 C("Вечером я читаю книги.","Le soir, je lis des livres.",["утром"],["вечером я читаю книги","я читаю книги вечером"]),
 C("Ты работаешь в кафе?","Tu travailles dans un café ?",["работаю"],["ты работаешь в кафе","в кафе ты работаешь"])],
"10-restaurant":[
 C("Я буду пиццу и чай.","Je vais prendre une pizza et du thé.",["пицца"],["я буду пиццу и чай","я буду чай и пиццу"]),
 C("Вы будете кофе?","Vous prenez un café ?",["буду"]),
 C("Было очень интересно!","C'était très intéressant !",["счёт"])],
"11-transport":[
 C("Куда ты едешь?","Où est-ce que tu vas (en véhicule) ?",["где"],["куда ты едешь","ты куда едешь"]),
 C("Я иду в парк.","Je vais au parc.",["парке"],["я иду в парк","в парк я иду"],"Pour aller VERS : « в парк », sans -е."),
 C("Ты едешь на такси?","Tu y vas en taxi ?",["еду"],["ты едешь на такси","на такси ты едешь"])],
"12-weekend":[
 C("Вчера я был в театре.","Hier, j'étais au théâtre.",["музее"],["вчера я был в театре","я был в театре вчера"]),
 C("В субботу я работал.","Samedi, j'ai travaillé.",["работала"],["в субботу я работал","я работал в субботу"]),
 C("Вчера мы смотрели фильм дома.","Hier, on a regardé un film à la maison.",["один"],["вчера мы смотрели фильм дома","вчера мы смотрели дома фильм","мы смотрели фильм дома вчера"])],
}
for lid, combos in COMBOS.items():
    p=L/f"{lid}.json"; d=json.loads(p.read_text(encoding='utf-8'))
    d["combos"]=combos
    steps=d["parts"][1]["steps"]
    steps[:]=[s for s in steps if s["type"]!="combine"]
    steps.append({"type":"combine","phrases":[f"c{i+1}" for i in range(len(combos))]})
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
print("ok")
