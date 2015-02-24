# Run an ANOVA with Rank and Sex as factors on all cases
sexsalary <-read.csv("sexsalary.txt")
anova(lm(TotalCompensation ~ Sex * Rank, sexsalary))

# Split data by Rank and run t-tests to see if there's a sex differnce at each rank
sexsalary_byrank <-split(sexsalary,sexsalary$Rank)

t(sapply(sexsalary_byrank,function(x) unlist(t.test(x$TotalCompensation ~x$Sex)[c("p.value", "statistic")])))

# Split file by schools
sexsalary_byuni <- split(sexsalary,sexsalary$University)

# Run an ANOVA with Rank and Sex as factors for each school
lapply(sexsalary_byuni, function(x) anova(lm(x$TotalCompensation ~ x$Sex * x$Rank, x)))

# Run followup t-test for each school by rank
# Run t-test between men and women by school
t(sapply(sexsalary_byuni,function(x) unlist(t.test(x$TotalCompensation ~x$Sex)[c("p.value", "statistic")])))
