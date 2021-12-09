import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import scikitplot
from sklearn.tree import export_graphviz
from subprocess import call

hazard_dict = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3
}

shift_dict = {
    'W': 0,
    'N': 1
}


def convert_with_dict(col, dict):
    for i in range(len(col)):
        col[i] = dict[col[i]]


file_path = './csv_result-seismic-bumps.csv'
data = pd.read_csv(file_path)

# Usunięcie kolumny id - nic nie wnosi
data = data.drop(columns=['id'])

# Transformacja wartości tekstowych na numeryczne
convert_with_dict(data['seismic'], hazard_dict)
convert_with_dict(data['seismoacoustic'], hazard_dict)
convert_with_dict(data['ghazard'], hazard_dict)
convert_with_dict(data['shift'], shift_dict)

# Utworzenie i dodanie własnych atrybutów
data['genergygpuls'] = (data['genergy'] / data['gpuls']
                        ).replace([np.inf, -np.inf], np.nan).fillna(data['genergy'])
data['gdenergydgpuls'] = (
    data['gdenergy'] / data['gdpuls']).replace([np.inf, -np.inf], np.nan).fillna(data['gdenergy'])
data['avgseismic'] = ((data['seismic'] + data['seismoacoustic']) / 2)
data['energygpuls'] = (data['energy'] / data['gpuls']
                       ).replace([np.inf, -np.inf], np.nan).fillna(data['energy'])
data['energynbumps'] = (data['energy'] / data['nbumps']
                        ).replace([np.inf, -np.inf], np.nan).fillna(data['energy'])

x = np.array(data.drop(columns=['class']))
y = np.array(data['class'])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.4)
randomForestCls = RandomForestClassifier()
randomForestCls.fit(x_train, y_train)

export_graphviz(randomForestCls.estimators_[1], out_file='tree.dot', 
                feature_names = data.columns.drop(['class']),
                class_names = 'class',
                rounded = True, proportion = False, 
                precision = 2, filled = True)
call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png'])

y_pred = randomForestCls.predict(x_test)
print('RANDOM FOREST CLASSIFIER ======================================================') 
print('Classification reporty\n',
      sklearn.metrics.classification_report(y_test, y_pred))
conf = sklearn.metrics.confusion_matrix(y_test, y_pred)
print('Confusion matrix\n', conf)
print('Accuracy\n', sklearn.metrics.accuracy_score(y_test, y_pred))
tn, fp, fn, tp = conf.ravel()
print('Specificity\n', tn / (tn+fp))
print('Sensitivity\n', tp / (tp+fn))
scikitplot.metrics.plot_lift_curve(y_test, randomForestCls.predict_proba(x_test))
plt.show()
sklearn.metrics.plot_roc_curve(randomForestCls, x_test, y_test)
plt.show()


gaussianNBCls = GaussianNB()
gaussianNBCls.fit(x_train, y_train)

y_pred = gaussianNBCls.predict(x_test)
print('GAUSSIAN NAIVE BAYES CLASSIFIER ======================================================') 
print('Classification reporty\n',
      sklearn.metrics.classification_report(y_test, y_pred))
conf = sklearn.metrics.confusion_matrix(y_test, y_pred)
print('Confusion matrix\n', conf)
print('Accuracy\n', sklearn.metrics.accuracy_score(y_test, y_pred))
tn, fp, fn, tp = conf.ravel()
print('Specificity\n', tn / (tn+fp))
print('Sensitivity\n', tp / (tp+fn))
scikitplot.metrics.plot_lift_curve(y_test, gaussianNBCls.predict_proba(x_test))
plt.show()
sklearn.metrics.plot_roc_curve(gaussianNBCls, x_test, y_test)
plt.show()
