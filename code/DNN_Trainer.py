import json
import numpy as np
#from VLQCouplingCalculator import VLQCouplingCalculator as vlq
import torch
import torch.nn as nn
from torch import optim
from torch.utils.data import DataLoader, random_split
from ReweighterNN import *

# [modeW, modeZ, modeH, mass/2500., mT/2500., M_target/2500., G_target/2500., float(eventID), y]

def Loss(y, y_pred):
    return torch.mean(((y - y_pred)/y)**2)

def Train(model, modelname, optimizer, device, 
          n_epochs, batchsize, X_train, X_test, X_test_only,
          train_loss_epochs, test_loss_epochs_1, test_loss_epochs_2):

    minloss = 99999.0
    for jj in range(n_epochs):
        xtf_batch = DataLoader(X_train, batch_size = batchsize, shuffle=True)
        if jj%(int(n_epochs/500)) == 0 or jj == n_epochs - 1:
            do_print = True
        else:
            do_print = False
        this_loss = [] 
        for i, xtf in enumerate(xtf_batch):
            y = xtf[:, -1].reshape(-1).to(device)
            y_pred = Model.forward(xtf[:, :-2]).reshape(-1)
            loss = Loss(y, y_pred)
            if do_print:
                print("Epoch = {}, Loss = {}".format(jj, int(loss*1.e+7)/1.e+7), end='\r')
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            this_loss.append(float(loss))
            del y, y_pred
        train_loss_epochs.append(float(torch.mean(torch.tensor(this_loss))))
        with torch.no_grad():
            test_set_1 = np.random.choice(len(X_test), batchsize, False)
            test_set_2 = np.random.choice(len(X_test_only), batchsize, False)
            y_test_pred_1 = Model.forward(X_test.dataset[X_test.indices][test_set_1][:, :-2]).reshape(-1)
            y_test_pred_2 = Model.forward(X_test_only[test_set_2][:, :-2]).reshape(-1)
            y_test_1 = X_test.dataset[X_test.indices][test_set_1][:, -1].reshape(-1)
            y_test_2 = X_test_only[test_set_2][:, -1].reshape(-1)
            test_loss_epochs_1.append(float(Loss(y_test_1.to(device), y_test_pred_1)))
            test_loss_epochs_2.append(float(Loss(y_test_2.to(device), y_test_pred_2)))
        del test_set_1, test_set_2, y_test_pred_1, y_test_pred_2, y_test_1, y_test_2
        if do_print:
            print("epoch = ", jj)
            print("\t Trianing Loss = ", train_loss_epochs[-1])
            print("\t Test Loss for train and test set = ", test_loss_epochs_1[-1])
            print("\t Test Loss for test only set = ", test_loss_epochs_2[-1])
        if jj > n_epochs/10 and float(train_loss_epochs[-1]) < minloss:
            minloss = float(train_loss_epochs[-1])
            torch.save(model, modelname)
            torch.save(train_loss_epochs,  "../Models/TrainingLossVLQ_" + Modelname.split('/')[-1].replace(".model", ".data")) 
            torch.save(test_loss_epochs_1, "../Models/TestLoss1VLQ_"    + Modelname.split('/')[-1].replace(".model", ".data"))
            torch.save(test_loss_epochs_2, "../Models/TestLoss2VLQ_"    + Modelname.split('/')[-1].replace(".model", ".data"))

if __name__ == "__main__" : 
    #X_train_test = torch.tensor(np.load("../data/VLQ_WTZt_X_train_test.npy")[:, 3:])
    X_train_test = torch.tensor(np.load("../data/VLQ_X_train_test.npy"))
    nVars = X_train_test.shape[1]
    X_train, X_test = random_split(X_train_test, 
                                   [int(X_train_test.shape[0]/4.0), X_train_test.shape[0] - int(X_train_test.shape[0]/4.0)])
    np.save("../data/VLQ_X_train_indices.npy", X_train.indices)
    np.save("../data/VLQ_X_test_indices.npy",  X_test.indices)
    #X_test_only = torch.tensor(np.load("../data/VLQ_WTZt_X_test_only.npy")[:, 3:])
    X_test_only = torch.tensor(np.load("../data/VLQ_X_test_only.npy"))
    Layers = [nVars - 2] + [1024]*3 + [1]
    Activation = nn.LeakyReLU()
    Modelname = "../Models/TrainedVLQ_nLayers_" \
            + str(len(Layers)) + "_nNodes_" + str(Layers[1]) + ".model"
    Device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #Device = 'cpu'

    Model = Reweighter(X_mean = 0.,
                       X_std = 1.,
                       Layers = Layers,
                       Activation = Activation,
                       device = Device)
    params = list(Model.parameters())
    optimizer = optim.Adam(params, lr=1e-3)
    n_epochs = 500
    batchsize = int(len(X_train)/50)
    train_loss_epochs = []
    test_loss_epochs_1 = []
    test_loss_epochs_2 = []

    Train(model = Model, 
          modelname = Modelname, 
          optimizer = optimizer, 
          device = Device,
          n_epochs = n_epochs, 
          batchsize = batchsize,
          X_train = X_train, 
          X_test = X_test, 
          X_test_only = X_test_only,
          train_loss_epochs = train_loss_epochs, 
          test_loss_epochs_1 = test_loss_epochs_1, 
          test_loss_epochs_2 = test_loss_epochs_2)

    
