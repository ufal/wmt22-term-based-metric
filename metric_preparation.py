import nltk
import os
import re
import pandas as pd
import numpy as np
import yake
from sklearn import preprocessing
from sklearn.metrics import f1_score

class TermBasedMetricPreparator():

    def __init__(self, pseudoref_strategy):
        self.pseudoref_strategy = pseudoref_strategy

    def file_opener(self, filename, strip_whitelines=False, to_lower=False):
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read()
        if strip_whitelines:
            data = re.sub(r'\n+', r'\n', data)
        if to_lower:
            data = data.lower()
        if data[-1] == '\n':
            data = data[:-1]
        return data

    def extract_keywords(self, data, method='yake', max_tokens=2, kw_extractor=None):
        """methods: yake, keybert, manual (regex); TODO: tfidf, from wordlist"""
        if method == 'yake':
            kw_extractor = yake.KeywordExtractor(n=max_tokens)
            yake_keywords = kw_extractor.extract_keywords(data)
            kws = []
            for yake_kw in yake_keywords:
                kws.append(yake_kw[0])

        elif method == 'manual':
            kws = kw_extractor(data)

        elif method == 'keybert':
            kws = None

        return kws

    def regex_kw_extractor(self, text):

        kw_1 = re.compile(r'[Dd]ále (téže? )?(také )?(jen )?(jako )?[„"] (.*?) [“"]')  # 6
        kw_2 = re.compile(r'["„] (.*?) [“"] (je |jsou |znamená |znamenají )')  # 1

        kws_1 = [f[-1] for f in re.findall(kw_1, text)]
        kws_2 = [f[0] for f in re.findall(kw_2, text)]

        kws = kws_1 + kws_2
        return kws

    def find_kws_in_sentence(self, sentence, kws):
        sentence = sentence.split(' ')
        kws_list = []
        ids_list = []
        kw_sent_set = set()
        for idx, word in enumerate(sentence):
            # print(idx, word)
            for kw in kws:
                # print(kw)
                if word.startswith(kw.split(' ')[0]):
                    # print('bigger than one')
                    kw_split = kw.split(' ')
                    # print(kw_split)
                    kw_len = len(kw_split)
                    kw_elem_counter = 1
                    kw_elem_match = 1
                    try:
                        while kw_elem_counter < len(kw_split):
                            if kw_split[kw_elem_counter] == sentence[idx + kw_elem_counter]:
                                kw_elem_match += 1
                            kw_elem_counter += 1
                        if kw_elem_match == kw_len:
                            kws_list.append(kw)
                            ids_list.append([idx, kw_len])
                            kw_sent_set.add(kw)
                    except:
                        pass

                else:
                    pass

        return kws_list, ids_list, kw_sent_set

    def retrieve_word_ids(self, text, kws, tolerate_case=False):
        text = text.split('\n')
        text_kw = set()
        df = pd.DataFrame(data=text, columns=['src_sentence'])
        # df['src_terms'] = np.nan
        # df['src_ids'] = np.nan
        df['src_terms'], df['src_ids'], sent_kw = zip(*df['src_sentence'].apply(lambda x: self.find_kws_in_sentence(x, kws)))
        # print(type(text_kw), type(sent_kw))
        # print(text_kw)
        # print(sent_kw)
        for sent in sent_kw:
            text_kw.update(sent)
        return df, text_kw

    def open_alignment_file(self, alignment_file):
        with open(alignment_file, 'r', encoding='utf-8') as a_f:
            alignments = a_f.readlines()
            # aligned_pairs = [{i:{}} for i in range(len(alignments))]
        aligned_sents = []
        if alignments[-1] == '':
            alignments = alignments[:-1]
        for sent_idx, sent_alignments in enumerate(alignments):
            sent_dict = {}
            pairs_list = sent_alignments.split(' ')
            for pair in pairs_list:
                src, tgt = pair.split('-')
                src, tgt = int(src), int(tgt)
                # if there are 1-to=many relations:
                sent_dict[src] = tgt
            #            if src not in sent_dict:
            #                sent_dict[src] = {tgt}
            #            else:
            #                sent_dict[src].add(tgt)
            aligned_sents.append(sent_dict)

        return aligned_sents

    def extract_aligned_words(self, tgt_sentence_list, alignment, src_ids):
        alignment_words = []
        alignment_idxs = []
        for src_idx in src_ids:
            # alignment_ids = []
            alignment_word = []
            src_ids_extended = [src_idx[0] + i for i in range(src_idx[1])]
            primary_alignment_ids = []

            for src_idx_extended in src_ids_extended: # TODO: maybe better also redo as list of [first_id, length of aligned token]
                try:
                    aligned_idx = alignment[src_idx_extended]
                    # print(aligned_idx)
                    primary_alignment_ids.append(int(aligned_idx))
                except:
                    pass
                    # aligned_idx = -1
                    # not_found_words += 1
                # primary_alignment_ids.append(aligned_idx)

            alignment_ids = sorted(primary_alignment_ids)
            # print(alignment_ids)
            # print(tgt_sentence_list)
            alignment_word = [tgt_sentence_list[idx] for idx in alignment_ids]
            # print(alignment_word)
            alignment_words.append(' '.join(alignment_word))
            alignment_idxs.append(alignment_ids)
        return alignment_words, alignment_idxs

    def add_tgt_info(self, df, alignments, tgt_file):  # alignment_file
        tgt_sentences = tgt_file.split('\n')
        # print(len(tgt_sentences), len(alignments), df.shape[0])
