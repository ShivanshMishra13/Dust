import string
import os 

###############
#    CONSTANTS     #
###############

DIGITS="1234567890"
LETTERS=string.ascii_letters
INT="INT"
STR="STRING"
KEYWORD="KEYWORD"
IDENTIFIER="IDENTIFIER"
EQ="EQ"
POW="POW"
FLOAT="FLOAT"
PLUS="PLUS"
MUL="MUL"
MIN="MINUS"
NEWL="NEWL"
DIV="DIVIDE"
LPAR="LPAR"
LSQR="LSQR"
RSQR="RSQR"
RPAR="RPAR"
EE="EE"
NE="NE"
GT="GT"
LT="LT"
LTE="LTE"
GTE="GTE"
EOF="EOF"
COMMA="COMMA"
ARROW ="ARROW"
SEMICOLON="SEMICOLON"
LBRAC="LBRAC"
RBRAC="RBRAC"
PIPE="PIPE"
KEYWORDS=[
"var",
"and",
"or",
"not",
"if",
"elif",
"else",
"then",
"for",
"to",
"while",
"step",
"func",
"end",
"return",
"continue",
"break"

]
LETTERS_DIGITS=LETTERS+DIGITS


###############
#    	ERROR 		  #
###############
class Error:
	def __init__(self,p_s,p_e,ename, edetails):
		self.error_name=ename
		self.error_details=edetails
		self.p_s=p_s
		self.p_e=p_e

	def in_string(self):
		string=f"{self.error_name}:{self.error_details}"
		string+= f" file{self.p_s.fn} line {self.p_s.ln} "
		return string

class IllegalCharError(Error):
	def __init__(self,p_s,p_e,detail):
		super().__init__(p_s,p_e,"IllegalChar", detail)
		
class ExpectedCharError(Error):
	def __init__(self,p_s,p_e,detail):
		super().__init__(p_s,p_e,"Expected Char Error", detail)

class InvalidSyntax(Error):
	def __init__(self,p_s,p_e, details=""):
		super().__init__(p_s,p_e,"InvalidSyntax", details)


###############
#      POSITION        #
###############

class Position:
	def __init__(self,idex,ln,col,fn,ftxt):
		self.col=col
		self.idex=idex
		self.ln=ln
		self.fn=fn
		self.ftxt=ftxt

	def advance(self,char=None):
		self.idex+=1
		self.col+=1
		if char=="\n":
			self.ln+=1
			self.col=0

	def copy(self):
		return Position(self.idex,self.ln,self.col,self.fn,self.ftxt)
	
class RTError(Error):
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Runtime Error', details)
		self.detailss=details 
		self.context = context

	def in_string(self):
		result  = self.generate_traceback()
		result += f'Runtime Error: {self.detailss}'
		return result

	def generate_traceback(self):
		result = ''
		pos = self.p_s
		ctx = self.context
		
		while ctx:
			result += f'File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n'
			pos = ctx.parent_entry_pos
			ctx = ctx.parent
			
		return 'Traceback (most recent call last):\n' + result
class Token:
	def __init__(self,type,value=None,p_s=None,p_e=None):
		if p_s:
			self.p_s=p_s.copy()
			self.p_e=self.p_s.copy()
			self.p_e.advance()
			
		if p_e:
			self.p_e=p_e
		self.type=type
		self.value= value 
		
		
	def matches(self,type_,value_):
		return self.type==type_ and self.value==value_




	def __repr__(self):
		if self.value: return f"{self.type}:{self.value}"
		return f"{self.type}"
		
		
		
###############
#       LEXER		     #
###############

