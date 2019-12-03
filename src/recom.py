# import pandas as pd
# import numpy as np

# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity as distance

# def similarityDF(TokensDict):
#     count_vectorizer = CountVectorizer()
#     sparse_matrix = count_vectorizer.fit_transform(TokensDict.values())
#     Tokens_term_matrix = sparse_matrix.todense()
#     df = pd.DataFrame(Tokens_term_matrix,columns=count_vectorizer.get_feature_names(),index=TokensDict.keys())
#     similarity_matrix = distance(df, df)
#     sim_df = pd.DataFrame(similarity_matrix, columns=TokensDict.keys(), index=TokensDict.keys())
#     np.fill_diagonal(sim_df.values, 0)
#     return sim_df