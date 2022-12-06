import re
import os
import subprocess

class Aligner():
    def __init__(self, alignment_algorithm='fast_align', algorithm_path=None):
        self.alignment_algorithm = alignment_algorithm
        self.algorithm_path = algorithm_path

    def strip_filepath(self, fname):
        if fname.find('/') == -1:
            return fname
        else:
            fpath = fname.split('/')
            file_name = fpath[-1]
            return file_name

    def strip_filename_from_tokenized(self, fname):
        fname_cleared = re.sub('_tokenized', '', fname)
        return fname_cleared

    def create_bitext(self, src_file, tgt_file, bitext_filepath, bitext_suffix='.s'):

        def create_parallel_sentence(src_sent, tgt_sent, separator=' ||| '):
            src_sent = re.sub(r'\r?\n', '', src_sent)
            tgt_sent = re.sub(r'\r?\n', '', tgt_sent)
            parallel_sentence = src_sent + separator + tgt_sent + '\n'
            parallel_sentence = re.sub(r' +\|\|\|', r' |||', parallel_sentence)
            return parallel_sentence

        with open(src_file, 'r') as src, open(tgt_file, 'r') as tgt:
            src_sentences = src.readlines()
            tgt_sentences = tgt.readlines()

        if len(src_sentences) != len(tgt_sentences):
            print('ATTENTION: SRC AND TGT LENGTHS ARE NOT EQUAL')

        src_filename = self.strip_filepath(src_file)
        tgt_filename = self.strip_filepath(tgt_file)
        src_filename = self.strip_filename_from_tokenized(src_filename)
        tgt_filename = self.strip_filename_from_tokenized(tgt_filename)
        print(src_file)
        print(src_filename)
        print(tgt_file)
        print(tgt_filename)
        bitext_file = bitext_filepath + '/' + src_filename[:-4] + '_' + tgt_filename[:-4] + bitext_suffix

        f = open(bitext_file, 'w').close()
        with open(bitext_file, 'a') as prl:
            for i in range(len(src_sentences)):
                parallel_sentence = create_parallel_sentence(src_sentences[i], tgt_sentences[i], ' ||| ')
                prl.write(parallel_sentence)

        return f'bitext {bitext_file} created'

    def simple_align(self, bitext, output_folder, remove_aux=False):
        if self.alignment_algorithm == 'fast_align':
            bitext_filename = self.strip_filepath(bitext)
            forward_filename = output_folder + '/' + bitext_filename[:-2] + '.f'
            reverse_filename = output_folder + '/' + bitext_filename[:-2] + '.r'
            intersect_filename = output_folder + '/' + bitext_filename[:-2] + '.i'
            #print(bitext_filename)
            #print(forward_filename)
            #print(reverse_filename)
            #print(intersect_filename)
            fast_align_path = self.algorithm_path + '/' + 'fast_align'
            atools_path = self.algorithm_path + '/' + 'atools'
            #print(fast_align_path)
            #print(atools_path)
            #subprocess.check_call(['wsl', f'"{fast_align_path}" -d -o -v -i {bitext} > {forward_filename}'])
            os.system(f'"{fast_align_path}" -d -o -v -i {bitext} > {forward_filename}')
            #print(f'"{fast_align_path}" -d -o -v -i {bitext} > {forward_filename}')
            #subprocess.check_call(['wsl', f'"{fast_align_path}" -d -o -v -r -i {bitext} > {reverse_filename}'])
            #subprocess.check_call(['wsl', f'"{atools_path}"  -i {forward_filename} -j {reverse_filename} -c intersect > {intersect_filename}'])
            os.system(f'"{fast_align_path}" -d -o -v -r -i {bitext} > {reverse_filename}')
            os.system(f'"{atools_path}"  -i {forward_filename} -j {reverse_filename} -c intersect > {intersect_filename}')

            if remove_aux:
                os.remove(forward_filename)
                os.remove(reverse_filename)
        return f'bitext {bitext} alignment created'

    def gather_into_one(self, bitext_folder, output_folder, doc_delimiter='<END_OF_DOCUMENT> ||| <END_OF_DOCUMENT>\r\n'):
        bitexts = os.listdir(bitext_folder)

        bitexts_doc_list = list(set([bitext.split('_')[0] for bitext in bitexts])) # use it for splitting as well
        bitexts_alg_list = list(set([bitext.split('_')[1][:-2] for bitext in bitexts]))

        doc_order_filename = f'{output_folder}/doc_order.txt'
        #doc_order = open(doc_order_filename, 'w').close()
        for alg in bitexts_alg_list:
            output_file = output_folder + '/' + alg + '.s'
            doc_order = open(doc_order_filename, 'w').close() # TODO: do it more smoothly

            f = open(output_file, 'w').close()
            with open(output_file, 'a') as general_alignment, open(doc_order_filename, 'a') as doc_order:
                for doc in bitexts_doc_list:
                    filename = bitext_folder + '/' + doc + '_' + alg + '.s'
                    #print(filename)
                    with open(filename, 'r') as doc_alg_alignment:
                        sents = doc_alg_alignment.readlines()
                        for sent in sents:
                            general_alignment.write(sent)
                            doc_order.write(doc+'\n')
                    general_alignment.write(doc_delimiter)
                    doc_order.write(doc_delimiter)

                    #with open(f'{output_folder}/doc_order.txt', 'w') as d:
                    #    for doc in bitexts_doc_list:
                    #        d.write(doc + '\n')
        return None

    def align_big_bitexts(self, bitext_folder, output_folder):
        bitext_file_list = os.listdir(bitext_folder)
        for bitext in bitext_file_list:
            if bitext != 'doc_order.txt':
                bitext_fpath = bitext_folder + '/' + bitext
                self.simple_align(bitext_fpath, output_folder, remove_aux=True)
        return None

    def split_alignments(self, alignments_folder, doc_alg_fpath, output_folder, doc_delimiter='<END_OF_DOCUMENT> ||| <END_OF_DOCUMENT>\r\n'):
        alg_alignments = [f for f in os.listdir(alignments_folder) if f != 'doc_order.txt']
        bitexts_list_file = alignments_folder + '/' + 'doc_order.txt'

        with open(doc_alg_fpath, 'r') as f:
            doc_alg_list = [line[:-1] for line in f.readlines()]

        for alg in alg_alignments:
            alg_path = alignments_folder + '/' + alg
            with open(alg_path, 'r') as f:
                split_alignments = f.readlines()
            #split_alignments = full_alignments.split(doc_delimiter)
            if len(split_alignments) != len(doc_alg_list):
                print('LEN OF ALIGNMENTS NOT EQUAL TO # DOCS!!!')
                print(len(split_alignments), len(doc_alg_list))
            #for doc, alignment in zip(doc_alg_list, split_alignments):
            #    small_alignment_fname = output_folder + '/' + doc + '_' + alg
            #    with open(small_alignment_fname, 'w') as f:
            #        f.write(alignment)

            for doc_id, sent_alignment in zip(doc_alg_list, split_alignments):
                if doc_id != doc_delimiter:
                    small_alignment_fname = output_folder + '/' + doc_id + '_' + alg
                    with open(small_alignment_fname, 'a') as f: # TODO: eraze files automatically before each run
                        f.write(sent_alignment)
                else:
                    pass

        return None