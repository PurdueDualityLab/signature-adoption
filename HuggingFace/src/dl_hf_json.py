from huggingface_hub.hf_api import ModelInfo, list_models
from glob import glob
from json import dump, load
from os import makedirs
from os.path import isdir, isfile
from pathlib import PurePath
from typing import List


def saveJSON(json: List[dict], filepath: PurePath = "data.json") -> None:
    with open(filepath, "w") as jsonFile:
        dump(obj=json, fp=jsonFile, indent=4)
        jsonFile.close()


def readJSON(jsonFilePath: PurePath) -> dict:
    with open(jsonFilePath, "r") as jsonFile:
        jsonData: dict = load(jsonFile)
        jsonFile.close()

    return jsonData

def getModelList() -> List[dict]:
    modelList: List[dict] = []

    print("Getting all PTMs hosted on Hugging Face...")
    resp: List[ModelInfo] = list_models(full=True, cardData=True, fetch_config=True, token='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')

    model: ModelInfo
    for model in list(iter(resp)):
        modelDict: dict = model.__dict__
        modelDict["siblings"] = [file.__dict__ for file in modelDict["siblings"]]
        modelList.append(modelDict)
    return modelList

def main() -> None:

    json: List[dict] = getModelList()

    print(f"Saving JSON")
    saveJSON(json=json)

if __name__ == "__main__":
    main()
