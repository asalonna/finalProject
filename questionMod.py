from textx import metamodel_from_file
import random


class Question(object):

    def __init__(self):
        self.questionText = ""
        self.answerText = ""
        self.variables = {}

    def __str__(self):
        return self.questionText

    def interpret(self, model, question_seed):
        for c in model.content:
            random.seed(question_seed)

            if c.__class__.__name__ == "Text":
                self.questionText = self.questionText + c.x

            elif c.__class__.__name__ == "Field":
                self.questionText =self.questionText + c.x

            elif c.__class__.__name__ == "RandOrder":
                arr = c.item
                random.shuffle(arr)
                self.questionText =self.questionText + str(arr)

            elif c.__class__.__name__ == "RandInt":
                randInt = random.randint(c.x,c.y)
                self.variables[c.variableName] = randInt
                self.questionText = self.questionText + str(randInt)

            elif c.__class__.__name__ == "RandFloat":
                randFloat = random.uniform(c.x,c.y)
                self.variables[c.variableName] = randFloat
                self.questionText = self.questionText + str(randFloat)
            
        
        for a in model.answerContents:
            if a.repeat is None:
                repeat = 1
            elif type(a.repeat) == str:
                repeat = self.variables[a.repeat]
            else:
                repeat = a.repeat
            for i in range(repeat):
                if a.contentType.__class__.__name__ == "Text":
                    self.answerText = self.answerText + a.contentType.x

                elif a.contentType.__class__.__name__ == "Order":
                    print(a.contentType.list)
                    for i in range(len(a.contentType.list)):
                        if type(a.contentType.list[i]) == str:
                            a.contentType.list[i] = self.variables[a.contentType.list[i]]
                    a.contentType.list.sort()
                    self.answerText = self.answerText + str(a.contentType.list).strip("[]")

                elif a.contentType.__class__.__name__ == "Sequence":
                    if type(a.contentType.start) == str:
                        a.contentType.start = self.variables[a.contentType.start]
                    if type(a.contentType.end) == str:
                        a.contentType.end = self.variables[a.contentType.end]
                    if type(a.contentType.step) == str:
                        a.contentType.step = self.variables[a.contentType.step]
                    rangeOutput = range(a.contentType.start, a.contentType.end, a.contentType.step)
                    for i in rangeOutput:
                        self.answerText = self.answerText + str(i)
                        if i + a.contentType.step < a.contentType.end:
                            self.answerText = self.answerText + ","
                
                elif a.contentType.__class__.__name__ == "Script":
                    self.answerText = self.answerText + str(eval(a.contentType.script))
                
                elif a.contentType.__class__.__name__ == "Variable":
                    self.answerText = self.answerText + str(self.variables[a.contentType.name])

    def isCorrect(self, answer):
        return answer == self.answerText
    
def verify(strDSL):
    try:
        question_mm = metamodel_from_file('question.tx')
        question_model = question_mm.model_from_str(strDSL)
    except:
        return False
    else:
        return True

def getQuestionObject(question_seed):
    question_mm = metamodel_from_file('question.tx')
    question_model = question_mm.model_from_file('program.qst')
    question = Question()
    question.interpret(question_model, question_seed)
    return question

def getQuestionObjectString(strDSL, question_seed):
    question_mm = metamodel_from_file('question.tx')
    question_model = question_mm.model_from_str(strDSL)
    question = Question()
    question.interpret(question_model, question_seed)
    return question
