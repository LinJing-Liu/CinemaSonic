import numpy as np
import nltk
import csv
import pandas as pd
from nltk.tokenize import TreebankWordTokenizer
import math

treebank_tokenizer = TreebankWordTokenizer()

def build_inverted_index(msgs):
    """ Builds an inverted index from the messages.
    
    Arguments
    =========
    
    msgs: list of dicts.
        Each message in this list already has a 'toks'
        field that contains the tokenized message.
    
    Returns
    =======
    
    inverted_index: dict
        For each term, the index contains 
        a sorted list of tuples (doc_id, count_of_term_in_doc)
        such that tuples with smaller doc_ids appear first:
        inverted_index[term] = [(d1, tf1), (d2, tf2), ...]
        
    Example
    =======
    
    >> test_idx = build_inverted_index([
    ...    {'toks': ['to', 'be', 'or', 'not', 'to', 'be']},
    ...    {'toks': ['do', 'be', 'do', 'be', 'do']}])
    
    >> test_idx['be']
    [(0, 2), (1, 2)]
    
    >> test_idx['not']
    [(0, 1)]
    
    """
    # YOUR CODE HERE
    inverted_index = {}
    
    for i, tokens in enumerate(msgs):
        term_count = {}
        for token in tokens:
            if not (token in term_count):
                term_count[token] = 1
            else:
                term_count[token] += 1
        
        for term in term_count:
            if not (term in inverted_index):
                inverted_index[term] = [(i, term_count[term])]
            else:
                inverted_index[term].append((i, term_count[term]))
    
    return inverted_index


def compute_idf(inv_idx, n_docs, min_df=10, max_df_ratio=0.95):
    """ Compute term IDF values from the inverted index.
    Words that are too frequent or too infrequent get pruned.
    
    Hint: Make sure to use log base 2.
    
    Arguments
    =========
    
    inv_idx: an inverted index as above
    
    n_docs: int,
        The number of documents.
        
    min_df: int,
        Minimum number of documents a term must occur in.
        Less frequent words get ignored. 
        Documents that appear min_df number of times should be included.
    
    max_df_ratio: float,
        Maximum ratio of documents a term can occur in.
        More frequent words get ignored.
    
    Returns
    =======
    
    idf: dict
        For each term, the dict contains the idf value.
        
    """
    
    # YOUR CODE HERE
    idf = {}
    
    for term in inv_idx:
        df = len(inv_idx[term])
        df_percent = df / n_docs
        
        if df >= 10 and df_percent <=max_df_ratio:
            # compute IDF
            idf[term] = math.log2(n_docs / (1+df))
    
    return idf

def compute_doc_norms(index, idf, n_docs):
    """ Precompute the euclidean norm of each document.
    
    Arguments
    =========
    
    index: the inverted index as above
    
    idf: dict,
        Precomputed idf values for the terms.
    
    n_docs: int,
        The total number of documents.
    
    Returns
    =======
    
    norms: np.array, size: n_docs
        norms[i] = the norm of document i.
    """
    
    # YOUR CODE HERE
    doc_norms = np.zeros(n_docs)
    
    for term in idf:
        for doc_id, tf in index[term]:
            term_idf = idf[term]
            doc_norms[doc_id] += (tf * term_idf)**2
    
    return np.sqrt(doc_norms)

def accumulate_dot_scores(query_word_counts, index, idf):
    """ Perform a term-at-a-time iteration to efficiently compute the numerator term of cosine similarity across multiple documents.
    
    Arguments
    =========
    
    query_word_counts: dict,
        A dictionary containing all words that appear in the query;
        Each word is mapped to a count of how many times it appears in the query.
        In other words, query_word_counts[w] = the term frequency of w in the query.
        You may safely assume all words in the dict have been already lowercased.
    
    index: the inverted index as above,
    
    idf: dict,
        Precomputed idf values for the terms.
    
    Returns
    =======
    
    doc_scores: dict
        Dictionary mapping from doc ID to the final accumulated score for that doc
    """
    
    # YOUR CODE HERE
    doc_scores = {}
    
    for word in query_word_counts:
        q_i = query_word_counts[word] * idf[word]
        
        for doc_id, tf in index[word]:
            d_ij = tf * idf[word]
            if not (doc_id in doc_scores):
                doc_scores[doc_id] = 0
            doc_scores[doc_id] += q_i * d_ij
    
    return doc_scores

def text_to_term_dict(text):
  text = text.split()
  text_dict = {}
  for token in text:
    if token in text_dict:
      text_dict[token] += 1
    else:
      text_dict[token] = 1
  
  return text_dict

def index_search(query, index, idf, doc_norms, score_func=accumulate_dot_scores, tokenizer=treebank_tokenizer):
    """ Search the collection of documents for the given query
    
    Arguments
    =========
    
    query: string,
        The query we are looking for.
    
    index: an inverted index as above
    
    idf: idf values precomputed as above
    
    doc_norms: document norms as computed above
    
    score_func: function,
        A function that computes the numerator term of cosine similarity (the dot product) for all documents.
        Takes as input a dictionary of query word counts, the inverted index, and precomputed idf values.
        (See Q7)
    
    tokenizer: a TreebankWordTokenizer
    
    Returns
    =======
    
    results, list of tuples (score, doc_id)
        Sorted list of results such that the first element has
        the highest score, and `doc_id` points to the document
        with the highest score.
    
    Note: 
        
    """
    
    # YOUR CODE HERE
    query = query.lower()
    query_words = tokenizer.tokenize(query)
    
    # calculate word count in query
    query_word_count = {}
    for word in query_words:
        if word in idf:
            if not (word in query_word_count):
                query_word_count[word] = 0
            query_word_count[word] += 1
    
    # compute query norm
    q_norm = 0
    for word in query_word_count:
        q_norm += (query_word_count[word] * idf[word]) ** 2
    q_norm = math.sqrt(q_norm)
    
    # compute numerator for all documents
    dot_prods = score_func(query_word_count, index, idf)
    
    # for each document, compute the sim score
    cosine_sim = []
    
    for i, d_norm in enumerate(doc_norms):
        numerator = dot_prods[i] if i in dot_prods else 0 
        score = 0 if d_norm == 0 else numerator / (q_norm * d_norm)
        cosine_sim.append((score, i))
    
    return sorted(cosine_sim, key=lambda x : x[0], reverse=True)
