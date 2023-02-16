import torch
import numpy as np
from model.encoder_decoder import EncoderDecoder
from utils.helpers import get_num_anchors, read_data_from_csv_for
from sentence_transformers import SentenceTransformer

sentence_transformer = SentenceTransformer('all-mpnet-base-v2')


if __name__ == "__main__":
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    data = read_data_from_csv_for(version=0)

    if data is not None:
        codes = []
        texts = []
        for i in range(len(data)):
            _, code, text, _ = data[i]
            codes.append(code)
            texts.append(text)

        text_embedings = []

        for text in texts:
            emb = sentence_transformer.encode(text)
            text_embedings.append(emb)

        text_embedings = torch.from_numpy(np.asarray(text_embedings)).to(device)

        model = EncoderDecoder(n_input = 768, n_embedding=512, n_anchors=get_num_anchors())
        
        model.load_state_dict(torch.load('./trained/step-1.pth'), strict=False)
        model.to(device)
        model.eval()

        out = model.encoder(text_embedings).detach().cpu().numpy()
        print(out.shape)