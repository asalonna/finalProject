from textx import metamodel_from_file
import random

class Question(object):

    def __init__(self):
        self.questionText = ""
        self.answerText = ""

    def __str__(self):
        return self.questionText

    def interpret(self, model, question_seed):
        for c in model.content:
            random.seed(question_seed)
            if c.__class__.__name__ == "Text":
                self.questionText = self.questionText + c.x
            elif c.__class__.__name__ == "Field":
                self.questionText =self.questionText  + " " + c.x + " "
            elif c.__class__.__name__ == "RandOrder":
                arr = c.item
                random.shuffle(arr)
                self.questionText =self.questionText  + " " +str(arr) + " "
            elif c.__class__.__name__ == "RandInt":
                self.questionText = self.questionText + " " + str(random.randint(c.x,c.y)) + " "
            elif c.__class__.__name__ == "RandFloat":
                self.questionText = self.questionText + " " + str(random.uniform(c.x,c.y)) + " "
        
        for a in model.answerContents:
            if a.__class__.__name__ == "Text":
                self.answerText = self.answerText + a.x

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
