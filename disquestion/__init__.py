from json import load
from random import choice
from rapidfuzz import fuzz
from markovify import Text

def createResponse(response: list):
    res = ""

    for words in response:
        word = choice(words)
        if word != "":
            res += word
            if word.__contains__("<end>"):
                return res.replace("<end>", "")
    
    return res


class Bot:
    def ask(input: str, *, threshold: int = 65, corpus_tries: int = 10, state_size: int = 2, dataset_file: str = "dataset.json"):
        with open(dataset_file, "r") as dataset: dataset = load(dataset)

        matches = []
        accurateMatches = {}

        for category in dataset["dataset"]:
            print(f"debug: reading category > {category}")
            for topic in dataset["dataset"][category]:
                print(f"debug: reading topic > {topic}")

                topicScore = 0
                inputPatterns = dataset["dataset"][category][topic]["input"]["patterns"]
                inputHighlight = dataset["dataset"][category][topic]["input"]["highlight"]

                for sentence in inputPatterns:
                    inputSimilarity = fuzz.token_sort_ratio(input, sentence)

                    if inputSimilarity > threshold:
                        print(f"debug: score result (pattern) :: topic: {topic} | similarity: {round(inputSimilarity)} | sentence: {sentence} ({category})")
                        topicScore += inputSimilarity

                for highlight in inputHighlight:
                    for word in highlight.split():
                        inputSimilarity = fuzz.token_sort_ratio(word, sentence)

                        if inputSimilarity > 80:
                            print(f"debug: score result (highlight) :: topic: {topic} | similarity: {round(inputSimilarity)} | sentence: {sentence} ({category})")
                            topicScore += topicScore * ((threshold / 100) * (threshold * .04))

                if topicScore > threshold:
                    print(f"score for {category} > {topic}: {topicScore}")
                    matches.append((category, topic, round(topicScore)))

        print(matches)

        for item in matches:
            print(item)
            key = (item[0], item[1])
            if key in accurateMatches: accurateMatches[key] += item[2]
            else: accurateMatches[key] = item[2]

        ranks = [[key[0], key[1], value] for key, value in accurateMatches.items()]

        if ranks != []:
            topReply = max(ranks, key=lambda x: x[2])
            category, topic, topicScore = topReply[0], topReply[1], topReply[2]

            nest = dataset["dataset"][category][topic]["responses"]["nest"]
            corpus = dataset["dataset"][category][topic]["responses"]["corpus"]

            if corpus == []:
                reply = choice(nest)
                decodedReply = createResponse(reply)
                return decodedReply, category, topic, topicScore, "nest"

            else:
                corpus = Text("\n".join(corpus))
                reply = corpus.make_sentence(tries=corpus_tries)

                if reply == None:
                    reply = choice(nest)
                    decodedReply = createResponse(reply)
                    return decodedReply, category, topic, topicScore, "nest"

                else:
                    return reply, category, topic, 0, "corpus"

        else:
            reply = choice(dataset["response-handle"]["no-response"])
            decodedReply = createResponse(reply)
            return decodedReply, "response-handle", "no-response", 0, "error"

#while True:
#    msg = input("Chat: ")
#    res = Bot.ask(msg, threshold=65, corpus_tries=100, state_size=4, dataset_file="./dataset/test.json")
#    print(f"the response: {res}")