class Lexer:
	def __init__(self,text,fn):
		self.text=text
		self.pos=Position(-1,0,-1,fn,text)
		self.curr_char= None
		self.advance()

	def advance(self):
		self.pos.advance(self.curr_char)
		self.curr_char=self.text[self.pos.idex] if self.pos.idex<len(self.text) else None

	def make_token(self):
		tokens=[]
		
		while self.curr_char != None:
			
			if self.curr_char in " \t ":
				self.advance()
			elif self.curr_char in DIGITS:
				tokens.append(self.make_numbers())
			elif self.curr_char=="+":
				tokens.append(Token(PLUS,p_s=self.pos))
				self.advance()
			
			elif self.curr_char in "; \n":
			    tokens.append(Token(NEWL,p_s=self.pos))
			    self.advance()
			elif self.curr_char=="-":
				tokens.append(self.make_minus_or_arrow())
				
			elif self.curr_char=="*":
				tokens.append(Token(MUL,p_s=self.pos))
				self.advance()
			elif self.curr_char=='"':
				tokens.append(self.make_strings())
				
			elif self.curr_char==",":
				tokens.append(Token(COMMA,p_s=self.pos))
				self.advance()
			elif self.curr_char=="|":
			    tokens.append(Token(PIPE,p_s=self.pos))
			    self.advance()
				
			elif self.curr_char=="/":
				tokens.append(Token(DIV,p_s=self.pos))
				self.advance() 
			elif self.curr_char=="^":
				tokens.append(Token(POW,p_s=self.pos))
				self.advance()		
			elif self.curr_char=="(":
				tokens.append(Token(LPAR,p_s=self.pos)) 
				self.advance() 
			elif self.curr_char=="=":
				tokens.append(self.make_equals())
			elif self.curr_char=="<":
				tokens.append(self.make_less_than()) 
			elif self.curr_char==">":
				tokens.append(self.make_less_than())

			elif self.curr_char=="!":
				tok, error=self.make_not_equals()
				if error: return [] ,error 
				tokens.append(tok)

	
			elif self.curr_char==")":
				tokens.append(Token(RPAR,p_s=self.pos))
				self.advance() 
			elif self.curr_char=="[":
				tokens.append(Token(LSQR,p_s=self.pos))
				self.advance()  
			elif self.curr_char=="]":
				tokens.append(Token(RSQR,p_s=self.pos))
				self.advance() 
			elif self.curr_char=="{":
				tokens.append(Token(LBRAC,p_s=self.pos))
				self.advance() 
			elif self.curr_char=="}":
				tokens.append(Token(RBRAC,p_s=self.pos))
				self.advance()

			elif self.curr_char in LETTERS:
				tokens.append(self.make_identifier())
				
			else:
				p_s=self.pos.copy()
				char=self.curr_char
				self.advance()
				return [] , IllegalCharError(p_s,self.pos,""+char+"")
		tokens.append(Token(EOF,p_s=self.pos))
		return tokens , None  
		
	def make_strings(self):
		strings_val=''
		p_s=self.pos.copy()
		escape_char=False 
		
		es_char={
		"n":"\n",
		"t":"\t"
		
		}
		
		self.advance()
		
		while self.curr_char!=None and (self.curr_char !='"' or escape_char):
			if escape_char:
				strings_val+=es_char.get(self.curr_char,self.curr_char)
				
			else:
				
				if self.curr_char=='\\':
					escape_char=True 
				else:		
					strings_val+=self.curr_char
			
			self.advance()
			escape_char=False
	
		self.advance()
		return Token(STR, strings_val,p_s,self.pos)
		


		
		
	def make_not_equals(self):
		p_s=self.pos.copy()
		self.advance()
		if self.curr_char=="=":
			self.advance()
			return Token(NE,p_s=p_s,p_e=self.pos),None 
		return None,ExpectedCharError(p_s,self.pos,"expected '=' after '!' ") 
		
	def make_minus_or_arrow(self):
		tok_type=MIN 
		p_s=self.pos.copy()
		self.advance()
		
		if self.curr_char==">":
			self.advance()
			tok_type=ARROW 
			
		return Token (tok_type,p_s=p_s,p_e=self.pos)


	
	def make_equals(self):
		tok_type=EQ
		p_s=self.pos.copy()
		self.advance()
		if self.curr_char =="=":
			tok_type=EE 
			self.advance()
		return Token(tok_type,p_s=p_s,p_e=self.pos)
		
	def make_less_than(self):
		tok_type=LT
		p_s=self.pos.copy()
		self.advance()
		if self.curr_char=="=":
			tok_type=LTE
			self.advance()
		return Token(tok_type,p_s=p_s,p_e=self.pos) 
	
	def make_greater_than(self):
		tok_type=GT
		p_s=self.pos.copy()
		self.advance()
		if self.curr_char=="=":
			tok_type=GTE
			self.advance()
		return Token(tok_type,p_s=p_s,p_e=self.pos)
 
 
 


		
	def make_identifier(self):
		id_str="" 
		p_s=self.pos.copy()
		
		while self.curr_char!=None and self.curr_char in LETTERS_DIGITS:
			id_str += self.curr_char
			self.advance()
			
			
		tok_type=KEYWORD if id_str in KEYWORDS else IDENTIFIER 
		return Token(tok_type,id_str,p_s,self.pos)
		 



	def make_numbers(self):
		p_s=self.pos.copy()
		dots=0
		num_str=""
		
		while self.curr_char != None and self.curr_char in DIGITS + ".":
			if self.curr_char==".":
				if dots >= 1: break
				dots+=1
				num_str+="."
			else:
				num_str+=self.curr_char
			self.advance()
				
		if dots==0:
			return Token(INT,int(num_str),p_s,self.pos)
		else:
			return Token(FLOAT,float(num_str),p_s,self.pos)
