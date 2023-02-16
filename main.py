import torch
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import StepLR
from sentence_transformers import SentenceTransformer
from utils.load_dataset import LoadDataset
from utils.helpers import get_num_anchors, get_max_num_codes
from model.encoder_decoder import EncoderDecoder
from typing import Literal
import argparse

def train_step1(epochs: int, model: EncoderDecoder, data_loader: DataLoader,device: Literal, loss_fn, optimizer, scheduler ):
    for t in range(epochs):
        for batch, (features, labels) in enumerate(data_loader):
            features, labels = features.to(device), labels.to(device)
            _, pred = model(features)
            loss = loss_fn(pred, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % 5 == 0:
                loss = loss.item()
                print(f"[epoch: {t:>3d}] loss:{loss:>7f}")
        scheduler.step()


if __name__ == "__main__":
    n_input = 768
    n_embedding = 512
    n_anchors = get_num_anchors()
    n_codes = get_max_num_codes()
    learning_rate = 1e-5
    batch_size = 128
    epochs = 100
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    parser = argparse.ArgumentParser(description="options")
    parser.add_argument('-s', '--step', type=int)
    args = parser.parse_args()

    ## pre training step
    if args.step == 1:
        model = EncoderDecoder(n_input, n_embedding, n_anchors, n_codes)
        model.to(device)
        loss_fn = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(),lr=learning_rate)
        scheduler = StepLR(optimizer, step_size=20, gamma=0.95)

        data_loader = DataLoader(LoadDataset(), batch_size=120, shuffle=True)
        
        train_step1(epochs, model,data_loader, device, loss_fn, optimizer, scheduler)
        
        torch.save(model.state_dict(), './trained/step-1.pth')
    
    ## denoising autoencoder step
    if args.step == 2:
        model = EncoderDecoder(n_input, n_embedding, n_anchors, n_codes)
        model.load_state_dict(torch.load('./trained/step-1.pth'), strict=False)

        ## find a way to add and initialize an extra input to the decoder;
        ## this extra information would tell the decoder, what coding system;
        ## the input belongs to, eg. ICD-10 or ICD-10-CM;
        model.to(device)


    ## step 3
    if args.step == 3:
        model = EncoderDecoder(n_input, n_embedding, n_anchors)