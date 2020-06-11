#!/usr/bin/env Rscript
library(countrycode)
write.csv(codelist[c("gwn","country.name.en","un.region.name","un.regionintermediate.name","un.regionsub.name")],"data/cc.csv",row.names=FALSE)
