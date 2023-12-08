from process_data import prepare_data, load_data


def recommend(movie_ids, preferred_genres):
    # print("Loading data...")
    # tfidf_matrix, cosine_sim, dataframe = load_data()
    print("Preparing data...")
    tfidf_matrix, cosine_sim, dataframe = prepare_data(preferred_genres)
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


if __name__ == "__main__":
    # recommend('곤지암')
    # recommend(['조제', '말아톤', '가을로'], ['액션', '범죄'])
    recommend([16, 692, 687], ['액션', '범죄'])
    # recommend_list(['곤지암', '공작', '감기'])
    # recommend_list(['여고괴담 5', '부산행', '기생충'])
