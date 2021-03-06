import nltk
import sys
import os
import string
import math
nltk.download('stopwords')
nltk.download('punkt')

FILE_MATCHES = 1
SENTENCE_MATCHES = 1

def main():
    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)

def load_files(directory):
    directory=(r"/content/corpus")
    file_contents = dict()

    for root, _, files in os.walk(directory):
        for file in files:
            f = open(os.path.join(root, file), "r")
            file_contents[file] = f.read()

    return file_contents

def tokenize(document):
    punctuation = string.punctuation
    stop_words = nltk.corpus.stopwords.words("english")

    words = nltk.word_tokenize(document.lower())
    words = [word for word in words if word not in punctuation and word not in stop_words]

    return words

def compute_idfs(documents):
    idfs = dict()
    total_num_documents = len(documents)
    words = set(word for sublist in documents.values() for word in sublist)
    
    for word in words:
        num_documents_containing_word = 0
        
        for document in documents.values():
            if word in document:
                num_documents_containing_word += 1
        
        idf = math.log(total_num_documents / num_documents_containing_word)
        idfs[word] = idf

    return idfs

def top_files(query, files, idfs, n):
    file_scores = dict()

    for file, words in files.items():
        total_tf_idf = 0
        for word in query:
            total_tf_idf += words.count(word) * idfs[word]
        file_scores[file] = total_tf_idf

    ranked_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
    ranked_files = [x[0] for x in ranked_files]

    return ranked_files[:n]

def top_sentences(query, sentences, idfs, n):
    sentence_scores = dict()

    for sentence, words in sentences.items():
        words_in_query = query.intersection(words)
        
        # idf value of sentence
        idf = 0
        for word in words_in_query:
            idf += idfs[word]
        
        # query term density of sentence
        num_words_in_query = sum(map(lambda x: x in words_in_query, words))
        query_term_density = num_words_in_query / len(words)

        # update sentence scores with idf and query term density values
        sentence_scores[sentence] = {'idf': idf, 'qtd': query_term_density}
    
    # rank sentences by idf then query term density
    ranked_sentences = sorted(sentence_scores.items(), key=lambda x: (x[1]['idf'], x[1]['qtd']), reverse=True)
    ranked_sentences = [x[0] for x in ranked_sentences]

    return ranked_sentences[:n]

main()
