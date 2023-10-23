from disquestion import Bot

bot = Bot(dataset_file="dataset.json")

while True:
    question = input("You: ")
    print(bot.ask(question))