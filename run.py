import torch.nn as nn
from torch_geometric.utils import to_dense_adj
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv, TransformerConv
import torch
import csv


class Filter(nn.Module):
    def __init__(self,
        in_channels : int,
        out_channels : int,
        k : int = 3
    ) -> None:
        super(Filter, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.num_layers = k
        self.layers = nn.ModuleList([TransformerConv(in_channels, out_channels, edge_dim = 2) for _ in range(k)])

    def forward(self, X, edge_index, edge_attr):
        x = X
        s = torch.zeros(X.shape[0], self.out_channels)
        
        A = to_dense_adj(edge_index)[0]
        for layer in self.layers:
            s += layer(x, edge_index, edge_attr)
                    
            x = torch.matmul(A, x)
            
        return torch.sigmoid(s)
    
class PowerGridGNN(nn.Module):
    def __init__(self, in_features=2, hidden_dim=16, out_features=2):
        super(PowerGridGNN, self).__init__()
        self.conv1 = Filter(in_features, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, out_features)
    
    def forward(self, data):
        x, edge_index, edge_attr = data.x, data.edge_index, data.edge_attr
        
        x = self.conv1(x, edge_index, edge_attr)  # First GCN layer
        x = self.conv2(x, edge_index)  # Output layer (Voltage predictions)
        return x.squeeze()  # Return node-wise voltage values

# Initialize and test the model

if __name__ == "__main__":
    import pandas as pd
    model = PowerGridGNN(in_features=8, hidden_dim=16, out_features=2)
    model.load_state_dict(torch.load("power_grid_gnn.pth"))

    X = pd.read_csv("X.csv")
    X = torch.from_numpy(X.drop(columns=["bus"]).to_numpy(dtype='float32'))

    edge_index, edge_attr = pd.read_csv("edge_index.csv")[['from_bus', 'to_bus']], pd.read_csv("edge_index.csv")[['R', 'X']]

    edge_index = torch.from_numpy(edge_index.to_numpy(dtype='int').T)
    edge_attr = torch.from_numpy(edge_attr.to_numpy(dtype='float32'))

    print(X.dtype, edge_attr.dtype)
    data = Data(x=X, edge_index=edge_index, edge_attr=edge_attr)
    out = model(data)
    with open("output.csv", 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["v_kv", "angle"])
        writer.writerows(out.tolist())
