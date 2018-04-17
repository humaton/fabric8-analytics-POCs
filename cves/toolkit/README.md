# This repository contains POC for issue #2485

> Assignee: Marek Cermak <macermak@redhat.com>\
> Issue: https://github.com/openshiftio/openshift.io/issues/2485 

### Description

> Mapping CVE entries to actual package names is much easier when we at least know name of a project (e.g. "Apache NiFi", or "Apache POI") that is affected by given vulnerability. Knowing the project name will help us to get better results and less false positives.

#### Input

One [NVD] CVE record.


#### Output

The output of this task should be a function that takes one NVD CVE record
on input and returns list of possible project name candidates.

Having confidence score for each candidate would be nice, but is not necessary.

---

# POC

#### Initial intention:  
Since it is not evident whether the NVD descriptions evince a latent pattern,
the first part of the POC will focus on exploring whether a pattern is present and to what
extent it can be used to predict project name candidates.

If such pattern is discovered, proceed with implementation of classifier and evaluate
its accuracy.


#### Sub tasks
- [x] Have a set of labeled data to train, validate and test accuracy with.
- [x] Discover whether the data evinces latent pattern. 
- [x] Model selection based on the description pattern properties
- [x] Classifier implementation
- [x] Accuracy evaluation

#### Concept

The data will be labeled in two ways.

1) Since the output should be a project name candidate, a correct label for the given description should reflect that. Hence for each description there will be a *classification label* representing correct project name. 

2) However, the Naive Bayes classificator will be used in a way such that it will evaluate each word of the description with a confidence score based on the probability that the word could be the project name. For that, each word has to have a separate *feautre label*, a boolean True (is project name), False (is not).


Such approach requires a certain amount of data preprocessing being done beforehead.

The score for each candidate will be evaluated based on features which will be extracted from the context as well as from the candidate. Feature optimization will be necessary in order to estimate which features affect the resulting accuracy the most.

The **features** were estimated as such:

- current tag
- previous word, previous tag
- following word, following tag
- previous tagged bigram
- fillowing tagged bigram
- vendor/product comparison
- included uppercase characte

The classifier is fed a dictionary of key/value pairs where key is an arbitrary feature name and the value is the evaluated value of the feature.

The accuracy evaluation will be done such that the classifier will be fed a CVE description and it will output an arbitrary amount of candidates (i.e. 3). The prediction is correct if any of these candidates is the correct project name (the classification label).
For the cross-validation, K-Fold validation was used, where *k*=10 and the train set was split into test set by ratio 0.8 (that is 1:5). Such drastical split was used to show how well the model generalizes.

#### Sub tasks evaluation
- The data used for this task was a sub set of the [NVD] record which directly references
GitHub. This allows for labeling the data with the project name infered from the GitHub repository

- To discover a latent pattern, a Naive Bayes Classifier was chosen for a model.
Vanilla feature extractors were based on simple text feature_keys such as positional tags.
[NLTK] was used for these purposes.

- Naive Bayes Classifier provided decent results on the toy data set and hence with feature extractor improvements, it was selected as a base model for this POC.

#### Conclusions

It is apperent that the data follows certain pattern and is therefore possible to predict the candidate with a certain accuracy.

Based on the initial evaluations, the accuracy reaches about 65% based on cross-validation results on the K-Folded training data and over 90% based on evaluation of the test set.

*Note: there was a huge difference in the cross-validation accuracy and evaluation on the test set. A probable explanation should be that it is because of the low amount of training data vs huge amout of test data which was used during K-Fold x-validation.*

The result, however, might not be very accurate since it is unclear whether the training and testing data is clean enough and also it is yet unknown how well the model performs on the real-world data (that is the data not linked to GitHub), since there was no way to automate the testing on such data set.


<br>

Based on the description of the task, the function taking the description as its input and outputting list of *n* possible candidates was implemented. User can choose the number of candidates which should be returned.


There is further feature optimization yet to be done.


[NLTK]: https://www.nltk.org/
[NVD]: https://nvd.nist.gov/


