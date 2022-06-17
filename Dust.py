"""
Project dust source file 

here is all the source code of dust programing language

"""
#----------------------------Start------------------------------------#
###############
# DEPENDENCY	 #
###############

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
"func"

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

###############
#          TOKEN 		#
###############

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


###############
#      NODES 	        #
###############
 

class NumberNode:
 	
 	def __init__(self,tok):
 		self.tok=tok		
 		self.p_s=self.tok.p_s
 		self.p_e=self.tok.p_e
 			
 	def __repr__(self):
 		return f"{self.tok}"	
 		
class StringNode:
 	
 	def __init__(self,tok):
 		self.tok=tok		
 		self.p_s=self.tok.p_s
 		self.p_e=self.tok.p_e
 			
 	def __repr__(self):
 		return f"{self.tok}"	
 		
class IfNode:
 		def __init__(self, cases,else_case):
 			self.cases=cases
 			self.else_case=else_case
 			
 			self.p_s=self.cases[0][0].p_s
 			self.p_e=(self.else_case or self.cases[len(self.cases)-1][0]).p_e
 			
class ForNode:
 		def __init__(self,var_name_tok,start_value_node,end_value_node,step_value_node,body_node):
 			self.var_name_tok=var_name_tok
 			self.start_value_node=start_value_node
 			self.end_value_node=end_value_node
 			self.step_value_node=step_value_node
 			self.body_node=body_node
 			
 			self.p_s=self.var_name_tok.p_s
 			self.p_e=self.body_node.p_e
 			
 			
 			
class WhileNode:
 	def __init__(self, condition_node,body_node):
 	 self.condition_node=condition_node
 	 self.body_node=body_node
 	 
 	 self.p_s=self.condition_node.p_s
 	 self.p_e=self.body_node.p_e
 	 
 			
 		
class VarAccessNode:
 		def __init__(self,var_name_tok):
 			self.var_name_tok=var_name_tok 
 			self.p_s=self.var_name_tok.p_s
 			self.p_e=self.var_name_tok.p_e
 			
 			
class VarAssignNode:
	def __init__(self,var_name_tok,value_node):
		self.var_name_tok=var_name_tok 
		self.value_node=value_node		
		
		self.p_s=self.var_name_tok.p_s
		self.p_e=self.var_name_tok.p_e
		

class FuncDefNode:
		def __init__(self,var_name_tok,arg_name_toks,body_node):
			
			self.var_name_tok = var_name_tok
			self.arg_name_toks = arg_name_toks
			self.body_node = body_node	
		
			if self.var_name_tok:
				self.p_s = self.var_name_tok.p_s
			elif len(self.arg_name_toks) > 0:
				self.p_s= self.arg_name_toks[0].p_s
			else:
				self.p_s_start = self.body_node.p_s

			self.p_e = self.body_node.p_e	
			
class CallNode:
		def __init__(self,node_to_call,arg_nodes):
				self.node_to_call=node_to_call
				self.arg_nodes=arg_nodes
				
				self.p_s = self.node_to_call.p_s
				
				if len(self.arg_nodes) > 0:			
					self.p_e = self.arg_nodes[len(self.arg_nodes) - 1].p_e
				
				else:				
					self.p_e= self.node_to_call.p_e

				
		
class BinOpNode:
 	def __init__(self,left_n,op_tok,right_n):
 		self.left_n=left_n
 		self.op_tok=op_tok
 		self.right_n=right_n
 		self.p_s=self.left_n.p_s
 		self.p_e=self.right_n.p_e
 		
 	def __repr__(self):
 		return f"BinOp({self.left_n}, {self.op_tok}, {self.right_n})"
class ListNode:
	def __init__(self, element_nodes,p_s,p_e):
		self.element_nodes=element_nodes
		
		self.p_s=p_s
		self.p_e=p_e
		
class UrnaryOpNode:
 		def __init__(self,op_tok,node):
 			self.op_tok=op_tok 
 			self.node=node 
 			self.p_s=self.op_tok.p_s
 			self.p_e=node.p_e
 			
 		def __repr__(self):
 			return f"({self.op_tok} {self.node})"
 		
###############
#   PARSERESULT   #
###############


class ParseResult:
 	def __init__(self):
 		self.error=None
 		self.node=None 
 		self.advance_count=0

 		
 	def register_advance(self):
 		self.advance_count+=1
	
 	
 	def register(self,res):	
 		if res.error: self.error=res.error
 		return res.node
 		
 			 	 
 	def success(self,node):
 		self.node=node 
 		return self

 	
 	def failure(self,error):
 		if not error or self.advance_count==0:
 			self.error=error 
 		return self
 		
	

