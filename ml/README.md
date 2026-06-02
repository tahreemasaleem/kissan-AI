# Kissan AI - Machine Learning Pipeline

This directory will hold all the scripts and Jupyter Notebooks for training the models.

## Data Setup

Since Kaggle datasets are very large, we do not track them in this repository. 
You need to manually download the datasets and place them in the correct folders.

### 1. Download PlantVillage Dataset
*   Go to Kaggle and download the PlantVillage dataset (or any crop dataset like Cotton).
*   Extract the images into `ml/data/raw/`

Your folder structure should look like this:
```text
ml/
├── data/
│   ├── raw/
│   │   ├── Apple___Apple_scab/
│   │   ├── Cotton___Target_Spot/
│   │   └── ...
│   └── processed/
├── README.md
└── train_cnn.ipynb (To be created)
```

## Next Steps

Once you have downloaded the dataset into the `ml/data/raw/` folder, let me know! 
I will generate a PyTorch or TensorFlow Jupyter Notebook (`train_cnn.ipynb`) that will:
1. Load and augment the images.
2. Fine-tune a pre-trained **ResNet-50** model.
3. Save the final weights to `ml/models/resnet50_crop_disease.pth` so our FastAPI backend can load it.
