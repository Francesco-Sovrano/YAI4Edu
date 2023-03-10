# YAI4Edu: Explanatory AI for Education
Using the latest question-answering technology, our e-book software (YAI4Edu, for short) generates on-demand, expandable explanations that can help readers effectively explore teaching materials in a pedagogically productive way. It does this by extracting a specialised knowledge graph from a collection of books or other resources that helps identify the most relevant questions to be answered for a satisfactory explanation. We tested our technology with excerpts from a textbook that teaches how to write legal memoranda in the U.S. legal system.

More details about this code can be found in the following paper:
> ["YAI4Edu: an Explanatory AI to Generate Interactive e-Books for Education"](http://ceur-ws.org/Vol-3192/itb22\_p4\_short8391.pdf)

To address the problem of automatically explaining, we studied how to automatically enhance static educational books by making them more interactive. We did this by reducing the sparsity of relevant information, thereby increasing the explanatory power of the medium while also linking it to a knowledge graph extracted from a collection of supplementary materials. To do so, we exploited a recent theory of explanations from Ordinary Language Philosophy (Sovrano & Vitali, 2022). This theory defines the act of explain- ing as “an illocutionary act of pragmatically answering questions (plural)”. It stresses the subtle and essential difference between simply “answering questions” and “explaining”. This difference is both illocutionary and pragmatic. It involves both informed and pertinent answering implicit questions such as why, how, when, what, who. In addition, it involves tailoring explanations to the specific background knowledge, needs, and goals of the person receiving them.

Assuming that the goal of an educational e-book is to explain something to the reader and consistent with the aforementioned definition of explanations, we built an explanatory process capable, through question-answering, of organising a textbook’s explanatory space to enable a reader to more efficiently and effectively retrieve helpful information. Specifically, our proposed solution consists of a pipeline of Explanatory AI (YAI) algorithms and heuristics to build, on top of textbooks, intelligent interfaces for:
- answering explicit questions asked by a user;
- automatically identifying the topics that can be explained by the contents of a textbook (or any collection of texts);
- generating explanations by anticipating a set of useful (implicit) questions a user might have about the textbook.

Our main contribution is a novel pipeline of YAI for enhancing the explanatory power of a textbook based on an algorithm (called Intelligent Explanation Generator) for identifying the questions best answered by a collection of texts.

To evaluate the Intelligent Explanation Generator, we ran a user-study (whose results are available at [user_study_interface/results](user_study_interface/results)). We compared the explanations generated by our algorithm with those of the following two baseline algorithms:
- a random explanations generator: an algorithm that organises explanations by randomly selecting implicit questions from those answered by the corpus of considered texts;
- a generic explanations generator: an algorithm that uses very generic questions (e.g., why, how, what) instead of those extracted from the text-book, under the assumption that all possible (implicit) questions are instances of such generic questions.


## Usage and Installation
This project has been tested on Debian 9 and macOS Mojave 10.14 with Python 3.9. 

The file system of this repository is organised as follows:
- In folder [user_study_interface](user_study_interface) it is possible to find the results of the user studies discussed in the 2 aforementioned papers and the code used for running the user study (i.e., the client-side interface).
- Folder [yai4edu_interface](yai4edu_interface) contains the client-side part of YAI4Edu.
- Folder [library_server](library_server) contains the server-side part of both user_study_interface and YAI4Edu.
- Folder [packages](packages) contains the libraries used by [library_server](library_server).
- Folder [question_extractor](question_extractor) contains the scripts for training the question extractor available at [question_extractor/data/models/distilt5-disco-qaamr-multi](question_extractor/data/models/distilt5-disco-qaamr-multi). However we did not upload the QAMR (```Michael, Julian, et al. "Crowdsourcing question-answer meaning representations." arXiv preprint arXiv:1711.05885 (2017)```) and QADiscourse (```Pyatkin, Valentina, et al. "QADiscourse--Discourse Relations as QA Pairs: Representation, Crowdsourcing and Baselines." arXiv preprint arXiv:2010.02815 (2020)```).

In the root directory it is possible to find a ```setup.sh``` script to install the software. To run the code, execute the following command ```./server.sh```. After running the "server.sh" script, you can access the the web applications through your browser at [http://localhost:8017](http://localhost:8017) for the user study software, and at [http://localhost:8015](http://localhost:8015) for YAI4Edu.
However, it may take some time (especially without a GPU) to successfully start the web applications because they will need to extract questions. For a quick demo run only the user study software.

In order to successfully launch the aforementioned software you need to: 
- Find the PDF of ```Brostoff, Teresa Kissane, Teresa Brostoff, and Ann Sinsheimer. United States legal language and culture: An introduction to the US common law system. Oxford University Press, 2013``` and add it to [yai4edu_interface/documents](yai4edu_interface/documents) and to [library_server/documents/edu/excerpts](library_server/documents/edu/excerpts).
- Download enough BVA cases by running the script [library_server/documents/bva/bva_scraper.py](library_server/documents/bva/bva_scraper.py).
- Run the script [library_server/documents/edu/encyclopaedia/cornell_law_scraper.py](library_server/documents/edu/encyclopaedia/cornell_law_scraper.py).
- Open [library_server/server_interface.py](library_server/server_interface.py) and check whether the path to the trained model at line 132 is correct. Do the same with [library_server/server_interface_bva.py](library_server/server_interface_bva.py), line 134. The trained model should be at [question_extractor/data/models/distilt5-disco-qaamr-multi](question_extractor/data/models/distilt5-disco-qaamr-multi).

**N.B.** Before being able to run the setup.sh scripts you have to install: virtualenv, python3-dev, python3-pip and make. 


## Citations
This code is free. So, if you use this code anywhere, please cite:
- Francesco Sovrano, Kevin D. Ashley, Peter Brusilovsky, Fabio Vitali: YAI4Edu: an Explanatory AI to Generate Interactive e-Books for Education. iTextbooks@AIED 2022: 31-39

BitTeX citations:
```
@inproceedings{DBLP:conf/aied/SovranoABV22,
  author    = {Francesco Sovrano and
               Kevin D. Ashley and
               Peter Brusilovsky and
               Fabio Vitali},
  editor    = {Sergey A. Sosnovsky and
               Peter Brusilovsky and
               Andrew S. Lan},
  title     = {YAI4Edu: an Explanatory {AI} to Generate Interactive e-Books for Education},
  booktitle = {Proceedings of the Fourth International Workshop on Intelligent Textbooks
               2022 co-located with 23d International Conference on Artificial Intelligence
               in Education {(AIED} 2022), Durham, UK, July 27, 2022},
  series    = {{CEUR} Workshop Proceedings},
  volume    = {3192},
  pages     = {31--39},
  publisher = {CEUR-WS.org},
  year      = {2022},
  url       = {http://ceur-ws.org/Vol-3192/itb22\_p4\_short8391.pdf},
  timestamp = {Tue, 22 Nov 2022 17:50:40 +0100},
  biburl    = {https://dblp.org/rec/conf/aied/SovranoABV22.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```

Thank you!

## Support
For any problem or question please contact me at `cesco.sovrano@gmail.com`
