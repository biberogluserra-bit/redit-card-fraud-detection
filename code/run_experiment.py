"""Credit-card fraud: leakage-aware, reproducible benchmark.

Real data: OpenML ID 1597. Use --data PATH for local original creditcard.csv.
Examples:
 python run_experiment.py --data data/creditcard.csv --out results
 python run_experiment.py --out results   # fetches OpenML online
 python run_experiment.py --smoke-test --out _smoke_test_only  # NOT real results
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml, make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (average_precision_score, f1_score, precision_score,
                             recall_score, roc_auc_score, confusion_matrix,
                             precision_recall_curve)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.stats import wilcoxon
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline

FEATURES=[f'V{i}' for i in range(1,29)]+['Amount']
SEEDS=[11,23,37,53,71]
MODELS=['LR_base','LR_weighted','LR_SMOTE_0.10','LR_RUS_0.10','LR_threshold_F1','RF_balanced']

def get_data(local=None,smoke=False):
    if smoke:
        X,y=make_classification(n_samples=4500,n_features=29,n_informative=12,
             n_redundant=5,weights=[0.985,0.015],flip_y=0,random_state=42)
        X=pd.DataFrame(X,columns=FEATURES)
        X['Amount']=np.maximum(X['Amount']+7,0)
        X=pd.concat([X,X.iloc[:45]],ignore_index=True)
        y=np.concatenate([y,y[:45]])
        return X,pd.Series(y,name='Class'), 'SYNTHETIC SMOKE TEST ONLY'
    if local is not None:
        df=pd.read_csv(local)
        origin=str(local)
    else:
        try:
            fetched=fetch_openml(data_id=1597,as_frame=True,parser='auto')
            df=fetched.frame.copy()
            if 'Class' not in df.columns: df['Class']=fetched.target
        except Exception as err:
            print('scikit-learn OpenML erişimi başarısız, openml istemcisi deneniyor:',str(err)[:120])
            import openml
            d=openml.datasets.get_dataset(1597)
            xx,yy,_,_=d.get_data(target=d.default_target_attribute,dataset_format='dataframe')
            df=xx.copy();df['Class']=yy
        origin='OpenML ID 1597, downloaded during execution'
    missing=set(FEATURES+['Class'])-set(df.columns)
    if missing: raise ValueError(f'Missing dataset columns: {missing}')
    # OpenML 1597 omits Time; drop original Time if CSV was supplied.
    X=df[FEATURES].apply(pd.to_numeric,errors='raise').astype('float64')
    y=pd.to_numeric(df['Class'],errors='raise').astype(int)
    if set(y.unique())!={0,1}: raise ValueError('Expected both class labels 0 and 1.')
    if X.isna().sum().sum()!=0 or y.isna().sum()!=0: raise ValueError('Missing values!')
    return X.reset_index(drop=True),y.reset_index(drop=True),origin

def model_factory(name,seed):
    lr=lambda weight=None: LogisticRegression(max_iter=1200,solver='lbfgs',
                                             class_weight=weight,random_state=seed)
    if name in ['LR_base','LR_threshold_F1']:
        return make_pipeline(StandardScaler(),lr())
    if name=='LR_weighted': return make_pipeline(StandardScaler(),lr('balanced'))
    if name=='LR_SMOTE_0.10':
        return ImbPipeline([('scale',StandardScaler()),
            ('smote',SMOTE(sampling_strategy=0.10,k_neighbors=5,random_state=seed)),
            ('model',lr())])
    if name=='LR_RUS_0.10':
        return ImbPipeline([('scale',StandardScaler()),
            ('rus',RandomUnderSampler(sampling_strategy=0.10,random_state=seed)),
            ('model',lr())])
    if name=='RF_balanced':
        return RandomForestClassifier(n_estimators=70,max_depth=12,
                         min_samples_leaf=2,class_weight='balanced_subsample',
                         n_jobs=-1,random_state=seed)
    raise KeyError(name)

def grouping(X):
    # Hash all 29 feature columns; same observed features kept in one split.
    return pd.util.hash_pandas_object(X,index=False).to_numpy()

def group_split(X,y,groups,seed=42,n_splits=5):
    splitter=StratifiedGroupKFold(n_splits=n_splits,shuffle=True,random_state=seed)
    tr,ev=next(splitter.split(X,y,groups))
    if y.iloc[tr].nunique()!=2 or y.iloc[ev].nunique()!=2:
        raise RuntimeError('A split lost one label; change fold seed or grouping policy.')
    return tr,ev

def optimal_f1_threshold(y,prob):
    p,r,thresholds=precision_recall_curve(y,prob)
    f=2*p[:-1]*r[:-1]/np.maximum(1e-12,p[:-1]+r[:-1])
    if len(f)==0: return 0.5
    # Ties: choose highest threshold among equal F1 candidates.
    ix=np.where(f>=np.nanmax(f)-1e-12)[0][-1]
    return float(thresholds[ix])

def score(y,prob,threshold=.5):
    pred=(prob>=threshold).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return dict(ap=float(average_precision_score(y,prob)),
                roc_auc=float(roc_auc_score(y,prob)),
                precision=float(precision_score(y,pred,zero_division=0)),
                recall=float(recall_score(y,pred,zero_division=0)),
                f1=float(f1_score(y,pred,zero_division=0)),
                tp=int(tp),fp=int(fp),fn=int(fn),tn=int(tn),
                illustrative_cost=int(fp+10*fn),threshold=float(threshold))

def execute(out_dir,local=None,smoke=False):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    X,y,origin=get_data(local,smoke)
    groups=grouping(X)
    summary_meta=dict(origin=origin,rows=len(y),features=len(FEATURES),fraud=int(y.sum()),
           fraud_rate=float(y.mean()),duplicates=int(X.duplicated().sum()),
           missing=int(X.isna().sum().sum()),study_status=('TECHNICAL_SMOKE_TEST_ONLY' if smoke else 'REAL_DATA'))
    # Hold-out test is segregated once, before any preprocessing or balancing.
    dev_ix,test_ix=group_split(X,y,groups,seed=42,n_splits=5)
    Xdev,ydev=X.iloc[dev_ix].reset_index(drop=True),y.iloc[dev_ix].reset_index(drop=True)
    gdev=groups[dev_ix]
    Xtest,ytest=X.iloc[test_ix],y.iloc[test_ix]
    summary_meta['test_size']=int(len(test_ix));summary_meta['test_fraud']=int(ytest.sum())
    records=[]
    run_seeds=SEEDS[:3] if smoke else SEEDS
    for seed in run_seeds:
        # dev -> outer train / outer validation (comparison), group aware.
        otr,oval=group_split(Xdev,ydev,gdev,seed=seed,n_splits=5)
        # outer train -> inner fit / calibration (threshold), group aware.
        xin,yin=Xdev.iloc[otr].reset_index(drop=True),ydev.iloc[otr].reset_index(drop=True)
        gin=gdev[otr]
        itr,ical=group_split(xin,yin,gin,seed=seed+100,n_splits=5)
        Xfit,yfit=xin.iloc[itr],yin.iloc[itr]
        Xcal,ycal=xin.iloc[ical],yin.iloc[ical]
        Xval,yval=Xdev.iloc[oval],ydev.iloc[oval]
        fitted={}
        for name in MODELS:
            base='LR_base' if name=='LR_threshold_F1' else name
            if base not in fitted:
                model=model_factory(base,seed)
                model.fit(Xfit,yfit)
                fitted[base]=model
            model=fitted[base]
            threshold=.5
            if name=='LR_threshold_F1':
                threshold=optimal_f1_threshold(ycal,model.predict_proba(Xcal)[:,1])
            metrics=score(yval,model.predict_proba(Xval)[:,1],threshold)
            records.append(dict(seed=seed,model=name,train_n=len(Xfit),
                 calibration_n=len(Xcal),validation_n=len(Xval),validation_frauds=int(yval.sum()),**metrics))
        print('Finished seed',seed,flush=True)
    raw=pd.DataFrame(records)
    raw.to_csv(out/'cv_repeated_results.csv',index=False)
    metrics=['ap','roc_auc','precision','recall','f1','illustrative_cost']
    mean=raw.groupby('model')[metrics].agg(['mean','std'])
    mean.columns=['_'.join(x) for x in mean.columns]
    mean=mean.sort_values('ap_mean',ascending=False)
    mean.to_csv(out/'cv_summary.csv',float_format='%.6f')
    winner=str(mean.index[0])
    # Pair-wise testing on five DEV splits: exploratory, non-independent folds.
    tests=[]
    baseline=raw[raw.model=='LR_base'].set_index('seed')
    for name in MODELS:
        if name=='LR_base':continue
        candidate=raw[raw.model==name].set_index('seed')
        differences=(candidate.loc[baseline.index,'ap']-baseline['ap']).values
        try: p=float(wilcoxon(differences,zero_method='wilcox',alternative='two-sided').pvalue)
        except ValueError:p=None
        tests.append(dict(model=name,vs='LR_base',mean_delta_ap=float(differences.mean()),
                    paired_effect_size_dz=(float(differences.mean()/differences.std(ddof=1))
                                           if len(differences)>1 and differences.std(ddof=1)>1e-12 else None),
                    wilcoxon_p_unadjusted=(p if p is not None and np.isfinite(p) else None),n=len(differences)))
    pd.DataFrame(tests).to_csv(out/'exploratory_paired_tests.csv',index=False)
    # Fit baseline and selected final model using only development data.
    # Dev split into fit/calibration; test remains untouched until evaluation.
    fin_fit,fin_cal=group_split(Xdev,ydev,gdev,seed=2026,n_splits=5)
    Xfit,yfit=Xdev.iloc[fin_fit],ydev.iloc[fin_fit]
    Xcal,ycal=Xdev.iloc[fin_cal],ydev.iloc[fin_cal]
    final={}
    test_probs={}
    for name in sorted(set(['LR_base',winner])):
        base='LR_base' if name=='LR_threshold_F1' else name
        m=model_factory(base,seed=2026)
        m.fit(Xfit,yfit)
        cutoff=(optimal_f1_threshold(ycal,m.predict_proba(Xcal)[:,1]) if name=='LR_threshold_F1' else 0.5)
        ptest=m.predict_proba(Xtest)[:,1]
        test_probs[name]=ptest
        final[name]=score(ytest,ptest,cutoff)
        final[name]['model']=name
        final[name]['test_n']=len(ytest)
        final[name]['test_positive']=int(ytest.sum())
        pr,rec,_=precision_recall_curve(ytest,ptest)
        plt.figure(figsize=(6,4));plt.plot(rec,pr,label=f'{name} AP={final[name]["ap"]:.3f}')
        plt.xlabel('Recall');plt.ylabel('Precision');plt.title('Untouched holdout / PR curve');plt.legend()
        plt.tight_layout();plt.savefig(out/f'pr_test_{name}.png',dpi=170);plt.close()
    pd.DataFrame(list(final.values())).to_csv(out/'final_untouched_test_results.csv',index=False)
    # Exploratory 95% CIs by bootstrapping duplicated-feature groups in the holdout.
    # Shared group resamples make comparisons paired; representativeness remains limited.
    rng=np.random.default_rng(2026)
    unique_g,inverse=np.unique(groups[test_ix],return_inverse=True)
    row_groups=[np.flatnonzero(inverse==j) for j in range(len(unique_g))]
    bt={name:[] for name in test_probs}
    for _ in range(200 if not smoke else 30):
        sampled=rng.integers(0,len(unique_g),size=len(unique_g))
        ix=np.concatenate([row_groups[j] for j in sampled])
        yt=ytest.to_numpy()[ix]
        if yt.min()==yt.max():continue
        for name,probs in test_probs.items():
            bt[name].append(average_precision_score(yt,probs[ix]))
    boot=[]
    for name,values in bt.items():
        boot.append(dict(model=name,metric='AP',ci_low_2_5=float(np.percentile(values,2.5)),
                         ci_high_97_5=float(np.percentile(values,97.5)),replicates=len(values),
                         note='Exploratory grouped holdout bootstrap; not population CI'))
    pd.DataFrame(boot).to_csv(out/'test_bootstrap_confidence_intervals.csv',index=False)
    summary_meta['selected_by_dev_cv_ap']=winner
    summary_meta['cv_repetitions']=len(run_seeds)
    summary_meta['preprocessing']='StandardScaler fit only to fit subset in Pipeline; SMOTE/RUS fit subset only'
    summary_meta['test_policy']='Test reserved; winner selected by DEV validation AP only'
    summary_meta['cost_warning']='FP=1, FN=10 illustrative units only, NOT observed financial loss'
    summary_meta['caveats']='No Time in OpenML 1597; no chronological holdout possible; repeated correlated splits; no population representativeness established'
    (out/'metadata.json').write_text(json.dumps(summary_meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':summary_meta['study_status'],'winner':winner,'final':final},ensure_ascii=False,indent=2))
    return out

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--data',default=None)
    a.add_argument('--out',default='results')
    a.add_argument('--smoke-test',action='store_true')
    args=a.parse_args()
    execute(args.out,args.data,args.smoke_test)
