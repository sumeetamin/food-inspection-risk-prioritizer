"""Train a conservative food-inspection failure-risk baseline from history."""
import argparse,json
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
 d=pd.read_csv(a.input);d["inspection_date"]=pd.to_datetime(d[a.date],errors="coerce");d["fail"] = d[a.result].astype(str).str.contains(r"\bfail\b",case=False,regex=True).astype(int)
 d=d.dropna(subset=["inspection_date"]).sort_values("inspection_date").copy()
 # Only prior/business context fields are predictors; free-text findings and IDs are excluded.
 blocked={a.result,a.date,"inspection_date","Violations","Inspection ID","License #","Address","AKA Name","DBA Name"}
 X=d.drop(columns=[c for c in blocked if c in d],errors="ignore");X=X.drop(columns=[c for c in X if c.lower().endswith("id")],errors="ignore");y=d.fail
 cut=int(len(d)*.8);Xtr,Xte=X.iloc[:cut],X.iloc[cut:];ytr,yte=y.iloc[:cut],y.iloc[cut:]
 if ytr.nunique()<2 or yte.nunique()<2:raise SystemExit("Chronological split must contain both fail and non-fail labels; adjust the date range.")
 num=X.select_dtypes(include="number").columns;cat=X.columns.difference(num)
 prep=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median",add_indicator=True)),("scale",StandardScaler())]),num),("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("ohe",OneHotEncoder(handle_unknown="ignore",min_frequency=10))]),cat)])
 m=Pipeline([("features",prep),("model",LogisticRegression(max_iter=1200,class_weight="balanced"))]);m.fit(Xtr,ytr);pr=m.predict_proba(Xte)[:,1]
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);report={"train_rows":len(Xtr),"test_rows":len(Xte),"failure_rate":float(yte.mean()),"roc_auc":float(roc_auc_score(yte,pr)),"average_precision":float(average_precision_score(yte,pr)),"split":"latest 20% of inspection dates"}
 (out/"metrics.json").write_text(json.dumps(report,indent=2));pd.DataFrame({"inspection_row":d.index[cut:],"failure_probability":pr,"observed_failure":yte.values}).to_csv(out/"review_queue.csv",index=False);joblib.dump({"model":m,"features":X.columns.tolist()},out/"model.joblib");print(json.dumps(report,indent=2))
if __name__=="__main__":main()
