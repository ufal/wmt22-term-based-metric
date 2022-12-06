import os
import nltk

class Tokenizer:
    '''init: pass parameters of model, suffix of tokenized file
    tokenize - input path, output path
    TODO: tokenize_folder
    TODO: lemmatize'''

    def __init__(self, model, path_to_model=None, tokenized_suffix='_tokenized'):
        self.model = model
        self.path_to_model = path_to_model
        self.tokenized_suffix = tokenized_suffix

    def __str__(self):
        return f"Tokenizer with {self.model} model"

    def tokenize_file(self, input_path, output_path, language='English'):
        #print('a')
        #print(input_path)
        #print(type(input_path))
        input_fname = os.path.split(input_path)[-1]
        print(input_fname)
        output_fname = input_fname.rstrip('.txt') + self.tokenized_suffix + '.txt'
        #print(output_fname)
        full_output_path = os.path.join(output_path, output_fname)
        #print(full_output_path)
        if self.model == 'morphodita':
            line = f'python {self.path_to_model} --src_file {input_path} --tgt_file {full_output_path} --lang {language.lower()}'
            os.system(line)
        elif self.model == 'nltk':
            #full_lang_dict = {'EN': 'english', 'CS': 'czech'}
            #full_lang = full_lang_dict[lang]
            with open(input_path, 'r', encoding='utf-8') as f_src:
                src_lines = f_src.readlines()
            for src_line in src_lines:
                tgt_line = nltk.word_tokenize(src_line, language=language.lower())
                tgt_line = ' '.join(tgt_line) + '\n'
                with open(full_output_path, 'a', encoding='utf-8') as f_tgt:
                    f_tgt.write(tgt_line)
        else:
            return 'No model chosen'

        final_line = f'tokenization for file {output_fname} done successfully'
        return final_line

    def tokenize_folder(self, input_path, output_path, language='English'):
        input_filenames = os.listdir(input_path)
        for input_file in input_filenames:
            full_input_path = os.path.join(input_path, input_file)
            self.tokenize_file(full_input_path, output_path, language=language)
        final_line = f'tokenization for folder {input_path} done successfully'
        return final_line

    def lemmatize(self):
        return None