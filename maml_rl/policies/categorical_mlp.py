import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical

from collections import OrderedDict
from maml_rl.policies.policy import Policy

def weight_init(module):
    if isinstance(module, nn.Linear):
        nn.init.xavier_uniform_(module.weight)
        module.bias.data.zero_()

class CategoricalMLPPolicy(Policy):
    def __init__(self, input_size, output_size,
                 hidden_sizes=(), nonlinearity=F.relu):
        super(CategoricalMLPPolicy, self).__init__(
            input_size=input_size, output_size=output_size)
        self.hidden_sizes = hidden_sizes
        self.nonlinearity = nonlinearity
        self.num_layers = len(hidden_sizes) + 1

        layer_sizes = (input_size,) + hidden_sizes + (output_size,)
        for i in range(1, self.num_layers + 1):
            self.add_module('layer{0}'.format(i),
                nn.Linear(layer_sizes[i - 1], layer_sizes[i]))
        self.apply(weight_init)

    def forward(self, input, params=None):
        if params is None:
            params = OrderedDict(self.named_parameters())
        output = input
        for i in range(1, self.num_layers):
            output = F.linear(output,
                weight=params['layer{0}.weight'.format(i)],
                bias=params['layer{0}.bias'.format(i)])
            output = self.nonlinearity(output)
        logits = F.linear(output,
            weight=params['layer{0}.weight'.format(self.num_layers)],
            bias=params['layer{0}.bias'.format(self.num_layers)])

        return Categorical(logits=logits)
