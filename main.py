from twitterscraper import query_tweets
import datetime as dt
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions, EmotionOptions

# =====
# SETTINGS AND FEATURES
# =====
enrichment_natural_language_understanding = True
sentiment_analysis_enabled = True
emotion_analysis_enabled = False

if (enrichment_natural_language_understanding):
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2018-11-16',
        iam_apikey='X4rbi8vwZmKpXfowaS3GAsA7vdy17Qh7km5D6EzKLHL2',
        url='https://gateway-wdc.watsonplatform.net/natural-language-understanding/api'
        # iam_apikey='pVXBdcOdZtldEtozvAEm68AnZb1x-bz8xrRIAmiMm7u9',
        # url='https://gateway.watsonplatform.net/natural-language-understanding/api'
    )
    if (sentiment_analysis_enabled):
        sentiment = SentimentOptions()
    else:
        sentiment = None
    if (emotion_analysis_enabled):
        emotion = EmotionOptions()
    else:
        emotion = None
    features = Features(sentiment=sentiment, emotion=emotion)


def parseDate(date):
    if date == 'default' or date == 'beggining':
        return dt.date(2006, 3, 21)
    elif date == 'yesterday':
        return dt.date.today() - dt.timedelta(days=1)
    elif date == 'today':
        return dt.date.today()
    else:
        x = date.split('-')
        return dt.date(int(x[0]), int(x[1]), int(x[2]))


def getNLU(tweet):
    if (sentiment_analysis_enabled):
        try:
            response = natural_language_understanding.analyze(text=tweet.text, features=features).get_result()
            tweet.sentiment = response['sentiment']['document']['score']
        except:
            pass
    else:
        tweet.sentiment = None
    if (emotion_analysis_enabled):
        try:
            if (emotion_analysis_enabled):
                for emotion in response['emotion']['document']['emotion']:
                    setattr(tweet, emotion, response['emotion']['document']['emotion'][emotion])
        except KeyError as err:
            tweet.sentiment = 0
            print(err)
            print(json.dumps(response, indent=2))


def genHeader(obj):
    j = 0
    header = ''
    for attr in dir(obj):
        if not attr.startswith('__') and attr not in excluded:
            if j == 0:
                header += attr
            else:
                header += ',' + attr
            j += 1
    if header != None: return header


if __name__ == '__main__':
    excluded = ['from_html', 'from_soup', 'html']

    # print the retrieved tweets to the screen:
    begindate = parseDate('2019-10-17')
    interdate = begindate + dt.timedelta(days=14)
    enddate = parseDate('today')

    fetchQuery = '#LaMarchaMasGrandeDeChile3'
    # #quechiledecida OR #huelgageneral OR #asambleaconstituyenteonada OR congreso constituyente OR plaza de la dignidad

    # done
    # '#estadodeexcepcion OR #evasionmasivatodoeldia OR #noestamosenguerra OR #chadwickasesino'
    # '#nomasafp OR #asambleaconstituyente'
    # '#chilenoestaenguerra OR #nuevaconstitucionparachile OR #chilesecanso'
    # '#todossomoschile OR #fuerachadwick OR #chileenllamas OR #chilesinmiedo OR #chileencrisis'
    # '#chileresiste OR #chilequierepaz OR #chileestadespertando OR #chileprotests'
    # '#chilesomostodos OR #ChileNoSeRinde OR #carcelparapiñera OR #renunciachadwick'
    # '#piñerarenuncia'
    # '#noparemoschile OR #recuperemoschile OR #evadiresluchar'
    # '#estopasaenchile OR #cambiodegabinete OR #HabraConsecuencias'
    # '#evasionmasiva OR #evasionmasivatodoeldia OR #DestitucionaPiñera OR #ChileDespierto'
    # '#LaMarchaMasGrandeDeChile2 OR #ChilenEnRebeldia OR #PineraDictador OR #PazParaChile OR #EstoNoHaTerminado'
    # '#LaMarchaMasGrandeDeTodas OR #LaMarchaMasGrandeDeTodas2 OR #ChileViolaLosDerechosHumanos'
    # '#LosMilicosNoSonTusAmigos OR #ChileDesperto OR #RenunciaPiñera OR #ChileQuiereCambios'

    while (interdate <= enddate):
        file = open('./out/' + fetchQuery[:30].replace(" ", "_") + '_' + str(begindate) + '.csv', 'w')
        row = 0

        for tweet in query_tweets(fetchQuery, begindate=begindate, enddate=interdate, poolsize=14):
            line = ''
            i = 0

            # clean the tweet properly for the csv file and perform sentiment analysis
            tweet.text = tweet.text.replace("\n", " ").replace(",", ".")
            tweet.fullname = tweet.fullname.replace("\n", " ").replace(",", ".")
            getNLU(tweet)
            # generate a row and write it to the csv. iterates over each attribute, so you can add custom attributes
            for attr in dir(tweet):
                if not attr.startswith('__') and attr not in excluded:
                    if i == 0:
                        line += str(getattr(tweet, attr))
                    else:
                        line += ',' + str(getattr(tweet, attr))
                    i += 1
            if row == 0: file.write(genHeader(tweet) + '\n')
            if line != '' and line != None: file.write(line + '\n')
            row += 1

        file.close()

        begindate = interdate + dt.timedelta(days=1)
        interdate = interdate + dt.timedelta(days=30)
        # print(begindate, interdate)
    exit()
