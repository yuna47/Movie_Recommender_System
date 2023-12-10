from process_data import prepare_data, load_data


def prepare(preferred_genres, modified):
    if modified:
        cosine_sim, dataframe = prepare_data(preferred_genres)
    else:
        try:
            cosine_sim, dataframe = load_data()
        except FileNotFoundError:
            cosine_sim, dataframe = prepare_data(preferred_genres)

    return cosine_sim, dataframe


def recommend(movie_ids, preferred_genres, modified):
    cosine_sim, dataframe = prepare(preferred_genres, modified)
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

    return result
