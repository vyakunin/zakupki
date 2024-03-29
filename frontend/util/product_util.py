#!/usr/bin/python2.5
# encoding: utf-8
"""
product_util.py

Copyright (c) Sergey Babenko and Vladimir Yakunin 2011.
All rights reserved.
"""

class ProductCategory(object):
  CATEGORIES = []
  CATEGORY_BY_CODE = {}

  def __init__(self, code, name):
    self.code = code
    self.name = name

  @staticmethod
  def ByCode(code):
    return ProductCategory.CATEGORY_BY_CODE.get(code[:2])

  @staticmethod
  def NameByCode(code):
    cat = ProductCategory.CATEGORY_BY_CODE.get(code[:2])
    if cat is not None:
      return cat.name
    else:
      return 'Другое'

ProductCategory.CATEGORIES = [
  ProductCategory('01', 'Сельское хозяйство,  охота и связанная с этим деятельность по предоставлению услуг'),
  ProductCategory('02', 'Лесное хозяйство, лесозаготовки и предоставление услуг в этих областях'),
  ProductCategory('05', 'Рыболовство, рыбоводство и предоставление услуг в этих областях'),
  ProductCategory('10', 'Добыча каменного угля и лигнита; добыча торфа'),
  ProductCategory('11', 'Добыча сырой   нефти   и  природного  газа;  деятельность  по предоставлению услуг, связанных с добычей нефти и газа, кроме  изыскательских работ'),
  ProductCategory('12', 'Добыча радиоактивных руд'),
  ProductCategory('13', 'Добыча металлических руд'),
  ProductCategory('14', 'Деятельность горнодобывающая и по разработке карьеров прочая'),
  ProductCategory('15', 'Производство пищевых продуктов и напитков'),
  ProductCategory('16', 'Производство табака и табачных изделий'),
  ProductCategory('17', 'Производство текстильных изделий'),
  ProductCategory('18', 'Производство одежды; выделка и крашение меха'),
  ProductCategory('19', 'Дубление и выделка кожи; производство чемоданов, сумок, шорно-седельных изделий и обуви'),
  ProductCategory('20', 'Производство древесины, деревянных и пробковых изделий, кроме мебели; производство изделий из соломки и плетенки'),
  ProductCategory('21', 'Целлюлозно-бумажное производство и производство изделий из бумаги и картона'),
  ProductCategory('22', 'Издательское дело, полиграфическая промышленность и воспроизведение печатных материалов'),
  ProductCategory('23', 'Коксохимическое производство, производство продукции нефтеперегонки, радиоактивных веществ и продукции на их основе'),
  ProductCategory('24', 'Производство продукции химического синтеза'),
  ProductCategory('25', 'Производство резиновых и пластмассовых изделий'),
  ProductCategory('26', 'Производство неметаллических минеральных продуктов прочих'),
  ProductCategory('27', 'Производство металлургическое'),
  ProductCategory('28', 'Производство металлообрабатывающее, кроме производства машин и оборудования'),
  ProductCategory('29', 'Производство машин и оборудования, не включенных в другие группировки'),
  ProductCategory('30', 'Производство канцелярских, бухгалтерских и электронно-вычислительных машин'),
  ProductCategory('31', 'Производство электрических машин и аппаратуры, не включенных в другие группировки'),
  ProductCategory('32', 'Производство оборудования и аппаратуры для радио, телевидения и связи'),
  ProductCategory('33', 'Производство медицинских приборов, точных и оптических инструментов, часов и приборов времени прочих'),
  ProductCategory('34', 'Производство автомобилей, прицепов и полуприцепов'),
  ProductCategory('35', 'Производство транспортных средств прочих'),
  ProductCategory('36', 'Производство мебели; производство готовых изделий, не включенных в другие группировки'),
  ProductCategory('37', 'Сбор и вторичная переработка отходов и лома в форму, пригодную для использования в качестве нового сырья'),
  ProductCategory('40', 'Снабжение электроэнергией, газом, паром и горячей водой'),
  ProductCategory('41', 'Сбор, очистка и распределение воды'),
  ProductCategory('45', 'Строительство'),
  ProductCategory('50', 'Продажа, техническое обслуживание и ремонт автомобилей и мотоциклов; розничная продажа горючего для транспортных средств с двигателями внутреннего сгорания'),
  ProductCategory('51', 'Оптовая и комиссионная торговля, кроме торговли автомобилями и мотоциклами'),
  ProductCategory('52', 'Розничная торговля, кроме торговли автомобилями и мотоциклами; ремонт бытовых товаров и предметов личного пользования'),
  ProductCategory('55', 'Деятельность гостиниц и ресторанов'),
  ProductCategory('60', 'Деятельность сухопутного транспорта'),
  ProductCategory('61', 'Деятельность водного транспорта'),
  ProductCategory('62', 'Деятельность воздушного транспорта'),
  ProductCategory('63', 'Деятельность транспортная вспомогательная и дополнительная; деятельность бюро путешествий и экскурсий'),
  ProductCategory('64', 'Связь'),
  ProductCategory('65', 'Финансовое посредничество, кроме страхования и пенсионного обеспечения'),
  ProductCategory('66', 'Страхование и пенсионное обеспечение, кроме обязательного социального страхования'),
  ProductCategory('67', 'Деятельность, являющаяся вспомогательной по отношению к финансовому посредничеству'),
  ProductCategory('70', 'Деятельность по операциям с недвижимым имуществом'),
  ProductCategory('71', 'Лизинг или аренда машин и оборудования без оператора; аренда бытовых товаров и предметов личного пользования'),
  ProductCategory('72', 'Деятельность, связанная с компьютерами'),
  ProductCategory('73', 'Деятельность в области исследований и разработок'),
  ProductCategory('74', 'Деятельность коммерческая и техническая прочая'),
  ProductCategory('75', 'Деятельность в области государственного управления и обороны; деятельность в области обязательного социального страхования'),
  ProductCategory('80', 'Деятельность в области образования'),
  ProductCategory('85', 'Деятельность в области здравоохранения и оказания социальных услуг'),
  ProductCategory('90', 'Деятельность по канализации и удалению отходов, санитарной обработке и аналогичные виды деятельности'),
  ProductCategory('91', 'Деятельность членских организаций'),
  ProductCategory('92', 'Деятельность в области организации распространения информации, культуры, спорта, отдыха и развлечений'),
  ProductCategory('93', 'Деятельность в области жилищно-коммунального хозяйства'),
  ProductCategory('94', 'Деятельность в обрабатывающей промышленности, осуществляемая по частным заказам за вознаграждение или на договорной основе'),
  ProductCategory('95', 'Деятельность частных домашних хозяйств с наемным обслуживанием'),
  ProductCategory('96', 'Деятельность частных домашних хозяйств по производству товаров для собственного потребления'),
  ProductCategory('97', 'Деятельность частных домашних хозяйств по предоставлению услуг для собственного пользования'),
  ProductCategory('99', 'Деятельность экстерриториальных организаций и органов'),
  
  ProductCategory('A', 'Продукция и услуги сельского хозяйства, охоты и лесоводства'),
  ProductCategory('B', 'Продукция и услуги рыболовства'),
  ProductCategory('C', 'Продукция и услуги горнодобывающей промышленности и разработки карьеров'),
  ProductCategory('D', 'Продукция и услуги обрабатывающей промышленности'),
  ProductCategory('E', 'Электроэнергия, газ и водоснабжение'),
  #TODO(vyakunin): Move all these to 45 when uploading data.
  ProductCategory('F', 'Продукция и услуги строительства'),
  ProductCategory('G', 'Услуги в оптовой и розничной торговле; услуги по техническому обслуживанию и ремонту автомобилей, бытовых приборов и предметов личного пользования'),
  ProductCategory('H', 'Услуги гостиниц и ресторанов'),
  ProductCategory('I', 'Услуги транспорта, складского хозяйства и связи'),
  ProductCategory('J', 'Услуги по финансовому посредничеству'),
  ProductCategory('K', 'Услуги, связанные с недвижимым имуществом, арендой, исследовательской и коммерческой деятельностью'),
  ProductCategory('L', 'Услуги в области государственного управления и обороны; услуги обязательного социального страхования'),
  ProductCategory('M', 'Услуги в области образования'),
  ProductCategory('N', 'Услуги в области здравоохранения и в социальной области'),
  ProductCategory('O', 'Услуги коммунальные, социальные и персональные прочие'),
  ProductCategory('P', 'Услуги по ведению частных домашних хозяйств с наемным обслуживанием'),
  ProductCategory('Q', 'Услуги, предоставляемые экстерриториальными организациями и органами'),
  
  # We also have '39', '54' and '86' in our data, but there's no such OKDP.
]

_categoryByCode = {}
for category in ProductCategory.CATEGORIES:
  _categoryByCode[category.code] = category
ProductCategory.CATEGORY_BY_CODE = _categoryByCode
