import pandas
import numpy as np
from pandas import DataFrame

def shrinkDataFrame(df: DataFrame, shrinkage: float = 0.1) -> DataFrame:
    if shrinkage >= 1:
        return df

    dfSize: int = len(df)
    lastRow: int = int(dfSize * shrinkage)

    return df.iloc[0:lastRow, :]


def main(shrinkage: float = .1) -> None:

    print(f"Loading into DataFrame...")
    df: DataFrame = pandas.read_json('data.json')

    print(f"Sorting DataFrame rows by download...")
    df.sort_values(by="downloads", ascending=False, inplace=True)
    df.reset_index(inplace=True)

    print(f"Reducing the size of the DataFrame to {shrinkage}...")
    df = shrinkDataFrame(df, shrinkage)

    urls: List[str] = [f"https://huggingface.co/{id}" for id in df["id"]]
    downloads: List[int] = [dl for dl in df["downloads"]]

    combined_urls_downloads = zip(urls, downloads)
    
    with open(f"./urls.txt", "w", newline="\n") as f:
        f.writelines([url + "\n" for url in urls])

    with open(f"./urls_downloads.csv", "w", newline="\n") as f:
        f.writelines([str(c[0]) + ',' + str(c[1]) + '\n' for c in combined_urls_downloads])



if __name__ == "__main__":
    main()
