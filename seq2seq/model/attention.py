import torch.nn as nn
import torch.nn.functional as F
from seq2seq.utils.masked_cross_entropy import *


class Attn(nn.Module):
    def __init__(self, method:str, hidden_size:int):
        super(Attn, self).__init__()

        self.method = method
        self.hidden_size = hidden_size

        if self.method == 'general':
            self.attn = nn.Linear(self.hidden_size, hidden_size)

        elif self.method == 'concat':
            self.attn = nn.Linear(self.hidden_size * 2, hidden_size)
            self.v = nn.Parameter(torch.tensor(1, hidden_size, dtype=torch.float))

    def forward(self, hidden:torch.tensor, encoder_outputs:torch.tensor):
        max_len = encoder_outputs.size(0)
        this_batch_size = encoder_outputs.size(1)
        # Create variable to store attention energies
        attn_energies = torch.zeros(this_batch_size, max_len, device=encoder_outputs.device)  # B x S

        # For each batch of encoder outputs
        for b in range(this_batch_size):
            # Calculate energy for each encoder output
            for i in range(max_len):
                attn_energies[b, i] = self.score(hidden[:, b], encoder_outputs[i, b].unsqueeze(0))
        # Normalize energies to weights in range 0 to 1, resize to 1 x B x S
        return F.softmax(attn_energies, dim=-1).unsqueeze(1)

    def score(self, hidden:torch.tensor, encoder_output:torch.tensor):

        if self.method == 'dot':
            energy = torch.squeeze(hidden).dot(torch.squeeze(encoder_output))
            return energy

        elif self.method == 'general':
            energy = self.attn(encoder_output)
            energy = torch.squeeze(hidden).dot(torch.squeeze(energy))
            return energy

        elif self.method == 'concat':
            energy = self.attn(torch.cat((hidden, encoder_output), 1))
            energy = self.v.dot(energy)
            return energy
