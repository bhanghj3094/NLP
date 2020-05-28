# Natural Language Processing

This is a repository for coursework in Natural Language Processing in CS372, 2020 Spring, KAIST.

## About the Course and NLTK

Please refer to the link : [Course](http://nlpcl.kaist.ac.kr/~cs372_2020/index.php), [NLTK Book](http://www.nltk.org/book/)

## About the Coursework

### HW1

Find pairs of expressions that are 'intensity-modifying'.

For example,

> Extol, praise _highly_  
> Destitute, _very_ poor

### HW2

Find pairs of words where one word is both 'restricting' and 'intensity-modifying' another word.

For example,

> _pitch_ black  
> _dead_ center  
> _deathly_ sick  
> _stark_ contrast

### HW3

Find sentences that has most occurrence of heteronyms.  
Single occurrence of heteronym is also counted. 

* Homograph: Same letters, different meaning.  
* Heteronym: Among homographs, different pronounciation. 

For example, 

> contains: _'wind(air)'_ + _'wind(tie)'_ + _'tear(pull apart)'_ + _'tear(droplet)'_   
> contains: _'wind(air)'_ + _'wind(tie)'_ + _'tear(pull apart)'_  
> ...


### HW4

Extract relations from MEDLINE database. *<X, ACTION, Y>*  
Collect 100 sentences with annotated relations.  
Use 80 sentences to train, test module with remaining 20 sentences. 

For example, 

> Inorganic phosphate inhibited HPr kinase but activated HPR phosphatase.  
> => <Inorganic phosphate, inhibited, HPr kinase>  
> => <Inorganic phosphate, activated, HPR phosphatase>

> All vasodilators activated K-Cl cotransport in LK SRBCs and HYZ in VSMCs, and this activation was inhibited by calyculin and genistein, two inhibitors of K-Cl cotransport.  
> => <All vasodilators, activated, K-CI cotransport>  
> => <All vasodilators, activated, HYZ>  
> => <this activation, was inhibited by, calyculin> OR <calyculin, inhibited, this activation>  
> => <this activation, was inhibited by, genistein> OR <genistein, inhibited, this activation>  
> => <this activation, was inhibited by, two inhibitors> OR <two inhibitors, inhibited, this activation>

## Environments

Refer to how to setup [here](./setup).
