import torch
import torch.nn as nn

class Reweighter(nn.Module):
    def __init__(self, 
                 Layers, 
                 #Categories, 
                 X_mean = 0., 
                 X_std = 1., 
                 Activation = nn.Sigmoid(), 
                 device = 'cpu'):
        super(Reweighter, self).__init__()
        self.Layers = Layers
        #self.Categories = torch.tensor(Categories)
        #self.nCategories = len(Categories)
        self.Activation = Activation
        self.device = device
        self.Model = self.build_model().to(device)
        self.X_mean = X_mean
        self.X_std = X_std
        
    def build_model(self):
        Seq = nn.Sequential()
        for ii in range(len(self.Layers)-2):
            this_module = nn.Linear(self.Layers[ii], self.Layers[ii+1])
            nn.init.xavier_normal_(this_module.weight)
            Seq.add_module("Linear" + str(ii), this_module)
            Seq.add_module("Activation" + str(ii), self.Activation)
        last_module = nn.Linear(self.Layers[-2], 1, True)
        Seq.add_module("Linear_last", last_module)
        #last_activation = nn.LeakyReLU()
        #Seq.add_module("Activation_last", last_activation)
        return Seq 
        
    def forward(self, X):
        X = ((X - self.X_mean)/self.X_std).to(self.device)
        #Xcat = X[:, self.Categories]
        #X = self.Model.forward(X).reshape(-1, self.nCategories)
        #return torch.sum(X*Xcat, dim=1)
        return self.Model.forward(X)
        
