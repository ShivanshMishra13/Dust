from DustBK import Run

while True:
	text= input("Dust > ")	
	result,error=Run(text,"<stdin>") 
	if error: print(error.in_string()) 
	else: print(result)
