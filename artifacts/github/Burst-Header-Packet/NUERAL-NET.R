library(neuralnet)
cd=read.csv("~/final_ml.csv")
View(cd)
str(cd)
samplesize = 0.60 *nrow(cd)
set.seed(80)
index =sample(seq_len(nrow(cd)), size= samplesize)
trainset=cd[index,]
testset = cd[-index , ]
set.seed(2)
nn=neuralnet(nb_no_block+nb_wait+no_block+block~.,trainset,hidden =100)
plot(nn)
mypredict=compute(nn,testset)$net.result
maxidx <- function(arr)
  return(which(arr == max(arr)))
idx <- apply(mypredict, c(1), maxidx)

prediction <- c('1', '3', '2','4')[idx]
table(prediction,testset$V22)

