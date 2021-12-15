import torch
import torch.nn as nn
import torch.nn.functional as F

import sys
import pickle

import pt_util

class TransliterateNet(nn.Module):
    
    def __init__(self, en_vocab_size, lang_vocab_size, feature_size, rnn_type):
        super(TransliterateNet, self).__init__()
        self.en_vocab_size = en_vocab_size
        self.lang_vocab_size = lang_vocab_size
        self.feature_size = feature_size
        
        self.encoder = nn.Embedding(self.en_vocab_size, self.feature_size)
        self.midLayer = nn.Linear(self.feature_size, self.feature_size)
        self.decoder = nn.Linear(self.feature_size, self.lang_vocab_size)
        
        if rnn_type == 'gru':
            self.rnn = nn.GRU(self.feature_size, self.feature_size, num_layers = 1, batch_first=True)
            self.rnn2 = nn.GRU(self.feature_size, self.feature_size, num_layers = 1, batch_first=True)
        elif rnn_type == 'lstm':
            self.rnn = nn.LSTM(self.feature_size, self.feature_size, num_layers = 1, batch_first=True)
            self.rnn2 = nn.LSTM(self.feature_size, self.feature_size, num_layers = 1, batch_first=True)
        else:
            raise ValueError('RNN type must be either \'gru\' or \'lstm\'')

        #self.decoder.weight = self.encoder.weight
        #self.decoder.bias.data.zero_()
        
        self.best_accuracy = -1
    
    def forward(self, x, hidden_state=None):
        x = self.encoder(x)
        x, hidden_state = self.rnn(x, hidden_state)
        x = self.midLayer(x)
        x = F.leaky_relu(x)
        x, hidden_state = self.rnn2(x, hidden_state)
        x = self.decoder(x)
        return x, hidden_state

    # This defines the function that gives a probability distribution and implements the temperature computation.
    def inference(self, x, hidden_state=None, temperature=1):
        x = x.view(-1, 1)
        x, hidden_state = self.forward(x, hidden_state)
        x = x.view(1, -1)
        x = x / max(temperature, 1e-20)
        x = F.softmax(x, dim=1)
        return x, hidden_state

    # Predefined loss function
    def loss(self, prediction, label, reduction='mean'):
        loss_val = F.cross_entropy(prediction.view(-1, self.lang_vocab_size), label.view(-1), reduction=reduction)
        return loss_val

    # Saves the current model
    def save_model(self, file_path, num_to_keep=1):
        pt_util.save(self, file_path, num_to_keep)

    # Saves the best model so far
    def save_best_model(self, accuracy, file_path, num_to_keep=1):
        if accuracy > self.best_accuracy:
            self.save_model(file_path, num_to_keep)
            self.best_accuracy = accuracy

    def load_model(self, file_path):
        pt_util.restore(self, file_path)

    def load_last_model(self, dir_path):
        return pt_util.restore_latest(self, dir_path)

def tokenize_data(data, voc2ind):
    return [voc2ind[char] for char in data]

def detokenize_and_depad_data(data, ind2voc, pad_val=0):
    res = []
    for ind in data:
        if ind.item() == pad_val:
            break
        res.append(ind2voc[ind.item()])
    return res

def pad_data(data, seq_len, pad_val=0):
    for _ in range(len(data), seq_len):
        data.append(pad_val)
    return data

def generate_transliteration(word, model, en_voc2ind, lang_ind2voc, seq_len):
    transliteration = []
    hidden = None
    
    en_tokens = tokenize_data(word, en_voc2ind)
    en_data = torch.LongTensor(pad_data(en_tokens, seq_len))
    
    for c in torch.LongTensor(en_data):
        x, hidden = model.inference(c, hidden)
        transliteration.append(torch.argmax(x))
    
    return detokenize_and_depad_data(transliteration, lang_ind2voc, len(lang_ind2voc) - 1)

if __name__ == '__main__':
    # Load model vars

    lang_dict = {
        'ta': 'Tamil',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'hi': 'Hindi'
    }

    if len(sys.argv) != 2 or sys.argv[1] not in lang_dict:
        raise ValueError('Make sure you pass exactly one valid language specifier as an argument when running demo.py\n'
                            + 'The valid language specifiers are: \'ta\', \'ml\', \'bn\', \'hi\'')

    lang = sys.argv[1]
    device = torch.device('cpu')

    with open('./vars/{}.pkl'.format(lang), 'rb') as data_pkl:
        variables = pickle.load(data_pkl)

    en_voc2ind = variables['en_voc2ind']
    lang_ind2voc = variables['lang_ind2voc']
    seq_len = variables['seq_len']

    model = TransliterateNet(len(en_voc2ind), len(lang_ind2voc), feature_size=128, rnn_type='gru').to(device)
    model.load_model('model/{}_gru.pt'.format(lang))
    print('Succesfully loaded model: {}'.format(lang_dict[lang]))
    print()
    print('Please make sure to transliterate only with English alphabetical characters.')
    print()

    while True:
        word = input('Enter the English word to be transliterated to {}. Enter q to quit: '.format(lang_dict[lang]))
        if word == 'q':
            print('Program terminated.')
            print()
            break

        translit_list = generate_transliteration(word, model, en_voc2ind, lang_ind2voc, seq_len)
        transliteration = ''.join(translit_list)
        print('The transliteration is: {}'.format(transliteration))
        print()
