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
 			self.p_e=(self.else_case or self.cases[len(self.cases)-1])[0].p_e
 			
class ForNode:
 		def __init__(self,var_name_tok,start_value_node,end_value_node,step_value_node,body_node,s_r_n):
 			self.var_name_tok=var_name_tok
 			self.start_value_node=start_value_node
 			self.end_value_node=end_value_node
 			self.step_value_node=step_value_node
 			self.body_node=body_node
 			
 			self.p_s=self.var_name_tok.p_s
 			self.p_e=self.body_node.p_e
 			self.s_r_n=s_r_n	
 			
 			
 			
class WhileNode:
 	def __init__(self, condition_node,body_node,s_r_n):
 	 self.condition_node=condition_node
 	 self.body_node=body_node
 	 
 	 self.p_s=self.condition_node.p_s
 	 self.p_e=self.body_node.p_e
 	 self.s_r_n=s_r_n	
 			
 		
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
		def __init__(self,var_name_tok,arg_name_toks,body_node,s_r_n):
			
			self.var_name_tok = var_name_tok
			self.arg_name_toks = arg_name_toks
			self.body_node = body_node
			self.s_r_n=s_r_n	
		
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
class ReturnNode:
    def __init__(self,node_to_return,p_s,p_e):
        self.node_to_return=node_to_return
        self.p_e=p_e
        self.p_s=p_s
        
class BreakNode:
    def __init__(self,p_s,
    p_e):
        self.p_e=p_e
        self.p_s=p_s

