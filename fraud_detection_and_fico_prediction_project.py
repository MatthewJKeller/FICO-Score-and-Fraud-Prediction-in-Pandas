# -*- coding: utf-8 -*-
"""Fraud Detection and FICO Prediction Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1f0ZdyU4-x5zj-0CD3qSza46WXbIhPvIV

# **SETUP:**
"""

from google.colab import drive
from sklearn.tree import DecisionTreeClassifier
import random
import pandas as pd
import numpy as np

drive.mount('/content/drive')
!ls "/content/drive/My Drive/archive"

transactions = pd.read_csv('/content/drive/My Drive/archive/50_transactions.csv')
users = pd.read_csv('/content/drive/My Drive/archive/sd254_users.csv')
data = pd.read_csv('/content/drive/My Drive/archive/sd254_users.csv')
cards = pd.read_csv('/content/drive/My Drive/archive/temp_cards.csv')

data.head()

"""# **FICO SCORE PREDICTION:**"""

data.drop(columns=["Person", "Birth Month", "Address", "Apartment", "City", "State", "Zipcode", "Per Capita Income - Zipcode", "Latitude", "Longitude", "Retirement Age"], inplace=True)
all_columns = data.columns.tolist()
all_columns.remove('FICO Score')
all_columns.remove('Num Credit Cards')
data = data[all_columns + ['Num Credit Cards', 'FICO Score']]

data["Gender"] = data["Gender"].apply(lambda x: 0 if x == "Male" else 1)

data["Yearly Income - Person"] = data["Yearly Income - Person"].apply(lambda x: int(x[1:]))

data["Total Debt"] = data["Total Debt"].apply(lambda x: int(x[1:]))

#data["FICO Score"] = data["FICO Score"].apply(lambda x: "Very Low" if x <630 else "Low" if x < 690 else "Medium" if x < 720 else "Good")
data["FICO Score"] = data["FICO Score"].apply(lambda x: "Very Low" if x <650 else "Good")

#data["FICO Score"] = pd.qcut(data["FICO Score"], q=4, labels=["Very Low", "Low", "Medium", "Good"])
data["FICO Score"].value_counts(normalize=True)

data.head()

training = data.sample(frac = 0.8)
test = data.drop(training.index)

training = training[training.columns[-4:]]
test = test[test.columns[-4:]]

training = training.set_index('FICO Score')
test.set_index('FICO Score', inplace=True)

training.head()

training2 = training#.apply(lambda x: (x-x.mean()) / x.std())

test2 = test#.apply(lambda x: (x-x.mean()) / x.std())

training2 = training2.apply(lambda x: x/magnitude(x), axis=1)
test2     = test2.apply(lambda x: x/magnitude(x), axis=1)

similarities = test2.dot(training2.T)

a = similarities.idxmax(axis=1)
sum(a == a.index) / len(a)

def euclidean(x, y):
    return np.linalg.norm(np.array(x[:-1]) - np.array(y[:-1]))

def magnitude(a):
    return np.linalg.norm(np.array(a[:-1]))

def dot_product(a, b):
    return np.dot(np.array(a[:-1]), np.array(b[:-1]))

def cosine_similarity(a, b):
    return dot_product(a, b) / (magnitude(a) * magnitude(b))

similaritiesCos = test.apply(lambda x: training.apply(lambda y: cosine_similarity(x, y), axis=1), axis=1)


similaritiesEuc = test.apply(lambda x: training.apply(lambda y: euclidean(x, y), axis=1), axis=1)

similaritiesEuc.idxmin()

def getCategory(row, similarities, similarity_type="euclidean", k=25):
   test_row_idx = row.name
   similarity_row = similarities.loc[test_row_idx]
   ascending = True if similarity_type == "euclidean" else False
   sorted_similarities = similarity_row.sort_values(ascending=ascending)

   nearest_indices = sorted_similarities.index[1:k+1]

   fico_scores = []
   for idx in nearest_indices:
       if idx < len(training):
           fico_score = training.loc[idx]["FICO Score"]
           fico_scores.append(fico_score)

   value_counts = pd.Series(fico_scores).value_counts()
   return value_counts.idxmax()

