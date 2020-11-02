import numpy as np
import pandas as pd
import math
import json

# считает среднюю оценку пользователя оценённых фильмов
def avgRating(row):
    rated, ratings = 0, 0
    for film in range(numberOfFilms):
        if row.iat[0, film] != -1:
            rated += 1
            ratings += row.iat[0, film]
    return round(ratings / rated, 3)


# считает значение sim двух пользователей
def calculateSim(user1, user2):
    uvSum, u2Sum, v2Sum = 0, 0, 0
    for i in range(numberOfFilms):
        if (user1.iat[0, i] != -1) and (user2.iat[0, i] != -1):
            uvSum += user1.iat[0, i] * user2.iat[0, i]
            u2Sum += user1.iat[0, i] ** 2
            v2Sum += user2.iat[0, i] ** 2

    return round(uvSum / (round(math.sqrt(u2Sum) * math.sqrt(v2Sum), 3)), 3)

# создаёт list из индексов непросмотренных фильмов
def findNotRated(variant):
    notRated = []
    for j in range(numberOfFilms):
        if data.iat[variant - 1, j] == -1:
            notRated.append(j)
    return notRated

# создаёт list из sim
def findSims(data, myUser):
    sims = []
    notRated = findNotRated(variant)
    for i in range(1, numberOfUsers + 1):
        if i == variant:
            sims.append(0)
        else:
            sims.append(calculateSim(data.loc[data.index == myUser], data.loc[data.index == 'User ' + str(i)]))

    # зануляем sim для пользователей у которых не оценён хотя бы один фильм из нужных нам
    for i in range(numberOfUsers):
        for j in notRated:
            if data.iat[i, j] == -1:
                sims[i] = 0
    return sims

# вычисляет оценку фильма на основе оценок схожих пользователей
def makeRate(filmIndex, k, maxSims, sims):
    ru = avgRating(data.loc[data.index == myUser])
    sumUp, sumDown = 0, 0

    for i in range(k):
        sumUp += sims[maxSims[i]] * (
                data.iat[maxSims[i], filmIndex] - avgRating(data.loc[data.index == 'User ' + str(maxSims[i] + 1)]))
        sumDown += abs(sims[maxSims[i]])

    return float(format(round(ru + round(sumUp / sumDown, 3), 3), '.3f'))

# для задания 1
def rateFilms(data):
    k = 4
    sims = findSims(data, myUser)
    notRated = findNotRated(variant)
    # находим индексы k пользователей с самыми большими значениями sim
    maxSims = np.array(sims).argsort()[-k:]

    rated = {}
    for film in notRated:
        rated["movie " + str(film + 1)] = makeRate(film, k, maxSims, sims)

    return rated

# коэффициент просмотра фильма на выходных
def onWeekend(maxSims, film):
    onWeekend = 0
    for user in maxSims:
        if context_day.iat[user, film] == " Sat" or context_day.iat[user, film] == " Sun":
            onWeekend += 1
    return round(onWeekend / 4 * 100 / 3, 3)

# коэффициент просмотра фильма на дома
def atHome(maxSims, film):
    atHome = 0
    for user in maxSims:
        if context_place.iat[user, film] == " h":
            atHome += 1
    return round(atHome / 4 * 100 / 3, 3)

# для задания 2
def recommendation(data):
    k = 4
    notRated = findNotRated(variant)
    sims = findSims(data, myUser)
    maxSims = np.array(sims).argsort()[-k:]

    rated = {}
    for film in notRated:
        rated[film] = round(makeRate(film, k, maxSims, sims) / 5 * 100 / 3, 3) + onWeekend(maxSims, film) + atHome(
            maxSims, film)

    for key in rated.keys():
        if rated.get(key) == max(rated.values()):
            d = {"movie " + str(key + 1): makeRate(key, k, maxSims, sims)}
            return d


data = pd.read_csv('data.csv', index_col=0).copy()
context_day = pd.read_csv('context_day.csv', index_col=0)
context_place = pd.read_csv('context_place.csv', index_col=0)

variant = 24
myUser = 'User ' + str(variant)

numberOfUsers = data.shape[0]
numberOfFilms = data.shape[1]

# задание 1
res1 = rateFilms(data)
# задание 2. В этом задании выбор делается из не просмотренных фильмов моего варианта на основе данных
# наиболее близких пользователей по sim. Оценка, место и время просмотра - учитываются равнозначно для выбора фильма
res2 = recommendation(data)

result = {"user": variant, "1": res1, "2": res2}
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4)