###############
#      PARSER           #
###############
 
class Parser:
 	def __init__(self,tokens):	
 		self.tokens=tokens
 		self.tok_idx=-1
 		self.advance()
 	def advance(self):
 		self.tok_idx+=1
 		if self.tok_idx<len(self.tokens):
 			self.curr_tok=self.tokens[self.tok_idx]
 		return self.curr_tok 
 		
 	
 		
 		
 		
 		
 	def parse(self):
 		res=self.expr()
 		
 		if not  res.error and self.curr_tok.type!=EOF:
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected + - * / "))
 	
 		return res 
 		
 	def if_expr(self):
 		res=ParseResult ()
 		cases=[]
 		else_case=None 
 		if not self.curr_tok.matches(KEYWORD,"if"):
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"expected if "))
 		res.register_advance()
 		self.advance()
 		condition=res.register(self.expr())
 		if res.error: return res 
 		if not self.curr_tok.matches(KEYWORD,"then"):
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"expected then "))
 		res.register_advance()
 		self.advance()
 		
 		expr=res.register(self.expr())
 		if res.error: return res 
 		cases.append((condition,expr))
 		
 		while self.curr_tok.matches(KEYWORD,"elif"):
 			res.register_advance()
 			self.advance()
 			
 			condition=res.register(self.expr())
 			if res.error: return res 
 			
 			if not self.curr_tok.matches(KEYWORD,"then"):
 				return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"expected then "))
 			res.register_advance()
 			self.advance()
 			
 			expr=res.register(self.expr())
 			if res.error: return res 
 			cases.append((condition,expr))
 			
 		if self.curr_tok.matches(KEYWORD,"else"):
 			res.register_advance()
 			self.advance()
 			
 			else_case=res.register(self.expr())
 			if res.error : return res 
 		
 		return res.success(IfNode(cases,else_case))
 		
 	def for_expr(self):
 		res=ParseResult ()
 		
 		if not self.curr_tok.matches(KEYWORD,"for"):
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expected for keyword"))
 		res.register_advance()
 		self.advance()
 		
 		if self.curr_tok.type!=IDENTIFIER:
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expected identifier"))
 			
 		var_name=self.curr_tok
 		res.register_advance()
 		self.advance()
 		
 		if self.curr_tok.type!=EQ:
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting a '='"))
 			
 		res.register_advance()
 		self.advance()
 		
 		start_value=res.register(self.expr())
 		if res.error: return res 
 		
 		if not  self.curr_tok.matches(KEYWORD,"to"):
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting to keyword"))
 		
 		res.register_advance()
 		self.advance()
 		
 		end_value = res.register(self.expr())
 		if res.error: return res

 			
 			
 		
 		if self.curr_tok.matches(KEYWORD,"step"):
 			
 			res.register_advance()
 			self.advance()
 			
 			step_value=res.register(self.expr())
 			if res.error: return res 
 		else:
 			step_value=None 
 			
 		if not self.curr_tok.matches(KEYWORD,"then"):
 			 return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting to keyword"))
 			
 		res.register_advance()
 		self.advance()
 		
 		body = res.register(self.expr())
 		if res.error: return res 
 		
 		return res.success(ForNode(var_name, start_value, end_value, step_value, body))
 		
 		
 	def while_expr(self):
 		res=ParseResult () 		
 		
 		if not self.curr_tok.matches(KEYWORD,"while"):
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting while keyword"))
 		res.register_advance()
 		self.advance()
 		
 		condition=res.register(self.expr())
 		if res.error: return res 
 		
 		if not self.curr_tok.matches(KEYWORD,"then"):
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting then keyword"))
 			
 		res.register_advance()
 		self.advance()
 		
 		body=res.register(self.expr())
 		if res.error: return res 
 		
 		return res.success(WhileNode(condition,body))
 	
 	def func_def(self):
 		res=ParseResult ()
 		
 		if not self.curr_tok.matches(KEYWORD,"func"):
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected func"))
 			
 		res.register_advance()
 		self.advance()
 		
 		if self.curr_tok.type==IDENTIFIER:
 			var_name_tok=self.curr_tok
 			res.register_advance()
 			self.advance()
 			if self.curr_tok.type!=LPAR:
 				return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected )"))
 		else:
 				
 				var_name_tok=None 
 				if self.curr_tok.type!=LPAR:
 					
 					return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected ("))
 					
 		res.register_advance()
 		self.advance()
 			
 		arg_name_toks=[]
 		
 		if self.curr_tok.type==IDENTIFIER:
 			arg_name_toks.append(self.curr_tok)
 			res.register_advance()
 			self.advance()
 			
 			while self.curr_tok.type==COMMA:
 				res.register_advance()
 				self.advance()
 				
 				if self.curr_tok.type!=IDENTIFIER:
 					return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected identifier"))
 					
 				arg_name_toks.append(self.curr_tok)
 				res.register_advance()
 				self.advance()
 				
 				if self.curr_tok.type!=RPAR:
 					return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected )"))
 					
 		else:
 			
 			if self.curr_tok.type!=RPAR:
 					return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected )"))
 					
 		res.register_advance()
 		self.advance()
 		
 		if self.curr_tok.type!=ARROW:
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected -> after func def "))
 		res.register_advance()
 		self.advance()
 		node_to_return=res.register(self.expr())
 		if res.error: return res 
 		
 		return res.success(FuncDefNode(
			var_name_tok,
			arg_name_toks,
			node_to_return
		))


 		

 	def list_expr(self):
 		res=ParseResult ()
 		
 		element_nodes=[]
 		p_s=self.curr_tok.p_s.copy()
 		
 		tok=self.curr_tok 
 		
 		if tok.type!=LSQR:
 			print("fuck it ")
 			return res.failure(InvalidSyntaxError(tok.p_s,tok.p_e,"expected ["))
 			
 		res.register_advance()
 		self.advance()
 		
 		if tok.type==RSQR:
 			print("hdus")
 			res.register_advance()
 			self.advance()
 			return res.success(ListNode(element_nodes,tok.p_s,tok.p_e.copy()))
 		
 		else:
 					
 				element_nodes.append(res.register(self.expr()))
 				if res.error:
 					 
 					 return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected '[', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"))
 				
 				while self.curr_tok.type==COMMA:
 					res.register_advance()
 					self.advance()
 					element_nodes.append(res.register(self.expr()))
 					if res.error : return res 
 				
 				if self.curr_tok.type!=RSQR:
 					return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expecting ]"))
 				res.register_advance()
 				self.advance()
 		return res.success(ListNode(element_nodes,tok.p_s,tok.p_e.copy()))
 		
 			
 			
 		
 		
 	def atom(self):
 		res=ParseResult()
 		tok=self.curr_tok
 		
 		
 		if tok.type in (INT,FLOAT):
 			
 			res.register_advance()
 			self.advance()
 			return res.success(NumberNode(tok))
 			
 		
 			
 				
 						
 		if tok.type == STR:
 			
 			
 			
 			res.register_advance()
 			self.advance()
 			return res.		success(StringNode(tok))	
 			
 			
 		elif tok.type==IDENTIFIER:
 			res.register_advance()
 			self.advance()
 			return res.success(VarAccessNode(tok))
 			
 		elif tok.type==LPAR:
 			res.register_advance()
 			self.advance()
 			expr=res.register(self.expr())
 			if res.error : return res 
 			if self.curr_tok.type== RPAR:
 				res.register_advance()
 				self.advance()
 				return res.success(expr)
 			else:
 				return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e," Expected  )"))
 				
 		elif tok.type==LSQR:
 		#	print("got it ")
 			list_expr=res.register(self.list_expr())
 			
 			if res.error: return res 
 			
 			return res.success(list_expr)				
 				
 		elif tok.matches(KEYWORD,"if"):
 				if_expr=res.register(self.if_expr())
 				if res.error: return res 
 				return res.success(if_expr)
 				
 		elif tok.matches(KEYWORD,"for"):
 				for_expr=res.register(self.for_expr())
 				if res.error: return res 
 				return res.success(for_expr)
 				
 		elif tok.matches(KEYWORD,"while"):
 				while_expr=res.register(self.while_expr())
 				if res.error: return res 
 				return res.success(while_expr)
 				
 		elif tok.matches(KEYWORD,"func"):
 				while_expr=res.register(self.func_def())
 				if res.error: return res 
 				return res.success(while_expr)
 				
 				

 		return res.failure(InvalidSyntax (tok.p_s,tok.p_e,"Expected identifier or var or + - / * ^"))
 		
 	
 	def power(self):
 		return self.bin_op(self.call,(POW),self.factor)
 		
 	def call(self):
 		res=ParseResult ()
 		atom=res.register(self.atom())
 		if res.error : return res 
 		
 		if self.curr_tok.type==LPAR:
 			res.register_advance()
 			self.advance()
 			arg_nodes=[]
 			if self.curr_tok.type==RPAR:
 				res.register_advance()
 				self.advance()
 			else:
 				arg_nodes.append(res.register(self.expr()))
 				if res.error:
 					 
 					 return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"))
 				
 				while self.curr_tok.type==COMMA:
 					res.register_advance()
 					self.advance()
 					arg_nodes.append(res.register(self.expr()))
 					if res.error : return res 
 				
 				if self.curr_tok.type!=RPAR:
 					return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expecting )"))
 				res.register_advance()
 				self.advance()
 			return res.success(CallNode(atom, arg_nodes))
 		return res.success(atom)
 					
		
 	def factor(self):
 		res=ParseResult()
 		tok=self.curr_tok
 		
 		if tok.type in (PLUS,MIN):
 			res.register_advance()
 			self.advance()
 			factor = res.register(self.factor())
 			if res.error : return res 
 			return res.success(UrnaryOpNode (tok,factor)) 
 		return self.power()
 			
 	

 		
 			
 			
 		
 	def term(self):
 		return self.bin_op(self.factor,(MUL,DIV))
 		
 	def comp_expr(self):
 		res=ParseResult ()
 		if self.curr_tok.matches(KEYWORD,"not"):
 			op_tok = self.current_tok
 			res.register_advance()
 			self.advance()
 			node = res.register(self.comp_expr())
 			if res.error: return res
 			return res.success(UnaryOpNode(op_tok, node))
 		node=res.register(self.bin_op(self.arith_expr,(EE,NE,LT,GT,LTE,GTE)))
 		if res.error:
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected int, float, identifier, '+', '-', '(' or 'NOT' "))
 		return res.success(node)
 		
 		
 	def arith_expr(self):
 		return self.bin_op(self.term, (PLUS, MIN))



 		
 	def expr(self):
 		res=ParseResult ()
 		if self.curr_tok.matches(KEYWORD,"var"):
 			res.register_advance()
 			self.advance()
 			if self.curr_tok.type != IDENTIFIER:
 				return res.failure(InvalidSyntax (
 				self.curr_tok.p_s,
 				self.curr_tok.p_e,
 				"Expected an identifier"))
 			var_name=self.curr_tok
 			res.register_advance()
 			self.advance()
 			if self.curr_tok.type != EQ:
 				return res.failure(InvalidSyntax (self.curr_tok.p_s,
 				self.curr_tok.p_e,
 				"Expected '=' ")) 
 			res.register_advance()
 			self.advance()
 			expr=res.register(self.expr())
 			return res.success(VarAssignNode(var_name,expr))
 		
 					
 			
 		node=res.register(self.bin_op(self.comp_expr,((KEYWORD,"and"),(KEYWORD,"or"))))
 		if res.error:	 		
 		 	return res.failure((InvalidSyntax (self.					curr_tok.p_s,
 				self.curr_tok.p_e,
 				"Expected var or identifier or + - / * not ")))
 		return res.success(node)
 			 		
 		
 	def bin_op(self,func_a,opts,func_b=None):
 		if func_b==None:
 			func_b=func_a
 		res=ParseResult()
 		left=res.register(func_a())
 		if res.error: return res 
 		value=None
 		if self.curr_tok.value!=None:
 			value=str(self.curr_tok.value)
 		value="z"

 		while str(self.curr_tok.type) in opts or value in opts:
 			op_tok=self.curr_tok
 			res.register_advance()
 			self.advance()
 			right=res.register(func_b())
 			if res.error: return res
 			left=BinOpNode(left,op_tok,right)
 		return res.success(left)

 ###############
