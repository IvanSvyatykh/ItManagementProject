from datetime import datetime
from typing import List
from matplotlib.path import Path
import matplotlib.pyplot as plt
import pandas as pd


async def create_hist_of_day_disribution(
    y_data: List[float], x_data: List[datetime], path_to_png: Path
) -> None:

    df = pd.DataFrame({"value": y_data, "timestamp": x_data})
    grouped_df = df.groupby(
        pd.Grouper(key="timestamp", freq="30min")
    ).mean()
    x_dates_grouped = grouped_df.index.to_pydatetime()
    x_labels = [dt.strftime("%H:%M") for dt in x_dates_grouped]
    fig, ax = plt.subplots()
    ax.bar(x_labels, grouped_df["value"], width=0.9, align="center")
    plt.gcf().autofmt_xdate(rotation=45)
    plt.title(f"Загруженность кухни за {x_data[0].date()}")
    plt.xlabel("Часы")
    plt.ylabel("Среднее количество человек")
    fig.savefig(path_to_png)
    plt.close(fig)
