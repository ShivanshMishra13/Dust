from DustBK import Run

while True:
	text= input("Dust > ")	
	result,error=Run(text,"<stdin>") 
	if error: print(error.in_string()) 
	else: print(result)
#. "Hello World"
#func a(x,y)->x+y
#var s=[8]
#append([69],82)()