#  		 VALUES	    #
###############
class Value:
	def __init__(self):
		self.set_pos()
		self.set_context()

	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

	def added_to(self, other):
		return None, self.illegal_operation(other)

	def subbed_by(self, other):
		return None, self.illegal_operation(other)

	def multed_by(self, other):
		return None, self.illegal_operation(other)

	def dived_by(self, other):
		return None, self.illegal_operation(other)

	def powed_by(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_eq(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_ne(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gt(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_lte(self, other):
		return None, self.illegal_operation(other)

	def get_comparison_gte(self, other):
		return None, self.illegal_operation(other)

	def anded_by(self, other):
		return None, self.illegal_operation(other)

	def ored_by(self, other):
		return None, self.illegal_operation(other)

	def notted(self):
		return None, self.illegal_operation(other)

	def execute(self, args):
		return RTResult().failure(self.illegal_operation())

	def copy(self):
		raise Exception('No copy method defined')

	def is_true(self):
		return False

	def illegal_operation(self, other=None):
		if not other: other = self
		return RTError(
			self.pos_start, other.pos_end,
			'Illegal operation',
			self.context
		)

class List(Value):
	def __init__(self, elements):
		super().__init__()
		self.elements=elements 
		
	
		
	def added_to(self,other):
		
		new_list=self.copy()
		
		new_list.elements.append(other)
		
		return new_list,None 
		
	def subbed_by(self,other):
		if isinstance (other,Number):
			new_list=self.copy()
			try:
				new_list.elements.pop(other.value)
				return new_list,None
			except:
				return None, RTError(
					other.p_s, other.p_e,
					'Cannot remove item index out of bound',
					self.context
				)
		else:
			return None,Value.illegal_operation(self, other)
	
	def div_by(self,other):
		if isinstance (other,Number):
	
			try:
				return self.elements[other.value],None

			except:
				return None, RTError(
					other.p_s, other.p_e,
					'Cannot remove item index out of bound or element does not exist ',
					self.context
				)
		else:
			return None,Value.illegal_operation(self, other)
	def __str__(self):
		return f'[{",".join(str(x) for x in self.elements)}]'
		
		
	def __repr__(self):
		return f'[{",".join(str(x) for x in self.elements)}]'
	def copy(self):
			copy=List(self.elements)
			copy.set_pos(self.pos_start,self.pos_end)
			copy.set_context(self.context)
			
			return copy
		
	def mul_by(self,other):
		if isinstance(other,List):
			new_list=self.copy()
			new_list.elements.extend(other.elements)
			
			return new_list,None 
		else:
			return None,Value.illegal_operation(self, other)


			


		
class Number(Value):
 def __init__(self,value):
 	super().__init__()
 	self.value=value 
 	self.set_pos()
 	self.set_context()
 	
 def __repr__(self):
 	return str(self.value)
 
 def set_pos(self,p_s=None,p_e=None):
 	self.p_s=p_s 
 	self.p_e=p_e
 	return self 
 def is_true(self):
 	return self.value !=0
 	
 def set_context(self, context=None):
		self.context = context
		return self
 	
 def added_to(self,other):
 	if isinstance(other,Number):
 		return Number(self.value+other.value).set_context(self.context), None 
 	else:
			return None, Value.illegal_operation(self, other)



 
 def subbed_by(self,other):
 	if isinstance(other,Number):
 		return Number(self.value-other.value).set_context(self.context), None 
 	else:
			return None, Value.illegal_operation(self, other)



 		
 def mul_by(self,other):
 	if isinstance(other,Number):
 		return Number(self.value*other.value).set_context(self.context), None 
 	else:
			return None, Value.illegal_operation(self, other)

 		
 		
 def copy(self):
 	copy=Number(self.value)
 	copy.set_pos(self.p_s,self.p_e)
 	copy.set_context(self.context)
 	return copy



 		 		
 def  div_by(self,other):
 	if isinstance(other,Number):
 		if other.value == 0:
 			return None, RTError(
					other.p_s, other.p_e,
					'Division by zero',
					self.context
				)
 		return Number(self.value/other.value),None 
 	else:
			return None, Value.illegal_operation(self, other)


 
 def powed_by(self,other):
 			
 			return Number (self.value ** other.value).set_context(self.context), None 
 def get_comparison_eq(self, other):
		if isinstance(other, Number):
			return Number(int(self.value == other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def get_comparison_ne(self, other):
		if isinstance(other, Number):
			return Number(int(self.value != other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def get_comparison_lt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value < other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def get_comparison_gt(self, other):
		if isinstance(other, Number):
			return Number(int(self.value > other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def get_comparison_lte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value <= other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def get_comparison_gte(self, other):
		if isinstance(other, Number):
			return Number(int(self.value >= other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def anded_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value and other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def ored_by(self, other):
		if isinstance(other, Number):
			return Number(int(self.value or other.value)).set_context(self.context), None 
		else:
			return None, Value.illegal_operation(self, other)


 def notted(self):
 	return Number(1 if self.value == 0 else 0).set_context(self.context), None 
 
Number.null=Number (0)
Number.true=Number (1)
Number.false=Number(0)

class String(Value):
	def __init__(self,value):
		super().__init__()
		self.value=value 
	
	def add_to(self,other):
		if isinstance(other,String):
			return String(self.value+other.value).set_context(self.context),None 
		else:
			return None , Value.illegal_operation(self,other) 
			
	def multed_by(self,other):
		if isinstance(other,Number):
			return String(self.value*other.value).set_context(self.context),None 
		else:
			return None , Value.illegal_operation(self,other) 
			
	def is_true(self):
		return len(self.value)>0
		
	def copy(self):
		cp=String(self.value)
		cp.set_pos(self.pos_start,self.pos_end)
		cp.set_context(self.context)
		
		return cp 
	def __str__(self):
		return self.value
				
	def __repr__(self):
		return f"{self.value}"


		



class BaseFunction(Value):
	def __init__(self,name):
		super().__init__()
		self.name = name or "<anonymous>"
		
	def generate_new_context(self):
			
			new_context = Context(self.name, self.context, self.pos_start)
			new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
			return new_context
			
	def check_args(self,arg_names,args):
		res=RTResult ()
		if len(args) > len(arg_names):
			return res.failure(RTError(
				self.p_s, self.p_e,
				f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
				self.context
			))
		
		if len(args) < len(arg_names):
			return res.failure(RTError(
				self.pos_start, self.pos_end,
				f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
				self.context
			))
		return res.success(None)
		
		
	def populate_args(self,arg_names,args,exec_ctx):
		for i in range(len(args)):
			arg_name = arg_names[i]
			arg_value = args[i]
			arg_value.set_context(exec_ctx)
			exec_ctx.symbol_table.set(arg_name, arg_value)
	
	
	def check_and_populate_args(self,arg_names,args,exec_ctx):
		res=RTResult ()
		res.register(self.check_args(arg_names,args))
		if res.error : return res 
		self.populate_args(arg_names,args,exec_ctx)
		return res.success(None)
		

				
				
				

class Function(BaseFunction):
	def __init__(self, name, body_node, arg_names):
		super().__init__(name)
		self.body_node = body_node
		self.arg_names = arg_names
		
		self.p_s=body_node.p_s
		self.p_e=body_node.p_e

	def execute(self, args):
		res = RTResult()
		interpreter = Interpreter()
		exe_context =self.generate_new_context()
		
		res.register(self.check_and_populate_args(self.arg_names,args,exe_context))
		if res.error: return res 


		value = res.register(interpreter.visit(self.body_node, exe_context))
		if res.error: return res
		return res.success(value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names)
		copy.set_context(self.context)
		copy.set_pos(self.p_s, self.p_e)
		return copy

	def __repr__(self):
		return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
 def __init__(self,name):
 	 	
 	super().__init__(name)
 	 	
 def execute(self,args):
 	res=RTResult ()
 	
 	exe_ctx=self.generate_new_context()
 	
 	method_name=f'execute_{self.name}' 	
 	method=getattr(self, method_name,self.no_visit_method)
 	
 	res.register(self.check_and_populate_args(method.arg_names,args,exe_ctx))
 	if res.error: return res 
 	
 	ret_val= res.register(method(exe_ctx))
 	if res.error: return res 
 	
 	return res.success(ret_val)
  	
 def no_visit_method(self,node,ctx):
 	raise Exception ("no method defined "+self.name)

 	
 def copy(self):
		copy = BuiltInFunction(self.name)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy 
			
 def __repr__(self):
		return f"<function {self.name}>"
		
	
 def execute_print(self,exec_ctx):
 	print(str(exec_ctx.symbol_table.get("value")))
 	return RTResult().success(Number.null)
 execute_print.arg_names=["value"]
 
 def execute_print_ret(self,exec_ctx):
 	print()
 	return RTResult().success(String(str(exec_ctx.symbol_table.get("value")))) 
 execute_print_ret.arg_names=["value"]  
 
 def execute_input(self,exe_ctx):
 	text=input ()
 	return RTResult (). success (String(text))
 execute_input.arg_names=[] 
 
 def execute_input_int(self,exe_ctx):
 	text=input ()
 	while True:
 		try:
 			num=int(text)
 			break
 		except ValueError:
 			 print (f'{text} should be an int ')
 		 
 		 
 	
 	return RTResult (). success (Number(num))
 execute_input_int.arg_names=[] 
 

 def execute_clear(self,exe_ctx):
 	os.system("cls" if os.name=='nt' else "clear")
 	return RTResult (). success (Number.null) 	
 execute_clear.arg_names=[]
 
 def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return RTResult().success(Number.true if is_number else Number.false)
 execute_is_number.arg_names = ["value"]

 def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return RTResult().success(Number.true if is_number else Number.false)
 execute_is_string.arg_names = ["value"]
 def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return RTResult().success(Number.true if is_number else Number.false)
 execute_is_list.arg_names = ["value"]

 def execute_is_function(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return RTResult().success(Number.true if is_number else Number.false)
 execute_is_function.arg_names = ["value"]
 
 

 def execute_AddReal(self, exec_ctx):
    list= exec_ctx.symbol_table.get("listO")
    val = exec_ctx.symbol_table.get("val")
    print("her i am motherufkcer values are"+str(list)+""+str(val))

    if not isinstance(list, List):
      return RTResult().failure(RTError(
        self.p_s, self.p_e,
        "First argument must be list",
        exec_ctx
      ))

   

    
    luli = list.elements = list.elements.extend([val])
    
    return RTResult().success(Number.true)
 execute_AddReal.arg_names = ["listO", "val"]
 
 def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    index = exec_ctx.symbol_table.get("index")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.p_s, self.p_e,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(index, Number):
      return RTResult().failure(RTError(
        self.p_s, self.p_e,
        "Second argument must be number",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RTResult().failure(RTError(
        self.p_s, self.p_e,
        'Element at this index could not be removed from list because index is out of bounds',
        exec_ctx
      ))
    return RTResult().success(element)
 execute_pop.arg_names = ["list", "index"]
 def execute_extend(self, exec_ctx):
    listA = exec_ctx.symbol_table.get("listA")
    listB = exec_ctx.symbol_table.get("listB")

    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.p_s, self.p_e,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(listB, List):
      return RTResult().failure(RTError(
        self.p_s, self.p_e,
        "Second argument must be list",
        exec_ctx
      ))

    listA.elements.extend(listB.elements)
    return RTResult().success(Number.null)
 execute_extend.arg_names = ["listA", "listB"]


BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.AddReal      = BuiltInFunction("AddReal")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend   = BuiltInFunction("extend")

 	
 
 
 
 

 #######################################
# RUNTIME RESULT
#######################################

class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

	def register(self, res):
		
			
		if res.error: self.error = res.error
		return res.value

	def success(self, value):
		self.value = value
		return self

	def failure(self, error):
		self.error = error
		return self
 
 
 ###############
#   SYMBOL TABLE #
###############
class SymbolTable:
 def __init__(self, parent=None):
 	self.symbols={}
 	self.parent=parent
 def get(self,name):
 	value=self.symbols.get(name,None)
 	if value==None and self.parent:
 		return self.parent.get(name)
 	return value 
 def set(self,name,value):
 	self.symbols[name]=value 
 def remove(self,name):
 	del self.symbols[name]



#######################################
# CONTEXT
#######################################

class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table=None



 ###############
#   INTERPRETER	 #
###############
class Interpreter:
	def visit(self,node,context):
		method_name=f"visit_{type(node).__name__}"
		method=getattr(self,method_name,self.no_visit_method)
		return method(node,context)
		
		
	def no_visit_method(self,node,context):
		raise Exception (type(node).__name__)
	
	def visit_NumberNode(self,node,context):
		return RTResult().success(Number(node.tok.value).set_pos(node.p_s,node.p_e).set_context(context)) 
	
	def visit_ListNode(self,node, context):
		res=RTResult ()
		
		elements=[]
		
		for element in node.element_nodes:
			elements.append(res.register(self.visit(element, context)))
			if res.error: return res 
		
		return res.success(List(elements).set_context(context).set_pos(node.p_s,node.p_e))
			
			
			
	
	def visit_FuncDefNode(self, node, context):
		res = RTResult()

		func_name = node.var_name_tok.value if node.var_name_tok else None
		body_node = node.body_node
		arg_names = [arg_name.value for arg_name in node.arg_name_toks]
		func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.p_s, node.p_e)
		
		if node.var_name_tok:
			context.symbol_table.set(func_name, func_value)

		return res.success(func_value) 
		
	def visit_StringNode(self,node, context):
		return RTResult (). success (String(node.tok.value).set_context(context).set_pos(node.p_s,node.p_e))
	
	
	def visit_CallNode(self, node, context):
		res = RTResult()
		args = []

		value_to_call = res.register(self.visit(node.node_to_call, context))
		if res.error: return res
		value_to_call = value_to_call.copy().set_pos(node.p_s, node.p_e)

		for arg_node in node.arg_nodes:
			args.append(res.register(self.visit(arg_node, context)))
			if res.error: return res

		return_value = res.register(value_to_call.execute(args))
		if res.error: return res 
		return_value = return_value.copy().set_pos(node.p_s,node.p_e).set_context(context)

		return res.success(return_value)

		
	def visit_ForNode(self,node,context):
		res=RTResult ()
		elements=[]
		
		start_value = res.register(self.visit(node.start_value_node, context))
		if res.error: return res 
		
		end_value = res.register(self.visit(node.end_value_node, context))
		if res.error: return res 
		
		
		if node.step_value_node:
			step_value = res.register(self.visit(node.step_value_node, context))
			if res.error: return res
		else:
			step_value = Number(1)
			
		i = start_value.value

		if step_value.value >= 0:
			condition = lambda: i < end_value.value
		else:
			condition = lambda: i > end_value.value
		
		while condition():
			context.symbol_table.set(node.var_name_tok.value, Number(i))
			i += step_value.value

			elements.append(res.register(self.visit(node.body_node, context)))
			if res.error: return res 
			
		return res.success(List(elements).set_context(context).set_pos(node.p_s,node.p_e))





		
	def visit_WhileNode(self,node, context):
		res=RTResult ()
		elements=[]
		
		
		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.error: return res

			if not condition.is_true(): break

			elements.append(res.register(self.visit(node.body_node, context)))
			if res.error: return res 
			
		return res.success(List(elements).set_context(context).set_pos(node.p_s,node.p_e))



		
		
	def visit_VarAccessNode(self,node,context):
		res=RTResult()
		var_name=node.var_name_tok.value
		value=context.symbol_table.get(var_name)
		if not value :
			return res.failure(RTError (
			node.p_s,
			node.p_e,
			f"variable {var_name}  not defined",
			context			
			))
		value=value.copy().set_pos(node.p_s,node.p_e).set_context(context)
		return res.success(value)
	
	def visit_VarAssignNode(self,node,context):
		res=RTResult ()
		var_name=node.var_name_tok.value
		value=res.register(self.visit(node.value_node,context))
		if res.error : return res 
		context.symbol_table.set(var_name,value)
		return res.success(value)		
		
	def visit_BinOpNode(self,node,context):
		res = RTResult()
		left=res.register(self.visit(node.left_n,context))
		if res.error: return res
		right=res.register(self.visit(node.right_n,context))
		if res.error: return res 
		
		if node.op_tok.type==MIN:
			result,error=left.subbed_by(right)
		elif node.op_tok.type==PLUS:
			result, error=left.added_to(right)
		elif node.op_tok.type==MUL:
			result,error=left.mul_by(right)
		elif node.op_tok.type==POW:
			result,error=left.powed_by(right)
		elif node.op_tok.type==DIV:
			result,error=left.div_by(right) 			
		elif node.op_tok.matches(EE,None):		
			result, error = left.get_comparison_eq(right)
		elif node.op_tok.type == NE:
			result, error = left.get_comparison_ne(right)
		elif node.op_tok.type == LT:
			result, error = left.get_comparison_lt(right)
		elif node.op_tok.type == GT:
			result, error = left.get_comparison_gt(right)
		elif node.op_tok.type == LTE:
			result, error = left.get_comparison_lte(right)
		elif node.op_tok.type == GTE:
			result, error = left.get_comparison_gte(right)
		elif node.op_tok.matches(KEYWORD, 'and'):
			result, error = left.anded_by(right)
		elif node.op_tok.matches(KEYWORD, 'or'):
			result, error = left.ored_by(right)
		if error:
			return res.failure(error)
		return res.success(result.set_pos(node.p_s,node.p_e).set_context(context))
		
	def visit_IfNode(self,node, context):
		res=RTResult ()
		
		for condition, expr in node.cases:
			condition_value=res.register(self.visit(condition, context))
			if res.error: return res 
			
			if condition_value.is_true():
				expr_value=res.register(self.visit(expr, context))
				return res.success(expr_value)
				
		if node.else_case:
				else_value=res.register(self.visit(node.else_case, context))
				if res.error: return res 
				return res.success(else_value)
				
				
		return res.success(None)
				
		
	def visit_UrnaryOpNode(self,node,context):
		res = RTResult()
		number=res.register(self.visit(node.node,context))
		if res.error: return res
		error=None
		if node.op_tok.type==MIN:
			number,error=number.mul_by(Number(-1))
		if error:
			return res.failure(error)
		return res.success(number.set_pos(node.p_s,node.p_e).set_context(context))
		
global_symbol_table=SymbolTable ()
global_symbol_table.set("null",Number.null)
global_symbol_table.set("true",Number.true)
global_symbol_table.set("false",Number.false)		
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_imt", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("isNum", BuiltInFunction.is_number)
global_symbol_table.set("isStr", BuiltInFunction.is_string)
global_symbol_table.set("isList", BuiltInFunction.is_list)
global_symbol_table.set("isFunc", BuiltInFunction.is_function)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("append", BuiltInFunction.AddReal)


###############
#      RUN 			     #
###############

def Run(fn,text):
	#Lexing the program
	lexer=Lexer(fn,text)
	tokens,error=lexer.make_token()
	if error:
		return "Failure in Lexical analysis", error 
	#generating ast 
#	print (tokens)
	parser=Parser(tokens)
	ast=parser.parse()
	if ast.error: return None,ast.error
	#running the program
	interpreter=Interpreter ()
	contexts=Context("<Program>")
	contexts.symbol_table=global_symbol_table
	result=interpreter.visit(ast.node,contexts)
	return result.value, result.error
	