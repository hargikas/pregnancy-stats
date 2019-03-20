import datetime

from lunardate import LunarDate

pinyin = {
    '甲': 'jiă',
    '乙': 'yĭ',
    '丙': 'bĭng',
    '丁': 'dīng',
    '戊': 'wù',
    '己': 'jĭ',
    '庚': 'gēng',
    '辛': 'xīn',
    '壬': 'rén',
    '癸': 'gŭi',

    '子': 'zĭ',
    '丑': 'chŏu',
    '寅': 'yín',
    '卯': 'măo',
    '辰': 'chén',
    '巳': 'sì',
    '午': 'wŭ',
    '未': 'wèi',
    '申': 'shēn',
    '酉': 'yŏu',
    '戌': 'xū',
    '亥': 'hài'
}

animals = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake',
           'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Pig']
elements = ['Wood', 'Fire', 'Earth', 'Metal', 'Water']

celestial = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
terrestrial = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
aspects = ['yang', 'yin']


def calculate(year):
    BASE = 4
    year = int(year)
    cycle_year = year - BASE
    stem_number = cycle_year % 10
    stem_han = celestial[stem_number]
    stem_pinyin = pinyin[stem_han]
    element_number = stem_number // 2
    element = elements[element_number]
    branch_number = cycle_year % 12
    branch_han = terrestrial[branch_number]
    branch_pinyin = pinyin[branch_han]
    animal = animals[branch_number]
    aspect_number = cycle_year % 2
    aspect = aspects[aspect_number]
    index = cycle_year % 60 + 1
    return "{}{} ({}-{}, {} {}; {} - year {} of the cycle)".format(stem_han, branch_han, stem_pinyin, branch_pinyin, element, animal, aspect, index)


def calculate_dt(birthday):
    if isinstance(birthday, datetime.datetime):
        birthday = birthday.date()
    year = birthday.year
    chinese_new_year = LunarDate(year, 1, 1).toSolarDate()
    if chinese_new_year > birthday:
        year -= 1
    return calculate(year)


if __name__ == '__main__':
    current_year = datetime.datetime.now().year
    years = [1943, 1948, 1975, 1978, 1985, current_year]
    for year in years:
        print(calculate(year))
