from textx import metamodel_from_file
import random
import javalang

class Question(object):

    def __init__(self):
        self.questionText = ""
        self.restrictions = ""
        self.answerText = ""
        self.variables = {}
        self.model = None

    def __str__(self):
        return self.questionText

    def interpret(self, model, question_seed):
        self.model = model
        random.seed(question_seed)
        for c in model.content:

            if c.__class__.__name__ == "Text":
                self.questionText = self.questionText + c.x

            elif c.__class__.__name__ == "Field":
                self.questionText =self.questionText + c.x

            elif c.__class__.__name__ == "RandOrder":
                arr = c.item
                random.shuffle(arr)
                self.questionText = self.questionText + str(arr)

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
                    for i in self.variables:
                        if type(self.variables[i]) == int:
                            exec("%s = %d" % (i,self.variables[i]))
                        elif type(self.variables[i]) == float:
                            exec("%s = %f" % (i,self.variables[i]))
                    self.answerText = self.answerText + str(eval(a.contentType.script))

                elif a.contentType.__class__.__name__ == "Variable":
                    self.answerText = self.answerText + str(self.variables[a.contentType.name])

    def isCorrect(self, answer):
        return (''.join(answer.split()).lower() == ''.join(self.answerText.split()).lower())

    def checkCode(self, code):
        tree = javalang.parse.parse(code)
        if_statement = "<class 'javalang.tree.IfStatement'>"
        for_statement = "<class 'javalang.tree.ForStatement'>"
        while_statement = "<class 'javalang.tree.WhileStatement'>"
        INDENT_PER_LEVEL = -3
        
        all_restrictions_valid = True

        for r in self.model.restrictions:
            restriction_valid = False
            listy = [r.x]
            number_of_levels = 0
            while r.nest is not None:
                r = r.nest
                listy.append(r.x)
                number_of_levels += 1
            
            poppy = listy.pop()
            if poppy == 'if':
                for path, node in tree.filter(javalang.tree.IfStatement):
                    node_valid = True
                    listy2 = listy.copy()
                    index = INDENT_PER_LEVEL
                    while len(listy2) > 0:
                        popped = listy2.pop()
                        if popped == 'for':
                            if str(type(path[index])) != for_statement:
                                node_valid = False
                        elif popped == 'if':
                            if str(type(path[index])) != if_statement:
                                node_valid = False
                        elif popped == 'while':
                            if str(type(path[index])) != while_statement:
                                node_valid = False
                        index += INDENT_PER_LEVEL
                    if node_valid == True:
                        restriction_valid = True
            elif poppy == 'for':
                for path, node in tree.filter(javalang.tree.ForStatement):
                    node_valid = True
                    listy2 = listy.copy()
                    index = INDENT_PER_LEVEL
                    while len(listy2) > 0:
                        popped = listy2.pop()
                        if popped == 'for':
                            if str(type(path[index])) != for_statement:
                                node_valid = False
                        elif popped == 'if':
                            if str(type(path[index])) != if_statement:
                                node_valid = False
                        elif popped == 'while':
                            if str(type(path[index])) != while_statement:
                                node_valid = False
                        index += INDENT_PER_LEVEL
                    if node_valid == True:
                        restriction_valid = True
            elif poppy == 'while':
                for path, node in tree.filter(javalang.tree.WhileStatement):
                    node_valid = True
                    listy2 = listy.copy()
                    index = INDENT_PER_LEVEL
                    while len(listy2) > 0:
                        popped = listy2.pop()
                        if popped == 'for':
                            if str(type(path[index])) != for_statement:
                                node_valid = False
                        elif popped == 'if':
                            if str(type(path[index])) != if_statement:
                                node_valid = False
                        elif popped == 'while':
                            if str(type(path[index])) != while_statement:
                                node_valid = False
                        index += INDENT_PER_LEVEL
                    if node_valid == True:
                        restriction_valid = True
            if restriction_valid == False:
                all_restrictions_valid = False
        return all_restrictions_valid
    
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
