from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.deep_linking import get_start_link
import asyncio


from tgbot.filters.is_admin import IsSubscriber
from tgbot.handlers.users.start import ru_language, bot_start, suitable_menu

from tgbot.keyboards.default.phone import phonenumber, phonenumber_uz
from tgbot.states.users import Custom, Location


async def about_handler(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    if await ru_language(message):
        text = """
Салаам Травел 2017 йилдан буён туризм соҳасида фаолият юритиб, асосий йўналиш сифатида Умра сафарларини ташкил этиш билан шуғулланиб келмоқда. Бугунги кунгача 30 000 га яқин умрачиларнинг чиройли ҳолда Умра сафарларига бориб келишларига хизмат қилган.

Умрачиларни асосий йўналишда тўғридан-тўғри рейслар билан, шунингдек, транзит йўналишлар орқали сафарга олиб бориб келади. Ҳозирги вақтда Салаам Травел Тошкент, Самарқанд, Наманган, Термиз ва Бухоро шаҳарларидан учувчи ишончли авиакомпаниялар, жумладан Қанот Шарқ, Ўзбекистон Ҳаво Йўллари, Аир Арабия, Флай Дубай, Жазира ва Сентрум авиакомпаниялари билан ҳамкорлик қилади.

Компаниянинг Ўзбекистон бўйлаб 30 га яқин филиали фаолият юритмоқда. Улар Тошкент шаҳри ва вилояти, Андижон, Наманган, Марғилон, Қўқон, Сирдарё, Жиззах, Самарқанд, Ургут, Бухоро, Қарши ва Денов шаҳарларида жойлашган. Сафарларни чиройли ташкил этиш мақсадида Салаам Травел доимий равишда Макка ва Мадинадаги қулай меҳмонхоналар билан ҳамкорлик қилади ва умрачиларга энг яхши хизматни тақдим этади.

Фирма номидан хизмат кўрсатувчи элликбошилар тажрибали ва малакали бўлиб, барчаси аҳли илм кишилардир. Улар Саудия, Азҳар ва Ўзбекистон мадрасаларида таълим олган, масжидларда имомлик қилган домлалар ва Ҳофизи Қуръон қорилардан иборатдир.

Умра амалини бажаришни ният қилганларга Аллоҳнинг раҳмати ва мағфиратлари ёр бўлсин! Бизларни сизларга кўмакчи қилиб қўйган Зотга чексиз ҳамду санолар бўлсин!

Ҳурмат билан, Салаам Травел жамоаси."""
    else:
        text = """
Salaam Travel 2017-yildan buyon turizm sohasida faoliyat yuritib, asosan Umra safarlarini tashkil etishga ixtisoslashgan. Shu kungacha 30 000 ga yaqin umrachilarning chiroyli va qulay sharoitlarda Umra safarini amalga oshirishlariga xizmat qilgan.

Umrachilarni to'g'ridan-to'g'ri reyslar va tranzit yo'nalishlar orqali olib boradi. Hozirda Salaam Travel Toshkent, Samarqand, Namangan, Termiz, Buxoro kabi shaharlarimizdan uchuvchi ishonchli aviakompaniyalar, jumladan Qanot Sharq, O'zbekiston Havo Yo'llari, Air Arabia, Flydubai, Jazira va Centrum aviakompaniyalari bilan hamkorlik qilib kelmoqda.

Bugungi kunda O'zbekiston bo'ylab 30 ga yaqin filiallarimiz faoliyat yuritmoqda. Ular orasida Toshkent shahri va viloyati, Andijon, Namangan, Marg'ilon, Qo'qon, Sirdaryo, Jizzax, Samarqand, Urgut, Buxoro, Qarshi va Denov kabi shaharlarda joylashgan filiallarimiz bor. Safarlarni chiroyli va samarali tashkil etish maqsadida, kompaniyamiz doimiy ravishda Makka va Madinadagi qulay mehmonxonalar bilan hamkorlik qiladi va umrachilarga eng qulay sharoitlarni tanlab xizmat ko'rsatadi.

Firma nomidan xizmat qiluvchi ellikboshilarimiz tajribali, malakali va ahli ilm kishilar bo'lib, ular Saudiya Arabistoni, Azhar va O'zbekiston madrasalarida ta'lim olgan, masjidlarda imomlik qilgan domlalar, hofizi Qur'on qorilardan iborat.

Umra amalini bajarishni niyat qilganlarga mehribon va rahmli Allohning o‘zi kuch-quvvat ato qilsin! Bizlarni sizlarga ko‘makchi qilib qo‘ygan Zotga cheksiz hamd-u sanolar bo‘lsin!

Hurmat bilan, Salaam Travel jamoasi."""
    await message.answer(text)


cities = [
    "Sergeli, Qumariq",
    "Toshkent",
    "Andijon",
    "Namangan",
    "Qo’qon",
    "Jizzax",
    "Surxondaryo Viloyati",
    "Surxondaryo Viloyati 2",
    "Buxoro",
    "Navoiy",
    "Samarqand",
    "Qo’qon Beshariq",
    "Surxondaryo viloyati - 3"
]

cities_cyrillic = [
    "Сергели, Кумарик",
    "Ташкент",
    "Андижон",
    "Наманган",
    "Қўқон",
    "Жиззах",
    "Сурхандарё вилояти",
    "Сурхандарё вилояти 2",
    "Бухоро",
    "Навоий",
    "Самарқанд",
    "Қўқон Бешариқ",
    "Сурхандарё вилояти - 3"
]

city_translations = {
    "Сергели, Кумарик": "Sergeli, Qumariq",
    "Ташкент": "Toshkent",
    "Андижон": "Andijon",
    "Наманган": "Namangan",
    "Қўқон": "Qo’qon",
    "Жиззах": "Jizzax",
    "Сурхандарё вилояти": "Surxondaryo Viloyati",
    "Сурхандарё вилояти 2": "Surxondaryo Viloyati 2",
    "Бухоро": "Buxoro",
    "Навоий": "Navoiy",
    "Самарқанд": "Samarqand",
    "Қўқон Бешариқ": "Qo’qon Beshariq",
    "Сурхандарё вилояти - 3": "Surxondaryo viloyati - 3"
}

cities_and_locations = [
        ("Sergeli, Qumariq", (41.323951, 69.230299)),
        ("Toshkent", (38.279357, 67.896133)),
        ("Andijon", (41.005471, 71.688572)),
        ("Namangan", (40.122173, 67.828882)),
        ("Qo’qon", (39.787849, 64.43103)),
        ("Jizzax", (40.54764, 70.957556)),
        ("Surxondaryo Viloyati", (41.243647, 69.252445)),
        ("Surxondaryo Viloyati 2", (38.274631, 67.892769)),
        ("Buxoro", (40.795544, 72.332632)),
        ("Navoiy", (40.089409, 65.387499)),
        ("Samarqand", (39.659715, 67.00969)),
        ("Qo’qon Beshariq", (40.436733, 70.60278)),
        ("Surxondaryo viloyati - 3", (37.24369, 67.272627))
    ]


def get_latin_version(city_cyrillic):
    return city_translations.get(city_cyrillic)


async def send_location_handler(message: types.Message):
    db = message.bot.get("db")
    _ = message.bot.get("lang")

    if await ru_language(message):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for city in cities_cyrillic:
            keyboard.add(KeyboardButton(text=city))
        keyboard.add(KeyboardButton(text="Асосий меню"))
        await message.answer("Илтимос, геолокациясини олиш учун шаҳарни танланг", reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for city in cities:
            keyboard.add(KeyboardButton(text=city))
        keyboard.add(KeyboardButton(text="Asosiy menyu"))
        await message.answer("Iltimos, geolokatsiyasini olish uchun shaharni tanlang", reply_markup=keyboard)
    await Location.City.set()


# Location.City
async def send_location_handler2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    _ = message.bot.get("lang")
    selected_city = message.text

    if await ru_language(message):
        city_latin = get_latin_version(selected_city)
        for city, location in cities_and_locations:
            if city == city_latin:
                latitude, longitude = location
                await message.bot.send_location(message.from_user.id, latitude, longitude)
                break
    else:
        for city, location in cities_and_locations:
            if city == selected_city:
                latitude, longitude = location
                await message.bot.send_location(message.from_user.id, latitude, longitude)
                break


def register_about(dp: Dispatcher):
    dp.register_message_handler(about_handler, IsSubscriber(), text=["ℹ️ Биз хакимизда", "ℹ️ Biz haqimizda"])

    dp.register_message_handler(send_location_handler, IsSubscriber(), text=["📍 Геолокация", "📍 Geolokaziya"])

    dp.register_message_handler(send_location_handler2, IsSubscriber(), state=Location.City)