test["Predicted FICO Score Euclidean"] = test.apply(lambda row: getCategory(row, similaritiesEuc, "euclidean"), axis=1)
test["Predicted FICO Score Cosine"] = test.apply(lambda row: getCategory(row, similaritiesCos, "cosine"), axis=1)

accuracy_euc = (test["FICO Score"] == test["Predicted FICO Score Euclidean"]).mean()
accuracy_cos = (test["FICO Score"] == test["Predicted FICO Score Cosine"]).mean()

TruePositiveEuc = len(test[(test["FICO Score"] == "Good") & (test["Predicted FICO Score Euclidean"] == "Good")])
FalsePositiveEuc = len(test[(test["FICO Score"] != "Good") & (test["Predicted FICO Score Euclidean"] == "Good")])
FalseNegativeEuc = len(test[(test["FICO Score"] == "Good") & (test["Predicted FICO Score Euclidean"] != "Good")])
TrueNegativeEuc = len(test[(test["FICO Score"] != "Good") & (test["Predicted FICO Score Euclidean"] != "Good")])

f1ScoreEuc = 2 * (TruePositiveEuc / (2 * TruePositiveEuc + FalsePositiveEuc + FalseNegativeEuc))
precisionEuc = TruePositiveEuc / (TruePositiveEuc + FalsePositiveEuc)
recallEuc = TruePositiveEuc / (TruePositiveEuc + FalseNegativeEuc)

print("Euclidean:")
print(f"F1-Score: {f1ScoreEuc:.2%}")
print(f"Precision: {precisionEuc:.2%}")
print(f"Recall: {recallEuc:.2%}")
print(f"Euclidean Accuracy: {accuracy_euc:.2%}")

TruePositiveCos = len(test[(test["FICO Score"] == "Good") & (test["Predicted FICO Score Cosine"] == "Good")])
FalsePositiveCos = len(test[(test["FICO Score"] != "Good") & (test["Predicted FICO Score Cosine"] == "Good")])
FalseNegativeCos = len(test[(test["FICO Score"] == "Good") & (test["Predicted FICO Score Cosine"] != "Good")])
TrueNegativeCos = len(test[(test["FICO Score"] != "Good") & (test["Predicted FICO Score Cosine"] != "Good")])
print("\n")
f1ScoreCos = 2 * (TruePositiveCos / (2 * TruePositiveCos + FalsePositiveCos + FalseNegativeCos))
precisionCos = TruePositiveCos / (TruePositiveCos + FalsePositiveCos)
recallCos = TruePositiveCos / (TruePositiveCos + FalseNegativeCos)

print("Cosine:")
print(f"F1-Score: {f1ScoreCos:.2%}")
print(f"Precision: {precisionCos:.2%}")
print(f"Recall: {recallCos:.2%}")
print(f"Cosine Accuracy: {accuracy_cos:.2%}")


print("\n")
majorityResults = pd.DataFrame()
majorityResults['actual'] = test['FICO Score']
majorityResults['predicted'] = 'Good'
majorityResults.head()

TruePositiveMajority = len(majorityResults[(majorityResults['actual'] == 'Good') & (majorityResults['predicted'] == 'Good')])
FalsePositiveMajority = len(majorityResults[(majorityResults['actual'] != 'Good') & (majorityResults['predicted'] == 'Good')])
FalseNegativeMajority = len(majorityResults[(majorityResults['actual'] == 'Good') & (majorityResults['predicted'] != 'Good')])
TrueNegativeMajority = len(majorityResults[(majorityResults['actual'] != 'Good') & (majorityResults['predicted'] != 'Good')])

f1ScoreMajority = 2 * (TruePositiveMajority / (2 * TruePositiveMajority + FalsePositiveMajority + FalseNegativeMajority))
precisionMajority = TruePositiveMajority / (TruePositiveMajority + FalsePositiveMajority)
recallMajority = TruePositiveMajority / (TruePositiveMajority + FalseNegativeMajority)

print("Majority Class Classifier:")
print(f"F1-Score: {f1ScoreMajority:.2%}")
print(f"Precision: {precisionMajority:.2%}")
print(f"Recall: {recallMajority:.2%}")
majorityClassAccuracy = len(test[(test["FICO Score"] == "Good")]) / len(test)
print(f"Majority Class Accuracy: {majorityClassAccuracy:.2%}")

