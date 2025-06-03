calc<-function(s,t){
  return(s+t)
}
calc(20,12)


say_name<-function(fname){
  paste("my name is ",fname)
  
}
say_name("james")



Result<-function(c,d){
  f<-c+d
  return(f)
}

Result(Result(3,5),Result(9,2))



#write a functin within a function 

Add<-function(x){
  Multiply<-function(y){
    d<-x*y
    return((d))
  }
  return(Multiply)
  
}
func_call<-Add(20)
func_call(12)




Outer_func <- function(x) {
  Inner_func <- function(y) {
    a <- x + y
    return(a)
  }
  return (Inner_func)
}
output <- Outer_func(3) # To call the Outer_func
output(5)





tri_recursion <- function(k) {
  if (k > 0) {
    result <- k + tri_recursion(k - 1)
    print(result)
  } else {
    result = 0
    return(result)
  }
}

tri_recursion(6)


#global variable
txt <- "awesome"
my_function <- function() {
  paste("R is", txt)
}

my_function()


#global and local variable

txt <- "global variable"
my_function <- function() {
  txt = "fantastic"
  paste("R is", txt)
}

my_function()

txt 



#using global assignment operator
my_function <- function() {
  txt <<- "fantastic"
  paste("R is", txt)
}

my_function()

print(txt)



#uing te global assignment peraor in side a fxn

txt <- "awesome"
my_function <- function() {
  txt <<- "fantastic"
  paste("R is", txt)
}

my_function()

paste("R is", txt)







