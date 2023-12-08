import os
import re
import pandas as pd
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sqlalchemy import create_engine


okt = Okt()


def sub_special(text):
    return re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣0-9a-zA-Z]', ' ', text)


def normalize(text):
    tokens = okt.morphs(text)
    return ' '.join(tokens)


def sub_horror_genre(text):
    return text.replace('호러', '')


def process_genre(text, preferred_genres):
    genres = text.split()
    for preferred_genre in preferred_genres:
        if preferred_genre in genres:
            text += f" {preferred_genre}"

    return text


def process_dataframe(dataframe, preferred_genres):
    dataframe = dataframe.fillna('')
    dataframe["genre"] = dataframe["genre"].apply(sub_special)
    dataframe["genre"] = dataframe["genre"].apply(sub_horror_genre)
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


def generate_indices(dataframe):
    # return pd.Series(dataframe['id'].values, index=dataframe['title']).drop_duplicates()
    return pd.Series(dataframe.index, index=dataframe['title']).drop_duplicates()


def generate_dataframe_from_db():
    # MySQL 데이터베이스에 연결
    db_url = 'mysql+mysqlconnector://dc2023:dc5555@210.117.128.202:3306/movieflix'
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


def prepare_data(file_path, preferred_genres):
    dataframe = process_dataframe(generate_dataframe_from_db(), preferred_genres)
    # dataframe = process_dataframe(pd.read_csv(file_path), preferred_genres)
    tfidf_matrix, tfidf = generate_tfidf_matrix(dataframe)
    cosine_sim = generate_cosine_sim(tfidf_matrix)
    indices = generate_indices(dataframe)

    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
    cosine_sim_df = pd.DataFrame(cosine_sim, index=dataframe.index, columns=dataframe.index)

    tfidf_df.to_pickle('tfidf_matrix.pkl')
    cosine_sim_df.to_pickle('cosine_sim.pkl')
    indices.to_pickle('indices.pkl')
    dataframe.to_pickle('dataframe.pkl')

    return tfidf_matrix, cosine_sim, indices, dataframe


def load_data():
    # tfidf_matrix = pd.read_pickle('tfidf_matrix.pkl')
    # cosine_sim = pd.read_pickle('cosine_sim.pkl')
    # indices = pd.read_pickle('indices.pkl')
    # dataframe = pd.read_pickle('dataframe.pkl')

    current_dir = os.path.dirname(__file__)

    tfidf_matrix_path = os.path.join(current_dir, 'tfidf_matrix.pkl')
    cosine_sim_path = os.path.join(current_dir, 'cosine_sim.pkl')
    indices_path = os.path.join(current_dir, 'indices.pkl')
    dataframe_path = os.path.join(current_dir, 'dataframe.pkl')

    tfidf_matrix = pd.read_pickle(tfidf_matrix_path)
    cosine_sim = pd.read_pickle(cosine_sim_path)
    indices = pd.read_pickle(indices_path)
    dataframe = pd.read_pickle(dataframe_path)

    return tfidf_matrix, cosine_sim, indices, dataframe