print("\n")
randomResults = pd.DataFrame()
randomResults['actual'] = test['FICO Score']
randomResults['predicted'] = np.random.choice(['Very Low', 'Low', 'Medium', 'Good'], size=len(test))
randomResults.head()

TruePositiveRandom = len(randomResults[(randomResults['actual'] == 'Good') & (randomResults['predicted'] == 'Good')])
FalsePositiveRandom = len(randomResults[(randomResults['actual'] != 'Good') & (randomResults['predicted'] == 'Good')])
FalseNegativeRandom = len(randomResults[(randomResults['actual'] == 'Good') & (randomResults['predicted'] != 'Good')])
TrueNegativeRandom = len(randomResults[(randomResults['actual'] != 'Good') & (randomResults['predicted'] != 'Good')])

f1ScoreRandom = 2 * (TruePositiveRandom / (2 * TruePositiveRandom + FalsePositiveRandom + FalseNegativeRandom))
precisionRandom = TruePositiveRandom / (TruePositiveRandom + FalsePositiveRandom)
recallRandom = TruePositiveRandom / (TruePositiveRandom + FalseNegativeRandom)

print("Random Classifier:")
print(f"F1-Score: {f1ScoreRandom:.2%}")
print(f"Precision: {precisionRandom:.2%}")
print(f"Recall: {recallRandom:.2%}")
randomClassAccuracy = len(test[(test["FICO Score"] == "Good")]) / len(test)
print(f"Random Class Accuracy: {randomClassAccuracy:.2%}")

test.head(5)

def naive_bayes_predict(training, test):
    features = training.iloc[:, :-3]
    priors = training['FICO Score'].value_counts(normalize=True)
    likelihoods = pd.DataFrame(index=features.columns, columns=priors.index)

    for score in priors.index:
        score_data = training[training['FICO Score'] == score]
        for feature in features.columns:
            feature_values = pd.to_numeric(score_data[feature], errors='coerce')
            likelihoods.loc[feature, score] = (len(feature_values[feature_values > 0]) + 1) / (len(score_data) + 2)

    predictions = []
    for _, row in test.iterrows():
        scores = {category: np.log(prior) for category, prior in priors.items()}
        for feature in features.columns:
            feature_value = pd.to_numeric(row[feature], errors='coerce')
            if pd.notna(feature_value) and feature_value > 0:
                for category in scores:
                    scores[category] += np.log(likelihoods.loc[feature, category])
        predictions.append(max(scores.items(), key=lambda x: x[1])[0])
    return predictions

test['Predicted FICO Score NB'] = naive_bayes_predict(training, test)

TruePositiveNB = len(test[(test["FICO Score"] == "Good") & (test["Predicted FICO Score NB"] == "Good")])
FalsePositiveNB = len(test[(test["FICO Score"] != "Good") & (test["Predicted FICO Score NB"] == "Good")])
FalseNegativeNB = len(test[(test["FICO Score"] == "Good") & (test["Predicted FICO Score NB"] != "Good")])
TrueNegativeNB = len(test[(test["FICO Score"] != "Good") & (test["Predicted FICO Score NB"] != "Good")])

f1ScoreNB = 2 * (TruePositiveNB / (2 * TruePositiveNB + FalsePositiveNB + FalseNegativeNB))
precisionNB = TruePositiveNB / (TruePositiveNB + FalsePositiveNB)
recallNB = TruePositiveNB / (TruePositiveNB + FalseNegativeNB)
accuracy_nb = len(test[(test["FICO Score"] == "Good")]) / len(test)

print("Naive Bayes:")
print(f"F1-Score: {f1ScoreNB:.2%}")
print(f"Precision: {precisionNB:.2%}")
print(f"Recall: {recallNB:.2%}")
print(f"Naive Bayes Accuracy: {accuracy_nb:.2%}")

"""# **FRAUD DETECTION:**"""

transactions['Amount'] = transactions['Amount'].apply(lambda x: float(x[1:]))

def modify_zip(row):
  if not pd.isna(row['Zip']):
    return row['Zip']
  elif row['Merchant City'] == 'ONLINE':
      return 0
  else:
    return -1

transactions['Zip'] = transactions.apply(lambda x: modify_zip(x), axis = 1)

