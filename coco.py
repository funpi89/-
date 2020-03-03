import tensorflow as tf
import pickle
import re
import numpy as np
import os
import time
import json
from glob import glob
from PIL import Image
import pickle
from image_caption_model import *

with open('max_length.pickle', 'rb') as handle:
    max_length = pickle.load(handle)

with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

num_layers = 4
d_model = 128
dff = 512
num_heads = 8
top_k = 5000
target_vocab_size = top_k
dropout_rate = 0.1
transformer = Transformer(num_layers, d_model, num_heads, dff,
                          target_vocab_size,
                          pe_target=target_vocab_size,
                          rate=dropout_rate)
transformer.load_weights('transformer.weight')


def load_image(image_path):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, (299, 299))
    img = tf.keras.applications.inception_v3.preprocess_input(img)
    return img, image_path


def create_masks(tar):
    dec_padding_mask = create_padding_mask(tar)
    look_ahead_mask = create_look_ahead_mask(tf.shape(tar)[1])
    dec_target_padding_mask = create_padding_mask(tar)
    combined_mask = tf.maximum(dec_target_padding_mask, look_ahead_mask)

    return combined_mask, dec_padding_mask


def evaluate(image, image_features_extract_model):
    temp_input = tf.expand_dims(load_image(image)[0], 0)
    img_tensor_val = image_features_extract_model(temp_input)
    img_tensor_val = tf.reshape(img_tensor_val, (img_tensor_val.shape[0], -1, img_tensor_val.shape[3]))

    decoder_input = [tokenizer.word_index['<start>']]
    output = tf.expand_dims(decoder_input, 0)

    for i in range(max_length):
        combined_mask, dec_padding_mask = create_masks(output)
        predictions, attention_weights = transformer(img_tensor_val,
                                                     output,
                                                     False,
                                                     combined_mask,
                                                     dec_padding_mask)
        predictions = predictions[:, -1:, :]  # (batch_size, 1, vocab_size)

        predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)

        if int(predicted_id) == tokenizer.word_index['<end>']:
            return tf.squeeze(output, axis=0), attention_weights

        output = tf.concat([output, predicted_id], axis=-1)

    return tf.squeeze(output, axis=0), attention_weights


def translate(image, image_features_extract_model):
    result, attention_weights = evaluate(image, image_features_extract_model)
    predicted_sentence = []

    for idx in result:
        predicted_sentence.append(tokenizer.index_word[int(idx)])
    sentence = ' '.join(predicted_sentence)
    sentence = sentence.replace('<start>','').replace('<end>','')
    sentence += '.'
    return sentence


if __name__ == "__main__":
    image_path = 'human3.jpg'
    translate(image_path)
