import tensorflow as tf
import numpy as np
from util.ops import shape_list

class MultiheadAttention():
  '''Multi-head attention implementation'''
  def __init__(self,
               query,
               value,
               num_heads=4,
               attention_type='mlp_attention',
               key_dim=128,
               value_dim=256):
    self.query = query
    self.value = value
    self.num_heads = num_heads
    self.key_dim = key_dim
    self.value_dim = value_dim
    self.scale_factor = (key_dim // num_heads)**-0.5

  def multi_head_attention(self):
    with tf.variable_scope("Multihead-attention"):
      q, k, v = self._linear_trans(self.query, self.value)
      qs, ks, vs = self._split_heads(q, k, v)
      style_embeddings = self._dot_product(qs, ks, vs)
      return self._combine_heads(style_embeddings)

  def _linear_trans(self, q, v):
    q = tf.layers.dense(q, self.key_dim, use_bias=False, name="q")
    k = tf.layers.dense(v, self.key_dim, use_bias=False, name="k")
    if self.linear_trans_for_value:
      v = tf.layers.dense(v, self.value_dim, use_bias=False, name="v")
    return q, k, v

  def _split_heads(self, q, k, v):
    '''Split the channels into multiple heads
    
    Returns:
         Tensors with shape [batch, num_heads, length_x, dim_x/num_heads]
    '''
    qs = tf.transpose(self._split_last_dimension(q, self.num_heads), [0, 2, 1, 3])
    ks = tf.transpose(self._split_last_dimension(k, self.num_heads), [0, 2, 1, 3])
    if self.linear_trans_for_value:
      vs = tf.transpose(self._split_last_dimension(v, self.num_heads), [0, 2, 1, 3])
    else:
      v_shape = shape_list(v)  
      vs = tf.tile(tf.expand_dims(v, axis=1), [1, self.num_heads, 1, 1])
    return qs, ks, vs

  def _split_last_dimension(self, x, num_heads):
    '''Reshape x to num_heads

    Returns:
        a Tensor with shape [batch, length_x, num_heads, dim_x/num_heads]
    '''
    x_shape = shape_list(x)
    dim = x_shape[-1]
    assert dim % num_heads == 0 
    return tf.reshape(x, x_shape[:-1] + [num_heads, dim // num_heads])

  def _dot_product(self, q, k, v):
    '''dot-product computation

    Returns:
        a context vector with shape [batch, num_heads, length_q, dim_v]
    '''
    qk = tf.matmul(q, k, transpose_b=True)
    qk *= self.scale_factor
    weights = tf.nn.softmax(qk, name="dot_attention_weights")
    context = tf.matmul(weights, v)
    return context

  def _mlp_attention(self, q, k, v):
    '''MLP computation modified by https://github.com/npuichigo

    Returns:
        a context vector with shape [batch, num_heads, length_q, dim_v]
    '''
    num_units = q.get_shape()[-1].value
    dtype = q.dtype

    v = tf.get_variable("attention_v", [num_units], dtype=dtype)
    # Single layer multilayer perceptron.
    add = tf.reduce_sum(v * tf.tanh(k + q), [-1], keepdims=True)
    # Compute attention weights.
    weights = tf.nn.softmax(add, name="mlp_attention_weights")
    # Compute attention context.
    context = tf.matmul(attn, values, transpose_a=True

  def _combine_heads(self, x):
    '''Combine all heads

       Returns:
           a Tensor with shape [batch, length_x, shape_x[-1] * shape_x[-2]]
    '''
    x = tf.transpose(x, [0, 2, 1, 3])
    x_shape = shape_list(x)
    return tf.reshape(x, x_shape[:-2] + [self.num_heads * x_shape[-1]])
  

