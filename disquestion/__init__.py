from json import load
from random import choice 
from collections import Counter
from rapidfuzz import fuzz
from markovify import Text

class Bot:
    def __init__(self, dataset_file: str):
        self.dataset_file = dataset_file

        with open(dataset_file, "r") as dataset: 
            self.dataset = load(dataset)

    def refreshDataset(self):
        with open(self.dataset_file, "r") as dataset:
            self.dataset = load(dataset)

    def ask(self, user_input: str, *, threshold: int = 65, corpus_tries: int = 100):
        matches = []
        accurateMatches = Counter()

        for category in self.dataset["dataset"]:
            for topic in self.dataset["dataset"][category]:
                inputPatterns = self.dataset["dataset"][category][topic]["input"]["patterns"]
                inputHighlight = self.dataset["dataset"][category][topic]["input"]["highlight"]

                for sentence in inputPatterns:
                    token_sort_ratio = fuzz.token_sort_ratio(user_input.lower() , sentence)
                    if token_sort_ratio > threshold:
                        topicScore = token_sort_ratio + sum(
                            fuzz.token_sort_ratio(word, sentence) * ((threshold / 100) * (threshold * .04))
                            for highlight in inputHighlight
                            for word in highlight.split()
                            if fuzz.token_sort_ratio(word, sentence) > 80
                        )

                        if topicScore > threshold:
                            print(f"score for {category} > {topic}: {topicScore}")
                            matches.append((category, topic, round(topicScore)))

        for item in matches:
            key = (item[0], item[1])
            accurateMatches[key] += item[2]

        ranks = [[key[0], key[1], value] for key, value in accurateMatches.items()] if accurateMatches else None

        def returnCorpus(ranks):
            topReply = max(ranks, key=lambda x: x[2])
            category, topic, topicScore = topReply[0], topReply[1], topReply[2]

            nest = self.dataset["dataset"][category][topic]["responses"]["nest"]
            corpus = self.dataset["dataset"][category][topic]["responses"]["corpus"]

            if not corpus:
                return returnNest(nest, category, topic, topicScore)

            corpus = Text("\n".join(corpus))
            reply = corpus.make_sentence(tries=corpus_tries)

            return (
                returnNest(nest, category, topic, topicScore)
                if reply is None
                else (reply, category, topic, 0, "corpus")
            )

        def returnNest(nest, category, topic, topicScore):
            reply = choice(nest)
            decodedReply = "".join(choice(words) for words in reply if (word := choice(words)) != "" and not word.__contains__("<end>"))
            return decodedReply, category, topic, topicScore, "nest"

        if ranks:
            return returnCorpus(ranks)

        reply = choice(self.dataset["response-handle"]["no-response"])
        decodedReply = "".join(choice(words) for words in reply if (word := choice(words)) != "" and not word.__contains__("<end>"))
        return decodedReply, "response-handle", "no-response", 0, "error"
