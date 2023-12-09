import os
import re
import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy import create_engine

from config import Config

okt = Okt()


def sub_special(text):
    return re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣0-9a-zA-Z]', ' ', text)


def normalize(text):
    tokens = okt.morphs(text)
    return ' '.join(tokens)


def process_genre(text, preferred_genres):
    text = text.replace(', ', ' ')
    genres = text.split()
    for preferred_genre in preferred_genres:
        if preferred_genre in genres:
            text += f" {preferred_genre}"

    return text


def process_dataframe(dataframe, preferred_genres):
    dataframe = dataframe.fillna('')
    # dataframe["genre"] = dataframe["genre"].apply(sub_special)
    dataframe["genre"] = dataframe["genre"].apply(lambda genre: process_genre(genre, preferred_genres))
    dataframe["director"] = dataframe["director"].apply(sub_special)
    dataframe["actor"] = dataframe["actor"].apply(sub_special)
    dataframe["synopsis"] = dataframe["synopsis"].apply(sub_special)

    dataframe["synopsis"] = dataframe["synopsis"].apply(normalize)

    dataframe["text"] = dataframe["genre"] + " " + dataframe["director"] + " " + dataframe["synopsis"]

    return dataframe


def generate_tfidf_matrix(dataframe):
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(dataframe["text"])
    return tfidf_matrix, tfidf


def generate_cosine_sim(tfidf_matrix):
    return linear_kernel(tfidf_matrix, tfidf_matrix)


def generate_dataframe_from_db():
    db_url = Config.SQLALCHEMY_DATABASE_URI
    engine = create_engine(db_url)

    query = 'SELECT * FROM movie'

    database = pd.read_sql_query(query, engine)

    space = pd.DataFrame({'id': [' '],
                          'title': [' '],
                          'genre': [' '],
                          'director': [' '],
                          'actor': [' '],
                          'synopsis': [' '],
                          'img': [' ']})

    dataframe = pd.concat([space, database], ignore_index=True)

    return dataframe


def prepare_data(preferred_genres):
    print("Preparing data...")
    dataframe = process_dataframe(generate_dataframe_from_db(), preferred_genres)
    tfidf_matrix, tfidf = generate_tfidf_matrix(dataframe)
    cosine_sim = generate_cosine_sim(tfidf_matrix)

    cosine_sim_df = pd.DataFrame(cosine_sim, index=dataframe.index, columns=dataframe.index)

    cosine_sim_df.to_pickle('recommender/cosine_sim.pkl')
    dataframe.to_pickle('recommender/dataframe.pkl')

    return cosine_sim, dataframe


def load_data():
    print("Loading data...")
    current_dir = os.path.dirname(__file__)

    cosine_sim_path = os.path.join(current_dir, 'cosine_sim.pkl')
    dataframe_path = os.path.join(current_dir, 'dataframe.pkl')

    cosine_sim = pd.read_pickle(cosine_sim_path)
    dataframe = pd.read_pickle(dataframe_path)

    return cosine_sim, dataframe