binary_transactions = transactions.drop(columns = ['Merchant City', 'Use Chip', 'Time', 'Month', 'Year', 'MCC', 'Day', 'Time', 'Year', 'Month', 'Errors?'])
x = pd.get_dummies(transactions['Use Chip'])

transactions['Time'] = transactions['Time'].apply(lambda x: 'time_' + x.split(':')[0])
x2 = pd.get_dummies(transactions['Time'])

bins = [1990, 1994, 1999, 2004, 2009, 2014, 2020]
labels = ['1990+', '1995+', '2000+', '2005+', '2010+', '2015+']
transactions['Year Cat'] = pd.cut(transactions['Year'], bins = bins, labels = labels)
x3 = pd.get_dummies(transactions['Year Cat'])

bins = [0, 10, 20, 32]
labels = ['early_month',  'mid_month', 'end_month']
transactions['days Cat'] = pd.cut(transactions['Day'], bins = bins, labels = labels)
x4 = pd.get_dummies(transactions['days Cat'])

bins = [0, 3, 6, 9, 13]
labels = ['Quarter 1',  'Quarter 2', 'Quarter 3', 'Quarter 4']
transactions['Month Cat'] = pd.cut(transactions['Month'], bins = bins, labels = labels)
x5 = pd.get_dummies(transactions['Month Cat'])

x6 = pd.get_dummies(transactions['Errors?'])

binary_transactions = pd.concat([binary_transactions, x, x2, x3, x4, x5, x6], axis = 1)

binary_transactions.drop(columns = ['Merchant State'], inplace = True)

binary_transactions['Is Fraud?'].replace({'Yes': 1, 'No': 0})

train = binary_transactions.sample(frac = .8)

test = binary_transactions.drop(train.index)

X_train = train.apply(lambda x: pd.Series(x), axis = 1)
X_test  = test.apply(lambda x: pd.Series(x), axis = 1)
y_train = train['Is Fraud?']
y_test = test['Is Fraud?']

tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_train, y_train)

for c in binary_transactions.columns:
  if len(binary_transactions[binary_transactions[c].isna()]) != 0:
    print(c)

binary_cards = cards.drop(columns = ['Card Number',	'Expires',	'CVV', 'Card Brand', 'Card Type'])

x = pd.get_dummies(cards[['Card Brand', 'Card Type']])

binary_cards['Has Chip'].replace({'YES': 1, 'NO': 0}, inplace = True)
binary_cards['Credit Limit'] = binary_cards['Credit Limit'].apply(lambda x: float(x[1:]))
binary_cards['Acct Open Date'] = binary_cards['Acct Open Date'].apply(lambda x: "".join(x.split('/')[::-1]))
binary_cards['Card on Dark Web'].replace({'No': 0, 'Yes': 1}, inplace = True)
binary_cards = pd.concat([binary_cards, x], axis = 1)
binary_cards['Acct Open Date'] = cards['Acct Open Date'].apply(lambda x: int("".join(x.split('/')[::-1])))

binary_cards.loc[binary_cards['std_legit_spending'].isna(), 'std_legit_spending'] = 1 # it is only for two of them, which are not in the transactions subset so I think it is fine

for c in binary_cards.columns:
  if len(binary_cards[binary_cards[c].isna()]) != 0:
    print(c)

transactions[(transactions['User'] == 255) & (transactions['Card']) == 3]

users['User'] = users.index
users['Gender'].replace({'Female': 1, 'Male': 0}, inplace = True)
bins = [1917, 1929, 1939, 1949, 1959, 1969, 1979, 1989, 2003]
labels = ['birth_year_1918+', 'birth_year_1930s', 'birth_year_1940s', 'birth_year_1950s', 'birth_year_1960s', 'birth_year_1970s', \
          'birth_year_1980s', 'birth_year_1990+']
users['birth_year Cat'] = pd.cut(users['Birth Year'], bins=bins, labels=labels)
x = pd.get_dummies(users['birth_year Cat'])


labels = ['early retirement', 'below average retirement', 'above average retirement', 'late retirment']
users['retirement Cat'] = pd.qcut(users['Retirement Age'], q = 4, labels = labels)
x4 = pd.get_dummies(users['retirement Cat'])

bins = [0, 629, 689, 719, 851]
labels = ['Very Low FICO',  'Low FICO', 'Medium FICO', 'Good FICO']
users['FICO Cat'] = pd.cut(users['FICO Score'], bins = bins, labels = labels)
x5 = pd.get_dummies(users['FICO Cat'])