class ContinueNode:
    def __init__(self,p_s,p_e):
        self.p_e=p_e
        self.p_s=p_s
    
				
		
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
 		self.rv_c=0

 		
 	def register_advance(self):
 		self.advance_count+=1
 		
 	def try_register(self,res):
 	    if res.error:
 	        self.rv_c=self.advance_count
 	        return None
 	    return self.register(res)
	
 	
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
 		self.update_tok()
 		return self.curr_tok 
 	def reverse(self,cd=1):
 	    self.tok_idx-=cd
 	    self.update_tok()
 	    return self.curr_tok 
 
 		
 	def update_tok(self):
 		if self.tok_idx<len(self.tokens):
 			self.curr_tok=self.tokens[self.tok_idx]
 		
 	
 		
 		
 		
 		
 	def parse(self):
 		res=self.statements()
 		
 		if not res.error and self.curr_tok.type!=EOF:
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected + - * / "))
 	
 		return res 
 		
 	def if_expr(self):
 		res=ParseResult()
 		all_cases=res.register(self.if_expr_cases('if'))
 		if res.error:return res 
 		cases,else_cases=all_cases
 		return res.success(IfNode(cases,else_cases))
 		
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
 		
 		if not  self.curr_tok.type==ARROW:
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
 			
 		if not self.curr_tok.type==LBRAC:
 			 return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting to keyword"))
 			
 		res.register_advance()
 		self.advance()
 		
 		
 		if self.curr_tok.type==NEWL:
 		    res.register_advance()
 		    self.advance()
 		    
 		    body= res.register(self.statements())
 		    if res.error : return res
 		    self.advance()
 		    self.advance()
 		    self.advance()
 		    print(self.curr_tok.type)
 		    
 		    if not self.curr_tok.type==RBRAC:
 		        return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,'Expexted "end" keyword '))
 		        
 		    res.register_advance()
 		    self.advance()
 		    return res.success(ForNode(var_name, start_value, end_value, step_value, body,True))
 		
 		
 		body = res.register(self.statement())
 		if res.error: return res 
 		
 		
 		return res.success(ForNode(var_name, start_value, end_value, step_value, body,False))
 		
 	def if_expr_b(self):
 	    return self.if_expr_cases('elif')
 	
 	def if_expr_c(self):
 	    res = ParseResult()
 	    else_case = None
 	    #self.curr_tok=self.tokens[self.tok_idx-1]
 	    print("else"+self.curr_tok.type)
 	    if self.curr_tok.matches(KEYWORD,'else'):
 	        res.register_advance()
 	        self.advance()
 	        if self.curr_tok.type!=LBRAC:
 	            return res.faliure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,'Expected end keyword after the if expression'))
 	        self.advance()
 	        
 	        if self.curr_tok.type==NEWL:
 	            res.register_advance()
 	            self.advance()
 	            statements= res.register(self.statements())
 	            if res.error: return res 
 	            else_case=(statements,True)
 	           
 	            self.advance()
 	            self.advance()
 	            self.advance()
 	            print("else last"+self.curr_tok.type)
 	            if self.curr_tok.type==RBRAC:
 	                res.register_advance()
 	                self.advance()
 	            else:
 	                return res.faliure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,'Expected end keyword after the if expression'))
 	        else:
 	            expr=res.register(self.statement())
 	            if res.error: return res
 	            else_case=(expr,False)
 	        
 	        
 	    return res.success(else_case)
 	
 	    
 	    
 	    
 	def if_expr_b_or_c(self):
 	    res=ParseResult()
 	    cases,else_cases=[],None
 	    if self.curr_tok.matches(KEYWORD,'elif'):
 	        all_cases= res.register(self.if_expr_b())
 	        if res.error: return res 
 	        cases,else_cases=all_cases 
 	    else:
 	        else_cases=res.register(self.if_expr_c())
 	        if res.error: return res 
 	        
 	    
 	    return res.success((cases,else_cases))
 	    
 	
 	
 		
 	def if_expr_cases(self,c_k):
 		res=ParseResult ()
 		cases=[]
 		else_case=None 
 		if not self.curr_tok.matches(KEYWORD,c_k):
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"expected  "+c_k))
 		res.register_advance()
 		self.advance()
 		condition=res.register(self.expr())
 		if res.error: return res 
 		if not self.curr_tok.type==LBRAC:
 			return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"expected then "))
 		res.register_advance()
 		self.advance()
 		
 		if self.curr_tok.type==NEWL:
 		    res.register_advance()
 		    self.advance()
 		    
 		    statements=res.register(self.statements())
 		    if res.error: return res 
 		    cases.append((condition,statements,True))
 		    self.advance()
 		    self.advance()
 		    self.advance()
 		    if self.curr_tok.type==RBRAC:
 		        res.register_advance()
 		        self.advance()
 		    else:
 		        print("if "+self.curr_tok.type)
 		        all_cases=res.register(self.if_expr_b_or_c())
 		        if res.error:return res
 		        new_cases, else_case = all_cases
 		        cases.extend(new_cases)
 		else:
 		    expr=res.register(self.statement())
 		    if res.error:return res 
 		    cases.append((condition,expr,False))
 		    all_cases=res.register(self.if_expr_b_or_c())
 		    if res.error: return res 
 		    n_cases,else_case=all_cases
 		    cases.extend(n_cases)
 		return res.success((cases,else_case))
 		
 		
 	    
 	 
 		
 		
 		
 		
 	def while_expr(self):
 		res=ParseResult () 		
 		
 		if not self.curr_tok.matches(KEYWORD,"while"):
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting while keyword"))
 		res.register_advance()
 		self.advance()
 		
 		condition=res.register(self.expr())
 		if res.error: return res 
 		
 		if not self.curr_tok.type==LBRAC:
 			return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,"Expecting then keyword"))
 			
 		res.register_advance()
 		self.advance()
 		
 		if self.curr_tok.type==NEWL:
 		    res.register_advance()
 		    self.advance()
 		    
 		    body= res.register(self.statements())
 		    if res.error : return res
 		    
 		    self.advance()
 		    self.advance()
 		    self.advance()
 		    print(self.curr_tok.type)
 		    
 		    
 		    if not self.curr_tok.type==RBRAC:
 		        return res.failure(InvalidSyntax(self.curr_tok.p_s,self.curr_tok.p_e,'Expexted "end" keyword '))
 		    res.register_advance()
 		    self.advance()
 		    return res.success(WhileNode(condition,body,True))
 		
 		body=res.register(self.statement())
 		if res.error: return res 
 		
 		return res.success(WhileNode(condition,body,False))
 	
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
 				return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected ("))
 		else:
 				
 				var_name_tok=None 
 				if self.curr_tok.type!=LPAR:
 					
 					return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected )"))
 					
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
 		
 		if self.curr_tok.type==ARROW:
 			res.register_advance()
 			self.advance()
 			node_to_return=res.register(self.expr())
 			if res.error: return res 
 			return res.success(FuncDefNode(
			var_name_tok,
			arg_name_toks,
			node_to_return,False
		))
 			
 		if self.curr_tok.type!=LBRAC:
 		    return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected -> or newline after func def "))
 		res.register_advance()
 		self.advance()
 		self.advance()
 		
 		node_to_return= res.register(self.statements())
 		
 		if res.error: return res 
 		self.advance()
 		self.advance()
 		self.advance()
 		print(self.curr_tok.type)
 		if not self.curr_tok.type==RBRAC:
 		   return res.failure(InvalidSyntax (self.curr_tok.p_s,self.curr_tok.p_e,"Expected end keyword after func definition "))
 		res.register_advance()
 		self.advance()
 		
 		return res.success(FuncDefNode(
			var_name_tok,
			arg_name_toks,
			node_to_return,True
		))
 

 	        
 		


 		

 	def list_expr(self):
 		res=ParseResult ()
 		
 		element_nodes=[]
 		p_s=self.curr_tok.p_s.copy()
 		
 		tok=self.curr_tok 
 		
 		if tok.type!=LSQR:
 			
 			return res.failure(InvalidSyntaxError(tok.p_s,tok.p_e,"expected ["))
 			
 		res.register_advance()
 		self.advance()
 		
 		if tok.type==RSQR:
 			
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
 	def statements(self):
 	    res=ParseResult()
 	    statements=[]
 	    p_s=self.curr_tok.p_s.copy()
 	    
 	    while self.curr_tok.type==NEWL:
 	        res.register_advance()
 	        self.advance()
 	    statement=res.register(self.statement())
 	    if res.error:return res 
 	    statements.append(statement)
 	    
 	    m_stat=True
 	    
 	    while True:
 	        n_c=0
 	        while self.curr_tok.type==NEWL and self.tokens[self.tok_idx+1]!=RBRAC:
 	            res.register_advance()
 	            self.advance()
 	            n_c+=1
 	        if n_c==0:
 	            m_stat=False
 	            
 	        if not m_stat: break
 	        statement=res.try_register(self.statement())
 	        if not statement:
 	            self.reverse(res.rv_c)
 	            m_stat=False
 	            continue
 	        statements.append(statement)
 	    return res.success(ListNode(
 	    statements,
 	    p_s,
 	    self.curr_tok.p_e.copy()
 	    
 	    ))
 	    
 	def statement(self):
 	    res=ParseResult()
 	    p_s=self.curr_tok.p_s.copy()
 	    
 	    if self.curr_tok.matches(KEYWORD,"return"):
 	        res.register_advance()
 	        self.advance()
 	        
 	        expr= res.try_register(self.expr())
 	        if not expr:
 	            self.reverse(res.to_reverse_count)
 	        return res.success(ReturnNode(expr,p_s,self.curr_tok.p_s.copy()))
 	    if self.curr_tok.matches(KEYWORD,"continue"):
 	        res.register_advance()
 	        self.advance()
 	        return res.success(ContinueNode(p_s,self.curr_tok.p_s.copy()))
 	        
 	    if self.curr_tok.matches(KEYWORD,"break"):
 	        res.register_advance()
 	        self.advance()
 	        
 	        return res.success(BreakNode(p_s,self.curr_tok.p_s.copy()))
 	        
 	        
 	    expr=res.register(self.expr())
 	    
 	    return res.success(expr)
 		



 		
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