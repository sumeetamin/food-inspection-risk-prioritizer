"""Train a conservative food-inspection failure-risk baseline from history."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd,joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,average_precision_score
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",required=True);p.add_argument("--date",default="Inspection Date");p.add_argument("--result",default="Results");p.add_argument("--out",default="outputs");a=p.parse_args()
 raw=pd.read_csv(a.input);id_col=next((c for c in raw.columns if c.lower().replace(" ","_")=="inspection_id"),None);duplicate_rows_removed=int(raw[id_col].duplicated().sum()) if id_col else 0
 if id_col:raw=raw.drop_duplicates(subset=id_col,keep="first")
 d=raw[raw[a.result].isin(["Fail","Pass","Pass w/ Conditions"])].copy();d["inspection_date"]=pd.to_datetime(d[a.date],errors="coerce");d["fail"] = d[a.result].eq("Fail").astype(int)
 d=d.dropna(subset=["inspection_date"]).sort_values("inspection_date").copy()
 # Only prior/business context fields are predictors; free-text findings and IDs are excluded.
 blocked={a.result,a.date,"inspection_date","fail","Violations","Inspection ID","License #","Address","AKA Name","DBA Name"}
 X=d.drop(columns=[c for c in blocked if c in d],errors="ignore");X=X.drop(columns=[c for c in X if c.lower().endswith("id")],errors="ignore");y=d.fail
 unique_dates=np.sort(d.inspection_date.dt.normalize().unique());cutoff=unique_dates[max(0,int(len(unique_dates)*.8)-1)];train_mask=d.inspection_date.dt.normalize()<=cutoff
 Xtr,Xte=X.loc[train_mask],X.loc[~train_mask];ytr,yte=y.loc[train_mask],y.loc[~train_mask]
 if ytr.nunique()<2 or yte.nunique()<2:raise SystemExit("Chronological split must contain both fail and non-fail labels; adjust the date range.")
 num=X.select_dtypes(include="number").columns;cat=X.columns.difference(num)
 prep=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median",add_indicator=True)),("scale",StandardScaler())]),num),("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("ohe",OneHotEncoder(handle_unknown="ignore",min_frequency=10))]),cat)])
 m=Pipeline([("features",prep),("model",LogisticRegression(max_iter=1200,class_weight="balanced"))]);m.fit(Xtr,ytr);pr=m.predict_proba(Xte)[:,1]
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);report={"dataset":"City of Chicago Food Inspections","source":"https://data.cityofchicago.org/resource/4ijn-s7e5.csv","input_sha256":hashlib.sha256(Path(a.input).read_bytes()).hexdigest(),"rows_received":int(len(pd.read_csv(a.input, usecols=[a.date]))),"duplicate_rows_removed":duplicate_rows_removed,"eligible_rows":len(d),"excluded_outcome_rows":int(len(raw)-len(d)),"eligible_outcomes":["Fail","Pass","Pass w/ Conditions"],"failure_definition":"Results exactly equal to Fail; Pass and Pass w/ Conditions are non-fail; non-completion outcomes are excluded.","date_range":[d.inspection_date.min().date().isoformat(),d.inspection_date.max().date().isoformat()],"train_date_end":d.loc[train_mask,"inspection_date"].max().date().isoformat(),"test_date_start":d.loc[~train_mask,"inspection_date"].min().date().isoformat(),"train_rows":len(Xtr),"test_rows":len(Xte),"failure_rate":float(yte.mean()),"roc_auc":float(roc_auc_score(yte,pr)),"average_precision":float(average_precision_score(yte,pr)),"split":"latest 20% of unique calendar dates among the 50,000 most recent source records; no same-day records are split across partitions"}
 (out/"metrics.json").write_text(json.dumps(report,indent=2));pd.DataFrame({"inspection_row":Xte.index,"failure_probability":pr,"observed_failure":yte.values}).to_csv(out/"review_queue.csv",index=False);joblib.dump({"model":m,"features":X.columns.tolist()},out/"model.joblib");print(json.dumps(report,indent=2))
if __name__=="__main__":main()

