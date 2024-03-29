from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,46,320,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,
        2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,
        13,7,13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,
        19,2,20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,
        26,7,26,2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,
        32,2,33,7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,
        39,7,39,2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,
        45,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,
        2,1,2,1,2,1,3,1,3,1,3,1,3,1,3,1,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,
        6,1,6,1,6,1,6,1,6,1,6,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,7,1,
        8,1,8,1,8,1,8,1,9,1,9,1,9,1,9,1,9,1,9,1,10,1,10,1,10,1,10,1,10,1,
        11,1,11,1,11,1,11,1,11,1,11,1,12,1,12,1,12,1,12,1,13,1,13,1,13,1,
        13,1,14,1,14,1,14,1,15,1,15,1,15,1,15,1,15,1,16,1,16,1,16,1,16,1,
        17,1,17,1,17,1,18,1,18,1,18,1,18,1,18,1,19,1,19,1,20,1,20,1,21,1,
        21,1,22,1,22,1,23,1,23,1,24,1,24,1,25,1,25,1,26,1,26,1,26,1,27,1,
        27,1,28,1,28,1,29,1,29,1,29,1,30,1,30,1,31,1,31,1,31,1,32,1,32,1,
        32,1,33,1,33,1,34,1,34,1,35,1,35,1,36,1,36,1,37,1,37,1,38,1,38,1,
        39,4,39,251,8,39,11,39,12,39,252,1,39,5,39,256,8,39,10,39,12,39,
        259,9,39,1,40,3,40,262,8,40,1,40,3,40,265,8,40,1,40,5,40,268,8,40,
        10,40,12,40,271,9,40,1,41,3,41,274,8,41,1,41,1,41,1,41,4,41,279,
        8,41,11,41,12,41,280,3,41,283,8,41,1,42,1,42,1,42,3,42,288,8,42,
        1,42,1,42,1,43,1,43,1,43,1,43,5,43,296,8,43,10,43,12,43,299,9,43,
        1,43,1,43,1,44,1,44,1,44,1,44,5,44,307,8,44,10,44,12,44,310,9,44,
        1,44,1,44,1,45,4,45,315,8,45,11,45,12,45,316,1,45,1,45,0,0,46,1,
        1,3,2,5,3,7,4,9,5,11,6,13,7,15,8,17,9,19,10,21,11,23,12,25,13,27,
        14,29,15,31,16,33,17,35,18,37,19,39,20,41,21,43,22,45,23,47,24,49,
        25,51,26,53,27,55,28,57,29,59,30,61,31,63,32,65,33,67,34,69,35,71,
        36,73,37,75,38,77,39,79,40,81,41,83,42,85,43,87,44,89,45,91,46,1,
        0,6,3,0,65,90,95,95,97,122,4,0,48,57,65,90,95,95,97,122,1,0,48,57,
        3,0,10,10,13,13,34,34,1,0,10,10,3,0,9,10,13,13,32,32,331,0,1,1,0,
        0,0,0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,
        0,13,1,0,0,0,0,15,1,0,0,0,0,17,1,0,0,0,0,19,1,0,0,0,0,21,1,0,0,0,
        0,23,1,0,0,0,0,25,1,0,0,0,0,27,1,0,0,0,0,29,1,0,0,0,0,31,1,0,0,0,
        0,33,1,0,0,0,0,35,1,0,0,0,0,37,1,0,0,0,0,39,1,0,0,0,0,41,1,0,0,0,
        0,43,1,0,0,0,0,45,1,0,0,0,0,47,1,0,0,0,0,49,1,0,0,0,0,51,1,0,0,0,
        0,53,1,0,0,0,0,55,1,0,0,0,0,57,1,0,0,0,0,59,1,0,0,0,0,61,1,0,0,0,
        0,63,1,0,0,0,0,65,1,0,0,0,0,67,1,0,0,0,0,69,1,0,0,0,0,71,1,0,0,0,
        0,73,1,0,0,0,0,75,1,0,0,0,0,77,1,0,0,0,0,79,1,0,0,0,0,81,1,0,0,0,
        0,83,1,0,0,0,0,85,1,0,0,0,0,87,1,0,0,0,0,89,1,0,0,0,0,91,1,0,0,0,
        1,93,1,0,0,0,3,97,1,0,0,0,5,103,1,0,0,0,7,111,1,0,0,0,9,117,1,0,
        0,0,11,124,1,0,0,0,13,135,1,0,0,0,15,146,1,0,0,0,17,156,1,0,0,0,
        19,160,1,0,0,0,21,166,1,0,0,0,23,171,1,0,0,0,25,177,1,0,0,0,27,181,
        1,0,0,0,29,185,1,0,0,0,31,188,1,0,0,0,33,193,1,0,0,0,35,197,1,0,
        0,0,37,200,1,0,0,0,39,205,1,0,0,0,41,207,1,0,0,0,43,209,1,0,0,0,
        45,211,1,0,0,0,47,213,1,0,0,0,49,215,1,0,0,0,51,217,1,0,0,0,53,219,
        1,0,0,0,55,222,1,0,0,0,57,224,1,0,0,0,59,226,1,0,0,0,61,229,1,0,
        0,0,63,231,1,0,0,0,65,234,1,0,0,0,67,237,1,0,0,0,69,239,1,0,0,0,
        71,241,1,0,0,0,73,243,1,0,0,0,75,245,1,0,0,0,77,247,1,0,0,0,79,250,
        1,0,0,0,81,261,1,0,0,0,83,273,1,0,0,0,85,284,1,0,0,0,87,291,1,0,
        0,0,89,302,1,0,0,0,91,314,1,0,0,0,93,94,5,118,0,0,94,95,5,97,0,0,
        95,96,5,114,0,0,96,2,1,0,0,0,97,98,5,112,0,0,98,99,5,114,0,0,99,
        100,5,105,0,0,100,101,5,110,0,0,101,102,5,116,0,0,102,4,1,0,0,0,
        103,104,5,112,0,0,104,105,5,114,0,0,105,106,5,105,0,0,106,107,5,
        110,0,0,107,108,5,116,0,0,108,109,5,108,0,0,109,110,5,110,0,0,110,
        6,1,0,0,0,111,112,5,108,0,0,112,113,5,101,0,0,113,114,5,110,0,0,
        114,115,5,111,0,0,115,116,5,102,0,0,116,8,1,0,0,0,117,118,5,99,0,
        0,118,119,5,111,0,0,119,120,5,112,0,0,120,121,5,121,0,0,121,122,
        5,111,0,0,122,123,5,102,0,0,123,10,1,0,0,0,124,125,5,102,0,0,125,
        126,5,108,0,0,126,127,5,111,0,0,127,128,5,111,0,0,128,129,5,114,
        0,0,129,130,5,105,0,0,130,131,5,110,0,0,131,132,5,116,0,0,132,133,
        5,111,0,0,133,134,5,102,0,0,134,12,1,0,0,0,135,136,5,114,0,0,136,
        137,5,111,0,0,137,138,5,117,0,0,138,139,5,110,0,0,139,140,5,100,
        0,0,140,141,5,105,0,0,141,142,5,110,0,0,142,143,5,116,0,0,143,144,
        5,111,0,0,144,145,5,102,0,0,145,14,1,0,0,0,146,147,5,99,0,0,147,
        148,5,101,0,0,148,149,5,105,0,0,149,150,5,108,0,0,150,151,5,105,
        0,0,151,152,5,110,0,0,152,153,5,116,0,0,153,154,5,111,0,0,154,155,
        5,102,0,0,155,16,1,0,0,0,156,157,5,115,0,0,157,158,5,105,0,0,158,
        159,5,110,0,0,159,18,1,0,0,0,160,161,5,119,0,0,161,162,5,104,0,0,
        162,163,5,105,0,0,163,164,5,108,0,0,164,165,5,101,0,0,165,20,1,0,
        0,0,166,167,5,84,0,0,167,168,5,114,0,0,168,169,5,117,0,0,169,170,
        5,101,0,0,170,22,1,0,0,0,171,172,5,70,0,0,172,173,5,97,0,0,173,174,
        5,108,0,0,174,175,5,115,0,0,175,176,5,101,0,0,176,24,1,0,0,0,177,
        178,5,110,0,0,178,179,5,111,0,0,179,180,5,116,0,0,180,26,1,0,0,0,
        181,182,5,97,0,0,182,183,5,110,0,0,183,184,5,100,0,0,184,28,1,0,
        0,0,185,186,5,111,0,0,186,187,5,114,0,0,187,30,1,0,0,0,188,189,5,
        100,0,0,189,190,5,101,0,0,190,191,5,99,0,0,191,192,5,108,0,0,192,
        32,1,0,0,0,193,194,5,114,0,0,194,195,5,101,0,0,195,196,5,116,0,0,
        196,34,1,0,0,0,197,198,5,105,0,0,198,199,5,102,0,0,199,36,1,0,0,
        0,200,201,5,101,0,0,201,202,5,108,0,0,202,203,5,115,0,0,203,204,
        5,101,0,0,204,38,1,0,0,0,205,206,5,61,0,0,206,40,1,0,0,0,207,208,
        5,59,0,0,208,42,1,0,0,0,209,210,5,58,0,0,210,44,1,0,0,0,211,212,
        5,44,0,0,212,46,1,0,0,0,213,214,5,43,0,0,214,48,1,0,0,0,215,216,
        5,45,0,0,216,50,1,0,0,0,217,218,5,42,0,0,218,52,1,0,0,0,219,220,
        5,42,0,0,220,221,5,42,0,0,221,54,1,0,0,0,222,223,5,47,0,0,223,56,
        1,0,0,0,224,225,5,60,0,0,225,58,1,0,0,0,226,227,5,60,0,0,227,228,
        5,61,0,0,228,60,1,0,0,0,229,230,5,62,0,0,230,62,1,0,0,0,231,232,
        5,62,0,0,232,233,5,61,0,0,233,64,1,0,0,0,234,235,5,61,0,0,235,236,
        5,61,0,0,236,66,1,0,0,0,237,238,5,40,0,0,238,68,1,0,0,0,239,240,
        5,41,0,0,240,70,1,0,0,0,241,242,5,91,0,0,242,72,1,0,0,0,243,244,
        5,93,0,0,244,74,1,0,0,0,245,246,5,123,0,0,246,76,1,0,0,0,247,248,
        5,125,0,0,248,78,1,0,0,0,249,251,7,0,0,0,250,249,1,0,0,0,251,252,
        1,0,0,0,252,250,1,0,0,0,252,253,1,0,0,0,253,257,1,0,0,0,254,256,
        7,1,0,0,255,254,1,0,0,0,256,259,1,0,0,0,257,255,1,0,0,0,257,258,
        1,0,0,0,258,80,1,0,0,0,259,257,1,0,0,0,260,262,5,45,0,0,261,260,
        1,0,0,0,261,262,1,0,0,0,262,264,1,0,0,0,263,265,2,48,57,0,264,263,
        1,0,0,0,265,269,1,0,0,0,266,268,7,2,0,0,267,266,1,0,0,0,268,271,
        1,0,0,0,269,267,1,0,0,0,269,270,1,0,0,0,270,82,1,0,0,0,271,269,1,
        0,0,0,272,274,5,45,0,0,273,272,1,0,0,0,273,274,1,0,0,0,274,275,1,
        0,0,0,275,282,3,81,40,0,276,278,5,46,0,0,277,279,7,2,0,0,278,277,
        1,0,0,0,279,280,1,0,0,0,280,278,1,0,0,0,280,281,1,0,0,0,281,283,
        1,0,0,0,282,276,1,0,0,0,282,283,1,0,0,0,283,84,1,0,0,0,284,287,5,
        39,0,0,285,288,5,39,0,0,286,288,8,3,0,0,287,285,1,0,0,0,287,286,
        1,0,0,0,288,289,1,0,0,0,289,290,5,39,0,0,290,86,1,0,0,0,291,297,
        5,34,0,0,292,293,5,92,0,0,293,296,5,34,0,0,294,296,8,3,0,0,295,292,
        1,0,0,0,295,294,1,0,0,0,296,299,1,0,0,0,297,295,1,0,0,0,297,298,
        1,0,0,0,298,300,1,0,0,0,299,297,1,0,0,0,300,301,5,34,0,0,301,88,
        1,0,0,0,302,303,5,47,0,0,303,304,5,47,0,0,304,308,1,0,0,0,305,307,
        8,4,0,0,306,305,1,0,0,0,307,310,1,0,0,0,308,306,1,0,0,0,308,309,
        1,0,0,0,309,311,1,0,0,0,310,308,1,0,0,0,311,312,6,44,0,0,312,90,
        1,0,0,0,313,315,7,5,0,0,314,313,1,0,0,0,315,316,1,0,0,0,316,314,
        1,0,0,0,316,317,1,0,0,0,317,318,1,0,0,0,318,319,6,45,1,0,319,92,
        1,0,0,0,14,0,252,257,261,264,269,273,280,282,287,295,297,308,316,
        2,0,1,0,6,0,0
    ]

class GramLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    VAR = 1
    PRINT = 2
    PRINTLN = 3
    LENOF = 4
    COPYOF = 5
    FLOORINTOF = 6
    ROUNDINTOF = 7
    CEILINTOF = 8
    SIN = 9
    WHILE = 10
    TRUE = 11
    FALSE = 12
    NOT = 13
    AND = 14
    OR = 15
    DECL = 16
    RET = 17
    IF = 18
    ELSE = 19
    ASSIGN = 20
    SEMI = 21
    COLON = 22
    COMMA = 23
    PLUS = 24
    MINUS = 25
    TIMES = 26
    POW = 27
    DIV = 28
    LESSTHAN = 29
    LESSTHANOREQUAL = 30
    GREATERTHAN = 31
    GREATERTHANOREQUAL = 32
    EQUALS = 33
    LPAREN = 34
    RPAREN = 35
    LBRACK = 36
    RBRACK = 37
    LBRACE = 38
    RBRACE = 39
    IDEN = 40
    INT = 41
    FLOAT = 42
    CHAR = 43
    STRING = 44
    LINE_COMMENT = 45
    WS = 46

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'var'", "'print'", "'println'", "'lenof'", "'copyof'", "'floorintof'", 
            "'roundintof'", "'ceilintof'", "'sin'", "'while'", "'True'", 
            "'False'", "'not'", "'and'", "'or'", "'decl'", "'ret'", "'if'", 
            "'else'", "'='", "';'", "':'", "','", "'+'", "'-'", "'*'", "'**'", 
            "'/'", "'<'", "'<='", "'>'", "'>='", "'=='", "'('", "')'", "'['", 
            "']'", "'{'", "'}'" ]

    symbolicNames = [ "<INVALID>",
            "VAR", "PRINT", "PRINTLN", "LENOF", "COPYOF", "FLOORINTOF", 
            "ROUNDINTOF", "CEILINTOF", "SIN", "WHILE", "TRUE", "FALSE", 
            "NOT", "AND", "OR", "DECL", "RET", "IF", "ELSE", "ASSIGN", "SEMI", 
            "COLON", "COMMA", "PLUS", "MINUS", "TIMES", "POW", "DIV", "LESSTHAN", 
            "LESSTHANOREQUAL", "GREATERTHAN", "GREATERTHANOREQUAL", "EQUALS", 
            "LPAREN", "RPAREN", "LBRACK", "RBRACK", "LBRACE", "RBRACE", 
            "IDEN", "INT", "FLOAT", "CHAR", "STRING", "LINE_COMMENT", "WS" ]

    ruleNames = [ "VAR", "PRINT", "PRINTLN", "LENOF", "COPYOF", "FLOORINTOF", 
                  "ROUNDINTOF", "CEILINTOF", "SIN", "WHILE", "TRUE", "FALSE", 
                  "NOT", "AND", "OR", "DECL", "RET", "IF", "ELSE", "ASSIGN", 
                  "SEMI", "COLON", "COMMA", "PLUS", "MINUS", "TIMES", "POW", 
                  "DIV", "LESSTHAN", "LESSTHANOREQUAL", "GREATERTHAN", "GREATERTHANOREQUAL", 
                  "EQUALS", "LPAREN", "RPAREN", "LBRACK", "RBRACK", "LBRACE", 
                  "RBRACE", "IDEN", "INT", "FLOAT", "CHAR", "STRING", "LINE_COMMENT", 
                  "WS" ]

    grammarFileName = "GramLexer.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.12.0")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