binary_users = users.drop(columns = ['FICO Score', 'Retirement Age', 'Birth Year', 'Address', 'Apartment', 'City', 'Birth Month', 'Current Age', \
                                     'Latitude', 'Longitude', 'FICO Cat', 'retirement Cat', 'birth_year Cat', 'Person'])
binary_users = pd.concat([binary_users, x, x4, x5], axis = 1)

binary_users['Per Capita Income - Zipcode'] = binary_users['Per Capita Income - Zipcode'].apply(lambda x: float(x[1:]))
binary_users['Yearly Income - Person'] = binary_users['Yearly Income - Person'].apply(lambda x: float(x[1:]))
binary_users['Total Debt'] = binary_users['Total Debt'].apply(lambda x: float(x[1:]))

for c in binary_users.columns:
  if len(binary_users[binary_users[c].isna()]) != 0:
    print(c)

len(binary_users[binary_users['Gender'].isna()])

merge = pd.merge(binary_transactions, binary_cards, on=['User', 'Card'], how='left', suffixes=('_transactions', '_cards'))
merge = pd.merge(merge, binary_users, on=['User'], how='left', suffixes=('_merged', '_users'))
merge['Is Fraud?'].replace({'Yes': 1, 'No': 0}, inplace = True)
merge['in_state'] = merge.apply(lambda x: x['Merchant State'] == x['State'], axis = 1)
merge.drop(columns = ['Merchant State', 'State'], inplace = True)
cols = [c for c in merge.columns if c != 'Is Fraud?'] + ['Is Fraud?']
merge = merge[cols]

for c in merge.columns:
    # Check if the column data type is not one of the specified types
    if not (np.issubdtype(merge[c].dtype, np.number) or merge[c].dtype == bool):
        print(f'is not a number {c}')
    if len(merge[merge[c].isna()]) != 0:
      print(f'is na {c}')

merge.info()

transactions = pd.read_csv('/content/drive/My Drive/archive/cosine_holy_grail.csv')
transactions.drop(columns = ['Unnamed: 0'], inplace = True)
merge = transactions

merge

merge.drop(columns = ["in_US", 'in_state', 'is_suspicious_amount'], inplace = True)

merge

def true_positive(df, positive):
  return len(df[(df['x'] == positive) & (df['y'] == positive)])

def true_negative(df, positive):
  return len(df[(df['x'] == (1-positive)) & df['y'] == (1-positive)])

def false_positive(df, positive):
  return len(df[(df['x'] == positive) & (df['y'] == (1 - positive))])

def false_negative(df, positive):
  return len(df[(df['x'] == (1 - positive)) & df['y'] == positive])

def get_precision(df, positive):
  denominator = (true_positive(df, positive) + false_positive(df, positive))
  if denominator == 0:
    return 0
  else:
    return true_positive(df, positive)/denominator

def get_recall(df, positive):
  denominator = (true_positive(df, positive) + false_negative(df, positive))
  if denominator == 0:
    return 0
  else:
    return true_positive(df, positive)/denominator

def get_f1(df, positive):
  denominator = (get_precision(df, positive) + get_recall(df, positive))
  if denominator == 0:
    return 0
  else:
    return 2 * ((get_precision(df, positive) * get_recall(df, positive))/ denominator)

def get_accuracy(df, positive):
  denominator = (true_positive(df, positive) + false_positive(df, positive) + false_negative(df, positive) + true_negative(df, positive))
  if denominator == 0:
    return 0
  else:
    return (true_positive(df, positive) + true_negative(df, positive))/denominator

merge.corr()['Is Fraud?'][merge.corr()['Is Fraud?'].abs().apply(lambda x: x>.10)].abs().sort_values(ascending = False)
merge.corr()['Is Fraud?'][merge.corr()['Is Fraud?'].abs().apply(lambda x: x>.10)].abs().sort_values(ascending = False).index

transactions = merge[['in_US', 'in_state', 'Zip', 'Online Transaction',
       'Swipe Transaction', 'is_suspicious_amount', 'Amount',
       'Num Credit Cards', 'Is Fraud?']]

def magnitude(a):
    return np.linalg.norm(np.array(a[:-1]))

