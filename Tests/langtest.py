from Dust import Run

while True:
	text= input("Dust > ")
	if text.strip()=="": continue	
	result,error=Run(text,"<stdin>") 
	if error: print(error.in_string()) 
	elif result:
	    if len(result.elements)==1:
	        print(result.elements[0]) 
	    else: print(result)
#. "Hello World"
#func a(x,y)->x+y
#var s=[8]
#add([69],82)
#ttbnc([8,9,6],7)
#var s= if 5==5 then "laude" else "fuck"
#if 5==5 then; print("fuck boi");print("noob bitch ") else print("wtf")
# func sub(x,y);print("subrtracting");print("noob") ;end 
#for i=0 to 10 then ; print(i);print("bitch") end
#while i<10 then ; print("bicth");print(i) end 