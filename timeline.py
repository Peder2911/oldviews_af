import seaborn as sns; sns.set()
from matplotlib import pyplot as plt
import pandas as pd
import geopandas as gpd
import sqlite3
import contextily as ctx

c = sqlite3.connect("data/pac.sqlite")

pred = pd.read_sql("SELECT * FROM predictions_2010_2050",c)

cc = pd.read_csv("data/cc.csv")
cc["gwcode"] = cc["gwn"]

shp = gpd.read_file("data/cshapes.shp")
shp = shp[
    (shp["GWEYEAR"] == 2016)
]
shp = shp.to_crs(epsg=3857)

pred = pred.merge(cc,on="gwcode",how="left")

pred = pred[
    (pred["year"] != pred["year"].max()) & 
    (pred["year"] != pred["year"].min())
]

#waf = pred[pred["un.regionsub.name"] == "Sub-Saharan Africa"]
waf = pred[pred["un.regionintermediate.name"] == "Western Africa"]

def thresh(df,when=2011,upper=None,lower=None):
    which = df["year"] == when
    if upper is not None:
        which &= df["combined"] < upper
    if lower is not None:
        which &= df["combined"] > lower
    return df[which]["gwcode"].values

for name,args in [
        ("hi",{"lower":0.1}),
        ("med",{"upper":0.1,"lower":0.03}),
        ("lo",{"upper":0.03})]:

    sub = waf[waf["gwcode"].apply(lambda x: x in thresh(waf,**args))]

    plt.clf()

    fig,ax = plt.subplots()
    fig.set_size_inches((10,5))
    ax = sns.lineplot(x="year",y="combined",hue="country.name.en",
        data=sub,ax=ax)

    ax.set(ylim=(0,1))

    plt.xlabel("Year")
    plt.ylabel("P(conflict)")

    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[1:],labels=labels[1:],bbox_to_anchor=(1.3,1.01))
    plt.subplots_adjust(right=0.78)

    fname = f"out/{name}_tl.png"
    plt.savefig(fname)
    print(f"Wrote {fname}")

ssaf = pred[pred["un.regionsub.name"] == "Sub-Saharan Africa"]
shp = shp[shp["GWCODE"].apply(lambda x: x in ssaf["gwcode"].values)]

xmin,ymin,xmax,ymax = shp.total_bounds
ylim = (ymin + 1500000,ymax + 400000)
xlim = (xmin + 500000 ,xmax - 500000)

for aggFn in ["min","max","mean"]:
    agg = (ssaf[["gwcode","combined"]]
        .groupby("gwcode")
        .agg(aggFn)
    )
    mapData = shp.merge(agg,left_on="GWCODE",right_on="gwcode")

    plt.clf()
    fig,ax = plt.subplots()
    fig.set_size_inches((10,8))
    ax = mapData.plot(column="combined",legend=True,
        legend_kwds={"label":"P(conflict)"},
        ax=ax,cmap="coolwarm")
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    fname = f"out/{aggFn}_map.png"
    plt.title(f"P(conflict) {aggFn.title()} 2010-2050")
    plt.savefig(fname)
    print(f"Wrote {fname}")

eth = pred[pred["country.name.en"] == "Ethiopia"]
plt.clf()
sns.lineplot(x="year",y="combined",data=eth)
plt.title("Ethiopia P(conflict) 2010-2050")
plt.xlabel("Year")
plt.ylabel("P(conflict)")
plt.ylim((0,1))
plt.savefig("out/eth.png")
print("Wrote out/eth.png")
