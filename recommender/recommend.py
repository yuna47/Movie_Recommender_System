from process_data import prepare_data, load_data


def prepare(preferred_genres):
    try:
        cosine_sim, dataframe = load_data()
    except FileNotFoundError:
        cosine_sim, dataframe = prepare_data(preferred_genres)

    return cosine_sim, dataframe


def recommend(movie_ids, preferred_genres):
    cosine_sim, dataframe = prepare(preferred_genres)
    result = set()

    for movie_id in movie_ids:
        # Get similarity scores for the selected movie
        sim_scores = list(enumerate(cosine_sim[movie_id]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:21]  # Exclude the movie itself from recommendations

        # Get indices of recommended movies
        movie_indices = [i[0] for i in sim_scores]

        # Add recommended movie indices to the set
        result.update(movie_indices)

    result = list(result)[:20]

    # print('< 추천 영화 >')
    # for i, movie_id in enumerate(result):
    #     print(f'{i + 1} : {dataframe["title"][movie_id]} {movie_id}')

    return result