#        minimum_length = min(len(tgt_sentences), len(alignments), df.shape[0])
#        tgt_sentences = tgt_sentences[:minimum_length]
#        df = df.iloc[:minimum_length]
        tgt_sentences_list = [sentence.split(' ') for sentence in tgt_sentences]
        df['tgt_sentence_list'] = tgt_sentences_list
        # alignments = open_alignment_file(alignment_file)
        # print('aaa')
        # if len(alignments) != df.shape[0]:
        # minimum_length = min(len(alignments), df.shape[0])
#        alignments = alignments[:minimum_length]
        # print(len(tgt_sentences), len(alignments), df.shape[0])

        # df = df.iloc[:minimum_length]
        # if df['src_sentence'].iloc[-1] == '':
        #    print('yes')
        #    df = df[:-1]
        df['alignment'] = alignments
        # print(df.columns)
        df['tgt_words'], df['tgt_ids'] = zip(
            *df.apply(lambda row: self.extract_aligned_words(row.tgt_sentence_list, row.alignment, row.src_ids), axis=1))
        return df

    def retrieve_alignment_variants(self, df, kw_list):
        alignment_variants_dict = {kw: {} for kw in kw_list}
        initiated = {kw: False for kw in kw_list}
        #    src_kw_col = df['src_terms'].to_list()
        #    src_kw_list = list(set([word for sentence in src_kw_col for word in sentence]))
        #tgt_initiated = dict()
        for index, row in df.iterrows():
            kw_len = len(row['src_terms'])
            #order_counter = 0.01
            for i in range(kw_len):
                src_term = row['src_terms'][i]
                tgt_term = row['tgt_words'][i]

                # if tgt_term == '':
                # first_time = False
                # initiated[src_term] = False
                # tgt_term = 'NAN'
                if not initiated[src_term]:  # and tgt_term != ''
                    first_time = True
                    # if tgt_term != '':
                    initiated[src_term] = tgt_term
                    # else:
                    #    initiated[src_term] = '<NONE>'
                else:
                    first_time = False
                if tgt_term in alignment_variants_dict[src_term]:
                    alignment_variants_dict[src_term][tgt_term] += 1
                else:
                    alignment_variants_dict[src_term][tgt_term] = 1
                #if tgt_term not in tgt_initiated:
                #    tgt_initiated[tgt_term] = index + order_counter
                #order_counter += 0.01
        df_data = []
        for src_term in alignment_variants_dict:
            for tgt_term in alignment_variants_dict[src_term]:
                is_initial = initiated[src_term] == tgt_term
                #if is_initial:
                #    index = index
                #else:
                #    index = -1
                df_data.append([src_term, tgt_term, alignment_variants_dict[src_term][tgt_term], is_initial]) #https://github.com/ufal/wmt22-term-based-metric

        df_alignment_variants = pd.DataFrame(data=df_data, columns=['src_term', 'tgt_term', 'count', 'is_initial'])

        most_common_translation_ids = df_alignment_variants.groupby('src_term')['count'].idxmax().to_list()
        df_alignment_variants['is_most_frequent'] = False
        for idx in most_common_translation_ids:
            df_alignment_variants.at[idx, 'is_most_frequent'] = True
        #df_alignment_variants[(df_alignment_variants.is_most_frequent == ''), 'is_most_frequent'] = '<NONE>'
        #df_alignment_variants['tgt_term'] = df_alignment_variants['tgt_term'].replace('', '<NOT_FOUND>', inplace=True)
        tgt_counts_dict = df_alignment_variants['tgt_term'].value_counts().to_dict()
        df_alignment_variants['tgt_overlap'] = df_alignment_variants['tgt_term'].apply(
            lambda x: True if (tgt_counts_dict[x] > 1 and x != '') else False)

        # TODO: think of something to block validating the same term as a translation.

        return df_alignment_variants

    def decide_the_best_tgt_correspondence(self, df, prescriptions=None, strategy='frequent'):
        # df - info about the actual correspondences, some features
        # prescriptions - some dictionary with best correspondences. Manually made?
        # strategy: [frequent, first]
        final_correspondences = {}
        # src_terms = list(df_a_v['src_term'].unique())
        if prescriptions is not None:
            pass  # TODO: for future
        #        df['prescribed'] = df.apply(lambda row: True if (row.src_term in prescriptions) else False) # and prescriptions[row.src_term] == row.tgt_term) else False)

        if strategy == 'frequent':
            if prescriptions is not None:
                df['prescribed'] = df.apply(
                    lambda row: True if (row.prescribed == True or row.is_most_frequent == True) else False)
                subset = df[df['prescribed'] == True]
            subset = df[df['is_most_frequent'] == True]
        elif strategy == 'first':
            if prescriptions is not None:
                df['prescribed'] = df.apply(
                    lambda row: True if (row.prescribed == True or row.is_initial == True) else False)
                subset = df[df['prescribed'] == True]
            subset = df[df['is_initial'] == True]

        final_correspondences = dict(zip(subset.src_term, subset.tgt_term))
        return final_correspondences
        #    subset = df[df['src_term'] == src_term]

    def get_pseudoref_by_src(self, src_list, pseudoref_dict):
        tgt_pseudoref_list = []
        if len(src_list) > 0:
            for src_term in src_list:
                tgt_pseudoref_term = pseudoref_dict[src_term]
                tgt_pseudoref_list.append(tgt_pseudoref_term)  # TODO: check if the order is correct

        return tgt_pseudoref_list

    def fill_ground_truth_terms(self, df, best_correspondences):
        df['pseudoref_terms'] = df['src_terms'].apply(lambda x: self.get_pseudoref_by_src(x, best_correspondences))
        return df

    def substitute_empty_translations(self, tgt_list, dummy='<NONE>'): # TODO: make iterative search for most frequent translation
        tgt_substituted_list = []
        for tgt in tgt_list:
            if tgt == '':
                tgt_substituted_list.append(dummy)
            else:
                tgt_substituted_list.append(tgt)
        return tgt_substituted_list

    def save_to_csv(self, df, filepath, dummy='<NONE>', delimiter='\t'):
        df['tgt_words'] = df['tgt_words'].apply(lambda x: self.substitute_empty_translations(x, dummy=dummy))
        df['pseudoref_terms'] = df['pseudoref_terms'].apply(lambda x: self.substitute_empty_translations(x, dummy=dummy))

        df['src_terms_str'] = df['src_terms'].apply(lambda x: ';'.join(x))
        df['tgt_terms_str'] = df['tgt_words'].apply(lambda x: ';'.join(x))
        df['pseudoref_terms_str'] = df['pseudoref_terms'].apply(lambda x: ';'.join(x))
        df['tgt_sentence_str'] = df['tgt_sentence_list'].apply(lambda x: ' '.join(x))

        df_to_save = df.copy(deep=True)
        df_to_save = df_to_save.drop(
            columns=['src_terms', 'src_ids', 'tgt_sentence_list', 'alignment', 'tgt_words', 'tgt_ids', 'pseudoref_terms'])
        df_to_save = df_to_save.reindex(
            ['src_sentence', 'tgt_sentence_str', 'src_terms_str', 'tgt_terms_str', 'pseudoref_terms_str'], axis="columns")

    #    for col in df_saved.columns.to_list():
    #        df_to_save[col] = df_to_save[col].str.replace(delimiter, '')
        df_to_save.to_csv(filepath, sep=delimiter)
        return df_to_save


    def pipeline(self, src_fname, tgt_fname, alg_fname, output_path): # 'first'
        src = self.file_opener(src_fname)
        tgt = self.file_opener(tgt_fname, to_lower=True)
        alg = self.open_alignment_file(alg_fname)
        alg_file = alg_fname.split('/')[-1]
        tort_fname = output_path + '/' + alg_file[:-2] + '_' + self.pseudoref_strategy + '.csv'
        kws = self.extract_keywords(src, method='manual', max_tokens=1, kw_extractor=self.regex_kw_extractor)
        df, kws_dict = self.retrieve_word_ids(src, kws)
        #####print(c_df.head(10))
        df = self.add_tgt_info(df, alg, tgt)
        #####print(df_c.head(10))
        df_a_v = self.retrieve_alignment_variants(df, kws_dict)
        #####print(df_a_v.head())
        best_correspondences = self.decide_the_best_tgt_correspondence(df_a_v, prescriptions=None, strategy=self.pseudoref_strategy) # TODO: add punishment for zero lines
        #####print(best_correspondences)
        #####print(len(c_kws_dict), len(df_a_v['src_term'].unique()), len(best_correspondences.keys()))
        df = self.fill_ground_truth_terms(df, best_correspondences)
        #####print(df_c.head(10))
        df_saved = self.save_to_csv(df, tort_fname, dummy='<NONE>')
        #own_metric, f1 = self.make_metrics(tort_fname, overall_metric=f1_score) # <- probably this to statistics
        return None#df_saved#df, df_a_v  #len(src.split('\n')), len(tgt.split('\n')), len(alg)#own_metric, f1