train = transactions.sample(frac = .8)

test = transactions.drop(train.index)

X_train = train.apply(lambda x: pd.Series(x), axis = 1)
X_test  = test.apply(lambda x: pd.Series(x), axis = 1)
X_train.index = train['Is Fraud?']
y_train = train['Is Fraud?']
y_test = test['Is Fraud?']

X_train = X_train.apply(lambda x: x/magnitude(x))
X_test  = X_test.apply(lambda x: x/magnitude(x))
X_train.index = train['Is Fraud?']
cosine_sim = X_test.dot(X_train.T)
x = cosine_sim.apply(lambda row: pd.Series(row.sort_values(ascending=False).head(101).index.tolist()), axis=1)

X_train

target_variable = []

measure = []

support = []

accuracy = []

precision = []

recall = []

f1 = []

for k in [1, 5, 11, 25, 51, 75, 101]:
  temp = x.apply(lambda row: row.head(k).mode(), axis = 1)
  y = y_test.to_frame()
  merge_cosine = temp.join(y)
  merge_cosine.rename(columns = {0: 'x', 'Is Fraud?': 'y'}, inplace = True)
  l = [(0, merge_cosine), (1, merge_cosine)]
  for target, df in l:
    measure.append(k)
    target_variable.append(target)
    support.append(len(transactions[transactions['Is Fraud?'] == target]))
    accuracy.append(get_accuracy(df, target))
    precision.append(get_precision(df, target))
    recall.append(get_recall(df, target))
    f1.append(get_f1(df, target))

result = pd.DataFrame({'Target Variable': target_variable, 'Measure/Model': measure, 'Support': support, 'Acccuracy': accuracy, 'Precision': precision, 'Recall': recall, 'F1-Score': f1})

result

result.groupby('Measure/Model').mean()

l = {}
for name, group in train.groupby(['Is Fraud?']):
  l[name[0]] = ((1+group.sum())/(len(train.columns) + group.sum().sum()))

transactions_sentiment = pd.concat([l[1], l[0]], axis = 1)
transactions_sentiment['sentiment'] = transactions_sentiment.apply(lambda x: x.idxmax(), axis = 1)

l[0]

test_sentiment = pd.DataFrame()
def get_sentiment(row, sent):
  row = pd.Series(row[row >= 1].index)

  x = pd.Series(row.apply(lambda x: np.log(transactions_sentiment.loc[x, sent])))

  return np.log(train['Is Fraud?'].value_counts(normalize = True).loc[sent]) + x.sum()

test_sentiment['Legit'] = test.iloc[:, :-1].apply(lambda row: get_sentiment(row, 0), axis = 1)

test_sentiment['Fraud'] = test.iloc[:, :-1].apply(lambda row: get_sentiment(row, 1), axis = 1)

y_pred = pd.Series(test_sentiment.apply(lambda x: x.idxmax(), axis = 1))

x = y_pred.to_frame()
y = test['Is Fraud?'].to_frame()
bayes = x.join(y)
bayes.rename(columns = {0: 'x', 'Is Fraud?': 'y'}, inplace = True)
bayes.replace({'Fraud': 1, 'Legit': 0}, inplace = True)

bayes['x'].unique()

random_df = x.copy()
random_df[0] = random_df[0].apply(lambda _: random.randint(0,1))
random_df = random_df.join(y)
random_df.rename(columns = {0:'x', 'Is Fraud?':'y'}, inplace = True)

majority_df = x.copy()
majority_df[0] = majority_df[0].apply(lambda _: 0)
majority_df = majority_df.join(y)
majority_df.rename(columns = {0:'x', 'Is Fraud?':'y'}, inplace = True)

l = [(0, euclidean_dist), (1, euclidean_dist)]

target_variable = []

measure = ['bayes', 'bayes', 'cosine', 'cosine', 'majority', 'majority', 'random', 'random']

support = []

accuracy = []

precision = []

recall = []

f1 = []

for target, df in l:
  target_variable.append(target)
  support.append(len(transactions[transactions['Is Fraud?'] == target]))
  accuracy.append(get_accuracy(df, target))
  precision.append(get_precision(df, target))
  recall.append(get_recall(df, target))
  f1.append(get_f1(df, target))

