###################################
#######  emplikH1.test() ##########
###################################

emplikH1.test <- function(x, d, theta, fun,
	              tola = .Machine$double.eps^.25)
{
n <- length(x)
if( n <= 2 ) stop("Need more observations")
if( length(d) != n ) stop("length of x and d must agree")
if(any((d!=0)&(d!=1))) stop("d must be 0/1's for censor/not-censor")
if(!is.numeric(x)) stop("x must be numeric values --- observed times")

#temp<-summary(survfit(Surv(x,d),se.fit=F,type="fleming",conf.type="none"))
#
newdata <- Wdataclean2(x,d)
temp <- DnR(newdata$value, newdata$dd, newdata$weight)

time <- temp$time         # only uncensored time?  Yes.
risk <- temp$n.risk
jump <- (temp$n.event)/risk

funtime <- fun(time)
funh <- (n/risk) * funtime    # that is Zi
funtimeTjump <- funtime * jump

if(jump[length(jump)] >= 1) funh[length(jump)] <- 0  #for inthaz and weights

inthaz <- function(x, ftj, fh, thet){ sum(ftj/(1 + x * fh)) - thet }

diff <- inthaz(0, funtimeTjump, funh, theta)

if( diff == 0 ) { lam <- 0 } else {
    step <- 0.2/sqrt(n)
    if(abs(diff) > 6*log(n)*step )
    stop("given theta value is too far away from theta0")

    mini<-0
    maxi<-0
    if(diff > 0) {
    maxi <- step
    while(inthaz(maxi, funtimeTjump, funh, theta) > 0 && maxi < 50*log(n)*step)
    maxi <- maxi+step
    }
    else {
    mini <- -step
    while(inthaz(mini, funtimeTjump, funh, theta) < 0 && mini > - 50*log(n)*step)
    mini <- mini - step
    }

    if(inthaz(mini, funtimeTjump, funh, theta)*inthaz(maxi, funtimeTjump, funh, theta) > 0 )
    stop("given theta is too far away from theta0")

    temp2 <- uniroot(inthaz,c(mini,maxi), tol = tola,
                  ftj=funtimeTjump, fh=funh, thet=theta)
    lam <- temp2$root
}

onepluslamh<- 1 + lam * funh   ### this is 1 + lam Zi in Ref.

weights <- jump/onepluslamh  #need to change last jump to 1? NO. see above

loglik <- 2*(sum(log(onepluslamh)) - sum((onepluslamh-1)/onepluslamh) )
#?is that right? YES  see (3.2) in Ref. above. This ALR, or Poisson LR.

#last <- length(jump)    ## to compute loglik2, we need to drop last jump
#if (jump[last] == 1) {
#                     risk1 <- risk[-last]
#                     jump1 <- jump[-last]
#                     weights1 <- weights[-last]
#                     } else {
#                            risk1 <- risk
#                            jump1 <- jump
#                            weights1 <- weights
#                            }
#loglik2 <- 2*( sum(log(onepluslamh)) +
#          sum( (risk1 -1)*log((1-jump1)/(1- weights1) ) )  )
##? this likelihood seems have negative values sometimes???

list( logemlik=loglik,  ### logemlikv2=loglik2,
      lambda=lam, times=time, wts=weights,
      nits=temp2$nf, message=temp2$message )
}

library("graphics")

par(mfrow = c(1, 2))
# plot histogram
x <- rnorm(100)
if (max(x) > 100)
  stop("Quite unexpected.")
else
  hist(x, plot=TRUE, col="ivory")

# from doc: lowess
plot(cars, main = "lowess(cars)")
     lines(lowess(cars), col = 2)
     lines(lowess(cars, f=.2), col = 3)
     legend(5, 120, c(paste("f = ", c("2/3", ".2"))), lty = 1, col = 2:3)

# from doc: is.na
is.na(c(1, NA))

# from doc: Extract
y <- list(1,2,a=4,5)
y[c(3,4)]             # a list containing elements 3 and 4 of y
y$a                   # the element of y named a

# from doc: for
for(n in c(2,5,10,20,50)) {
  x <- stats::rnorm(n)
  cat(n,":", sum(x2),"\n")
}

class(fo <- y ~ x1*x2) # "formula"




