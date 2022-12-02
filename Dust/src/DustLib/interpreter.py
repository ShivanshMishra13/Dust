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
	def __init__(self, name, body_node, arg_names,s_r_n):
		super().__init__(name)
		self.s_r_n=s_r_n
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
		return res.success(Number.null if self.s_r_n else value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names,self.s_r_n)
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
 
 def execute_run(self,exec_ctx):
 	fn=exec_ctx.symbol_table.get("fn")
 	fn=fn.value
 	try:
 		with open(fn,"r") as f:
 			script=f.read()
 			
 	except Exception as e :
 		
 		return RTResult().failure(RTError(
        0, 0,
        "cannot read the file :"+str(e),
        exec_ctx
      ))
      
      
 	_,error=Run(fn, script )
 	
 	if error:
 		
 		return RTResult().failure(RTError(
        self.pos_start, self.pos_end,error.in_string()
        ,
        exec_ctx
        
      )) 
 	
 	return RTResult (). success (Number.null)
 execute_run.arg_names=["fn"]
 	
 		
   
     
    
      
 		
 
 	


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
BuiltInFunction.run   = BuiltInFunction("run")


 	
 
 
 
 

 #######################################
# RUNTIME RESULT
#######################################

class RTResult:
	def __init__(self):
		self.reset()
		
		
		
	def reset(self):
	    self.value=None
	    self.error=None
	    self.func_return_value=None
	    self.loop_should_break=None
	    self.loop_should_continue=None
	    

	def register(self, res):
	    self.func_return_value=res.func_return_value
	    self.loop_should_continue=res.loop_should_continue
	    self.loop_should_break=res.loop_should_break
	    if res.error: self.error = res.error
	    return res.value

	def success(self, value):
	    self.reset()
	    self.value = value
	    return self 
	    
	def success_return(self,value):
		self.reset()
		self.func_return_value=value
		return self
		
	def success_continue(self):
		self.reset()
		self.loop_should_continue=True
		return self 
	def success_break(self):
		self.reset()
		self.loop_should_break=True
		return self
		
		
	
	    
    
    
    
    

	def failure(self, error):
	    self.reset()
	    self.error = error
	    return self
	
	def should_return(self):
	    return (
	        self.error or 
	        self.func_return_value or 
	        self.loop_should_break or 
	        self.loop_should_continue 
	        
	        )
 
 
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
	#	print(method)
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
		func_value = Function(func_name, body_node, arg_names,node.s_r_n).set_context(context).set_pos(node.p_s, node.p_e)
		
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
			
		return res.success(Number.null if node.s_r_n else List(elements).set_context(context).set_pos(node.p_s,node.p_e))





		
	def visit_WhileNode(self,node, context):
		res=RTResult ()
		elements=[]
		
		
		while True:
			condition = res.register(self.visit(node.condition_node, context))
			if res.error: return res

			if not condition.is_true(): break

			elements.append(res.register(self.visit(node.body_node, context)))
			if res.error: return res 
			
		return res.success(Number.null if node.s_r_n else List(elements).set_context(context).set_pos(node.p_s,node.p_e))



		
		
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
		
		for condition, expr,srn in node.cases:
			condition_value=res.register(self.visit(condition, context))
			if res.error: return res 
			
			if condition_value.is_true():
				expr_value=res.register(self.visit(expr, context))
				return res.success(Number.null if srn else expr_value )
				
		if node.else_case:
				expr,srn= node.else_case
				
				else_value=res.register(self.visit(expr, context))
				if res.error: return res 
				return res.success(Number.null if srn else else_value)
				
				
		return res.success(Number.null)
				
		
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
		
	def visit_ReturnNode(self,node,context):
		res=RTResult()
		
		if node.node_to_return :
			value=res.register(self.visit(node.node_to_return,context))
			
			if res.should_return():	 
				 return res 
		else:
			value=Number.null
		
		return res.success_return(value)
		
	def visit_ContinueNode(self,node, context ):
		return RTResult().success_continue()
	def visit_BreakNode(self,node,context):
		return RTResult().success_break()
		
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
global_symbol_table.set("run", BuiltInFunction.run)