result = pd.DataFrame({'Target Variable': target_variable, 'Measure/Model': measure, 'Support': support, 'Acccuracy': accuracy, 'Precision': precision, 'Recall': recall, 'F1-Score': f1})

result.groupby('Measure/Model').mean()

result

train = transactions.sample(frac = .8)

test = transactions.drop(train.index)

X_train = train.apply(lambda x: pd.Series(x), axis = 1)
X_test  = test.apply(lambda x: pd.Series(x), axis = 1)
X_train.index = train['Is Fraud?']
y_train = train['Is Fraud?']
y_test = test['Is Fraud?']

target_variable = []

measure = []

support = []

accuracy = []

precision = []

recall = []

f1 = []


for k in [1, 3, 5]:
  temp = pd.DataFrame(euc_x.apply(lambda row: row.head(k).mode().iloc[0], axis = 1))
  y = y_test.to_frame()
  merge_euclidean = temp.join(y)
  merge_euclidean.rename(columns = {0: 'x', 'FICO Score': 'y'}, inplace = True)
  l = [(0, merge_euclidean), (1, merge_euclidean)]

  for target, df in l:
    measure.append(k)
    target_variable.append(target)
    support.append(len(data[data['FICO Score'] == target]))
    accuracy.append(get_accuracy(df, target))
    precision.append(get_precision(df, target))
    recall.append(get_recall(df, target))
    f1.append(get_f1(df, target))

result = pd.DataFrame({'Target Variable': target_variable, 'Measure/Model': measure, 'Support': support, 'Acccuracy': accuracy, 'Precision': precision, 'Recall': recall, 'F1-Score': f1})

transactions.info()

test = test.sample(n = 500)

y_test = test.iloc[:, -1]
test = test.iloc[:, :-1]

train = train.iloc[:, 2:-1]

train

train.index = y_train

def train_it(transaction, k):

    #convert transaciton to numpy array
    transaction = transaction.to_numpy()

    #compute difference
    differences = train.to_numpy() - transaction

    distances = np.sum(differences**2, axis=1)

    top_indices = np.argsort(distances)[:k]

    #Use labels to get is fraud label
    top_labels = train.iloc[top_indices, -1]

    return pd.Series(top_labels.index).mode()

euclidean_dist = test.apply(lambda x: train_it(x, k=5), axis=1)

target_variable = []

measure = []

support = []

accuracy = []

precision = []

recall = []

f1 = []
temp_euc = euclidean_dist.apply(lambda x: x.apply(lambda col: y_train.loc[col]), axis = 1)

for k in [1, 3, 5]:
  temp = pd.DataFrame(temp_euc.apply(lambda x: x.head(k).mode().iloc[0], axis = 1))
  y = y_test.to_frame()
  merge_cosine = temp.join(y)
  merge_cosine.rename(columns = {0: 'x', 'Is Fraud?': 'y'}, inplace = True)
  l = [(0, merge_cosine), (1, merge_cosine)]

  for target, df in l:
    measure.append(k)
    target_variable.append(target)
    # support.append(len(transactions[transactions['Is Fraud?'] == target]))
    accuracy.append(get_accuracy(df, target))
    precision.append(get_precision(df, target))
    recall.append(get_recall(df, target))
    f1.append(get_f1(df, target))

result = pd.DataFrame({'Target Variable': target_variable, 'Measure/Model': measure, 'Acccuracy': accuracy, 'Precision': precision, 'Recall': recall, 'F1-Score': f1})

result

# merge_cosine['y'].unique()
y_test.unique()

result.groupby('Measure/Model').mean()

x_eucy = y_test.to_frame()
  merge_cosine = temp.join(y)
  merge_cosine.rename(columns = {0: 'x', 'Is Fraud?': 'y'}, inplace = True)
  l = [(0, merge_cosine), (1, merge_cosine)]

  for target, df in l:
    measure.append(k)
    target_variable.append(target)
    support.append(len(transactions[transactions['Is Fraud?'] == target]))
    accuracy.append(get_accuracy(df, target))
    precision.append(get_precision(df, target))
    recall.append(get_recall(df, target))
    f1.append(get_f1(df, target))

result = pd.DataFrame({'Target Variable': target_variable, 'Measure/Model': measure, 'Support': support, 'Acccuracy': accuracy, 'Precision': precision, 'Recall': recall, 'F1-Score': f1})