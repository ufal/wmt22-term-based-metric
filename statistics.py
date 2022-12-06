import pandas as pd
from sklearn import preprocessing
from sklearn.metrics import f1_score


class TermBasedMetric():

    def __init__(self, overall_metric):
        self.overall_metric = overall_metric
        #self.tort_fpath = tort_fpath
        pass

    def flatten(self, col, drop_zeros=True): # TODO: delete empty elements
        col = col.to_list()
        flattened_col = [term for sentence in col for term in str(sentence).split(';')]
        if drop_zeros:
            flattened_col = [term for term in flattened_col if term != '']
        return flattened_col

    def label_encode(self, tgt_list, gt_list):
        le = preprocessing.LabelEncoder()
        general_list = tgt_list + gt_list
        le.fit(general_list)
        tgt_encoded_list = le.transform(tgt_list)
        gt_encoded_list = le.transform(gt_list)
        return tgt_encoded_list, gt_encoded_list


    def termwise_metric(self, tgt_list, gt_list):
        gt_set = list(set(gt_list))
        termwise_dict = {gt_term: [0, 0] for gt_term in gt_set}
        for idx in range(len(gt_list)):
            termwise_dict[gt_list[idx]][0] += 1  # add to counts
            if tgt_list[idx] == gt_list[idx]:
                termwise_dict[gt_list[idx]][1] += 1  # add to correct occurrences

        termwise_df = pd.DataFrame.from_dict(termwise_dict, orient='index', columns=['count', 'correct'])
        termwise_df['ratio'] = termwise_df.apply(lambda row: row['correct'] / row['count'], axis=1)
        result_metric = termwise_df['ratio'].sum() / termwise_df.shape[0]
        return result_metric

    def make_metrics(self, tort_filepath, delimiter='\t'): #dummy='<NONE>' - ???
        dataframe = pd.read_csv(tort_filepath, sep=delimiter)
        tgt_list = self.flatten(dataframe['tgt_terms_str'], drop_zeros=True)
        gt_list = self.flatten(dataframe['gt_terms_str'], drop_zeros=True)
        #print(len(tgt_list), len(gt_list))
        if len(tgt_list) != len(gt_list):
            minimal = min(len(tgt_list), len(gt_list))
            tgt_list, gt_list = tgt_list[:minimal], gt_list[:minimal]
        # termwise metric:
        termwise = self.termwise_metric(tgt_list, gt_list)
        # overall_metric:
        tgt_encoded, gt_encoded = self.label_encode(tgt_list, gt_list)
        overall = self.overall_metric(tgt_encoded, gt_encoded, average='micro')
        return termwise, overall

    # own_metric, f1 = self.make_metrics(tort_fname, overall_metric=f1_score) # <- probably this to statistics
