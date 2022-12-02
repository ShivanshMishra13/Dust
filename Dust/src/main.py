from DustLib import lexer,parser,interpreter
def Run(fn,fileloca):
	
		
	with open(fileloca,"r") as f:
 			text=f.read()
 	
 		
	

	#Lexing the program

	lexerr=lexer.Lexer(text,fn)
	tokens,error=lexerr.make_token()
	if error:
		return "Failure in Lexical analysis", error 
	#generating ast 
	#print (tokens)
	parserr=parser.Parser(tokens)
	ast=parserr.parse()
	if ast.error: return None,ast.error
	#running the program
	interpreterr=interpreter.Interpreter ()
	contexts=interpreter.Context("<Program>")
	contexts.symbol_table=interpreter.global_symbol_table
	result=interpreterr.visit(ast.node,contexts)
	return result.value, result.error
text=input("Dust >")
Run("<stdin>",text)
	
