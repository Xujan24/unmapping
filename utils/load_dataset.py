import torch
from torch.utils.data import Dataset
from sentence_transformers import SentenceTransformer
from utils.helpers import get_anchors, get_num_anchors, get_one_hot_encoding, read_data_from_csv


class LoadDataset(Dataset):
    def __init__(self) -> None:
        super().__init__()
        self.dataset = read_data_from_csv()

        self.anchors_list = get_anchors()
        self.sentence_transformer = SentenceTransformer('all-mpnet-base-v2')
    
    def __getitem__(self, index):
        item = self.dataset[index]
        idx, code, text, anchor = item
        feature = torch.from_numpy(self.sentence_transformer.encode(text))
        label = torch.from_numpy(get_one_hot_encoding(anchor))
        return feature, label
    
    def __len__(self) -> int:
        return len(self.dataset)