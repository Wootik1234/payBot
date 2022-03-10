from aiogram.types import Message, ShippingOption, ShippingQuery, LabeledPrice, PreCheckoutQuery
from aiogram.types.message import ContentType

from messages import MESSAGES
from config import PToken, item_url
from main import dp, bot

PRICES = {
    LabeledPrice(label="Ноутбук", amount=10000),
    LabeledPrice(label="Прочная упаковка", amount=10000)
}

SUPER_SHIPPING = ShippingOption(
    id="superspeed",
    title="Супер быстрая!"
).add(LabeledPrice("Лично в руки!", 10000))

POST_SHIPPING = ShippingOption(
    id="post",
    title="Почта России"
)

POST_SHIPPING.add(LabeledPrice("Картонная коробка", 10000))
POST_SHIPPING.add(LabeledPrice("Срочное отправление!", 10000))

PICKUP_SHIPPING = ShippingOption(
    id="pickup",
    title="Самовызов"
)
PICKUP_SHIPPING.add(LabeledPrice("Самовызов в Москве", 10000))


@dp.message_handler(commands=["start"])
async def start_cmd(message: Message):
    await message.answer(MESSAGES["start"])

@dp.message_handler(commands=["help"])
async def help_cmd(message: Message):
    await message.answer(MESSAGES["help"])

@dp.message_handler(commands=["terms"])
async def terms_cmd(message: Message):
    await message.answer(MESSAGES["terms"])


@dp.message_handler(commands=["buy"])
async def buy_process(message: Message):
    await bot.send_invoice(message.chat.id,
                           title=MESSAGES["tm_title"],
                           description=MESSAGES["tm_description"],
                           provider_token=PToken,
                           currency="rub",
                           photo_url=item_url,
                           photo_height=650,
                           photo_width=950,
                           need_email=True,
                           need_phone_number=True,
                           is_flexible=True,
                           prices=PRICES,
                           start_parameter="example",
                           payload="some_invoice"
                           )

@dp.shipping_query_handler(lambda q: True)
async def shipping_process(shipping_query: ShippingQuery):
    if shipping_query.shipping_address.country_code == "UK":
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message=MESSAGES["UK_error"]
        )
    shipping_option = [SUPER_SHIPPING]
    if shipping_query.shipping_address.country_code =="RU":
        shipping_option.append(POST_SHIPPING)
        if shipping_query.shipping_address.city =="Москва":
            shipping_option.append(PICKUP_SHIPPING)

    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        shipping_options=shipping_option
    )

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    await bot.send_message(
        message.chat.id,
        MESSAGES["successful_pay"].format(total_amount=message.successful_payment.total_amount,
                                          currency=message.successful_payment.currency)
    )


