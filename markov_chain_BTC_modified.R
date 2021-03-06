rm(list=ls())

setwd("C:/Users/vince/Desktop/5703_playground")
library(dplyr)
library(infotheo)

#Read in data, BTC trading data has been resampled by various length of data range.
BTC <- read.csv("BTC_data.csv", row.names = "Date")

rownames(BTC) <- strptime(x = as.character(rownames(BTC)), format = "%Y-%m-%d")
#head(BTC)
#tail(BTC)
#plot(BTC$Weighted_Price)

BTC <- data.frame(BTC)
BTC$Close.Date <- row.names(BTC)

temp_set <- c()

for(row_set in seq(10000)){
  row_quant <- sample(10:30,1)
  row_start <- sample(1:(nrow(BTC) - row_quant), 1)
  market_subset <- BTC[row_start:(row_start + row_quant),]
  market_subset <- dplyr::mutate(market_subset, 
                                 Close_Date = max(market_subset$Close.Date),
                                 Close_Gap=(Close - lag(Close))/lag(Close) ,
                                 High_Gap=(High - lag(High))/lag(High) ,
                                 Low_Gap=(Low - lag(Low))/lag(Low),
                                 Volume_Gap=(Volume_BTC - lag(Volume_BTC))/lag(Volume_BTC), # The volume of BTC of last day
                                 Daily_Change=(Close - Open)/Open,
                                 Outcome_Next_Day_Direction= (lead(Volume_BTC)-Volume_BTC)) %>% # How much changed in vol next day
    dplyr::select(-Open, -High, -Low, -Close, -Volume_BTC, -Volume_Currency, -Weighted_Price) %>%
    na.omit
  market_subset$Sequence_ID <- row_set
  temp_set <- rbind(temp_set, market_subset)
}

#dim(temp_set)

# create sequences
# simplify the data by binning values into three groups

# Close_Gap
#range(temp_set$Close_Gap)
data_dicretized <- discretize(temp_set$Close_Gap, disc="equalfreq", nbins=3)
temp_set$Close_Gap <- data_dicretized$X
temp_set$Close_Gap_LMH <- ifelse(temp_set$Close_Gap == 1, 'L', ifelse(temp_set$Close_Gap ==2, 'M','H'))

# Volume_Gap
#range(temp_set$Volume_Gap)
data_dicretized <- discretize(temp_set$Volume_Gap, disc="equalfreq", nbins=3)
temp_set$Volume_Gap <- data_dicretized$X
temp_set$Volume_Gap_LMH <- ifelse(temp_set$Volume_Gap == 1, 'L', ifelse(temp_set$Volume_Gap ==2, 'M','H'))

# Daily_Change
#range(temp_set$Daily_Change)
data_dicretized <- discretize(temp_set$Daily_Change, disc="equalfreq", nbins=3)
temp_set$Daily_Change <- data_dicretized$X
temp_set$Daily_Change_LMH <- ifelse(temp_set$Daily_Change == 1, 'L', ifelse(temp_set$Daily_Change ==2, 'M','H'))


#check point
new_set <- temp_set

# new set, remove cols except for bined cols
new_set <- new_set[,c("Sequence_ID", "Close_Date", "Close_Gap_LMH", "Volume_Gap_LMH", 
                      "Daily_Change_LMH", "Outcome_Next_Day_Direction")]

new_set$Event_Pattern <- paste0(new_set$Close_Gap_LMH,      
                                new_set$Volume_Gap_LMH, 
                                new_set$Daily_Change_LMH) 


# reduce set 
compressed_set <- dplyr::group_by(new_set, Sequence_ID, Close_Date) %>%
                  dplyr::summarize(Event_Pattern = paste(Event_Pattern, collapse = ",")) %>%
                  data.frame

compressed_set <- merge(x=compressed_set,y=new_set[,c(1,6)], by="Sequence_ID")


# use last x days of data for validation
library(dplyr)
compressed_set_validation <- dplyr::filter(compressed_set, Close_Date >= "2017-10-21")
#dim(compressed_set_validation)
compressed_set <- dplyr::filter(compressed_set, Close_Date < "2017-10-21")
#dim(compressed_set)

#drop colse date column
compressed_set <- dplyr::select(compressed_set, -Close_Date)
compressed_set_validation <- dplyr::select(compressed_set_validation, -Close_Date)


# only keep big moves
#summary(compressed_set$Outcome_Next_Day_Direction)
compressed_set <- compressed_set[abs(compressed_set$Outcome_Next_Day_Direction) > 3638.0,]
compressed_set$Outcome_Next_Day_Direction <- ifelse(compressed_set$Outcome_Next_Day_Direction > 0, 1, 0)
#summary(compressed_set$Outcome_Next_Day_Direction)
#dim(compressed_set)
compressed_set_validation$Outcome_Next_Day_Direction <- ifelse(compressed_set_validation$Outcome_Next_Day_Direction > 0, 1, 0)








# create two data sets - won/not won
compressed_set_pos <- dplyr::filter(compressed_set, Outcome_Next_Day_Direction==1) %>% dplyr::select(-Outcome_Next_Day_Direction)
#dim(compressed_set_pos)
compressed_set_neg <- dplyr::filter(compressed_set, Outcome_Next_Day_Direction==0) %>% dplyr::select(-Outcome_Next_Day_Direction)
#dim(compressed_set_neg)


# build the markov transition grid
build_transition_grid <- function(compressed_grid, unique_patterns) {
  grids <- c()
  for (from_event in unique_patterns) {
    #print(from_event)
    
    # how many times 
    for (to_event in unique_patterns) {
      pattern <- paste0(from_event, ',', to_event)
      IDs_matches <- compressed_grid[grep(pattern, compressed_grid$Event_Pattern),]
      if (nrow(IDs_matches) > 0) {
        Event_Pattern <- paste0(IDs_matches$Event_Pattern, collapse = ',', sep='~~')
        found <- gregexpr(pattern = pattern, text = Event_Pattern)[[1]]
        grid <- c(pattern,  length(found))
      } else {
        grid <- c(pattern,  0)
      }
      grids <- rbind(grids, grid)
    }
  }
  
  # create to/from grid
  grid_Df <- data.frame(pairs=grids[,1], counts=grids[,2])
  grid_Df$x <- sapply(strsplit(as.character(grid_Df$pairs), ","), `[`, 1)
  grid_Df$y <- sapply(strsplit(as.character(grid_Df$pairs), ","), `[`, 2)
  head(grids)
  
  all_events_count <- length(unique_patterns)
  transition_matrix = t(matrix(as.numeric(as.character(grid_Df$counts)), ncol=all_events_count, nrow=all_events_count))
  
  transition_dataframe <- data.frame(transition_matrix)
  names(transition_dataframe) <- unique_patterns
  row.names(transition_dataframe) <- unique_patterns
  head(transition_dataframe)
  
  # replace all NaN with zeros
  transition_dataframe[is.na(transition_dataframe)] = 0
  # transition_dataframe <- opp_matrix
  transition_dataframe <- transition_dataframe/rowSums(transition_dataframe) 
  return (transition_dataframe)
}

unique_patterns <- unique(strsplit(x = paste0(compressed_set$Event_Pattern, collapse = ','), split = ',')[[1]])

grid_pos <- build_transition_grid(compressed_set_pos, unique_patterns)
grid_neg <- build_transition_grid(compressed_set_neg, unique_patterns)

# predict on out of sample data
actual = c()
predicted = c()
for (event_id in seq(nrow(compressed_set_validation))) {
  patterns <- strsplit(x = paste0(compressed_set_validation$Event_Pattern[event_id], collapse = ','), split = ',')[[1]]
  pos <- c()
  neg <- c()
  log_odds <- c()
  for (id in seq(length(patterns)-1)) {
    
    # logOdds = log(tp(i,j) / tn(i,j)
    log_value <- log(grid_pos[patterns[id],patterns[id+1]] / grid_neg[patterns[id],patterns[id+1]])
    if (is.na(log_value) || (length(log_value)==0) || (is.nan(log(grid_pos[patterns[id],patterns[id+1]] / grid_neg[patterns[id],patterns[id+1]]))==TRUE)) {
      log_value <- 0.0
    } else if (log_value == -Inf) {
      log_value <- log(0.00001 / grid_neg[patterns[id],patterns[id+1]])
    } else if (log_value == Inf) {
      log_value <- log(grid_pos[patterns[id],patterns[id+1]] / 0.00001)
      
    }
    log_odds <- c(log_odds, log_value)
    
    pos <- c(pos, grid_pos[patterns[id],patterns[id+1]])
    neg <- c(neg, grid_neg[patterns[id],patterns[id+1]])
  }
  #print(paste('outcome:', compressed_set_validation$Outcome_Next_Day_Direction[event_id]))
  #print(sum(pos)/sum(neg))
  #print(sum(log_odds))
  
  actual <- c(actual, compressed_set_validation$Outcome_Next_Day_Direction[event_id])
  predicted <- c(predicted, sum(log_odds))
  
}

library(caret)#confusion matrix to validate model
result <- confusionMatrix(ifelse(predicted>0,1,0), actual)
result 
#print(grid_neg)


library(RColorBrewer)
my_group=as.numeric(as.factor(substr(rownames(as.matrix(grid_neg)), 1 , 1)))
my_col=brewer.pal(9, "Set1")[my_group]
heatmap(as.matrix(grid_neg), Colv = NA, Rowv = NA, scale="column" , RowSideColors=my_col)
heatmap(as.matrix(grid_pos), Colv = NA, Rowv = NA, scale="column" , RowSideColors=my_col)

write.csv(compressed_set,file = 'zigzag_features.csv')
write.csv(grid_pos, file = 'zigzag_grid_pos.csv')
write.csv(grid_neg, file = 'zigzag_grid_neg.csv')







# prediction
#last 20 days pattern for prediction
row_quant <- 20
row_start <- nrow(BTC) - 20
market_subset <- BTC[row_start:(row_start + row_quant),]
#print(market_subset)
market_subset <- dplyr::mutate(market_subset, 
                               Close_Date = max(market_subset$Close.Date),
                               Close_Gap=(Close - lag(Close))/lag(Close) ,
                               High_Gap=(High - lag(High))/lag(High) ,
                               Low_Gap=(Low - lag(Low))/lag(Low),
                               Volume_Gap=(Volume_BTC - lag(Volume_BTC))/lag(Volume_BTC), # The volume of BTC of last day
                               Daily_Change=(Close - Open)/Open,
                               Outcome_Next_Day_Direction= (lead(Volume_BTC)-Volume_BTC)) %>% # How much changed in vol next day
  dplyr::select(-Open, -High, -Low, -Close, -Volume_BTC, -Volume_Currency, -Weighted_Price) %>%
  na.omit#handle of missed data

#Close_Gap
data_dicretized <- discretize(market_subset$Close_Gap, disc="equalfreq", nbins=3)
market_subset$Close_Gap <- data_dicretized$X
market_subset$Close_Gap_LMH <- ifelse(market_subset$Close_Gap == 1, 'L', ifelse(market_subset$Close_Gap ==2, 'M','H'))

# Volume_Gap
data_dicretized <- discretize(market_subset$Volume_Gap, disc="equalfreq", nbins=3)
market_subset$Volume_Gap <- data_dicretized$X
market_subset$Volume_Gap_LMH <- ifelse(market_subset$Volume_Gap == 1, 'L', ifelse(market_subset$Volume_Gap ==2, 'M','H'))

# Daily_Change
data_dicretized <- discretize(market_subset$Daily_Change, disc="equalfreq", nbins=3)
market_subset$Daily_Change <- data_dicretized$X
market_subset$Daily_Change_LMH <- ifelse(market_subset$Daily_Change == 1, 'L', ifelse(market_subset$Daily_Change ==2, 'M','H'))

market_subset <- market_subset[,c("Close_Gap_LMH", "Volume_Gap_LMH", 
                                  "Daily_Change_LMH", "Outcome_Next_Day_Direction")]

market_subset$Event_Pattern <- paste0(market_subset$Close_Gap_LMH,      
                                      market_subset$Volume_Gap_LMH, 
                                      market_subset$Daily_Change_LMH) 

market_subset <- market_subset[,c("Event_Pattern","Outcome_Next_Day_Direction")]
market_subset <- market_subset[abs(market_subset$Outcome_Next_Day_Direction) > 1638.0,]
patterns <- market_subset$Event_Pattern
window <- length(patterns)

for(i in seq(10)){
  if(market_subset$Outcome_Next_Day_Direction[length(market_subset$Outcome_Next_Day_Direction)] > 0){
    a <- grid_pos[tail(patterns, n = 1)]
    pattern <- colnames(grid_pos)[which(a == max(a))]
  }else{
    a <- grid_neg[tail(patterns, n = 1)]
    pattern <- colnames(grid_neg)[which(a == max(a))]
  }
  patterns <- c(patterns, pattern)
}




predicting = c()

for (event_id in seq(10)) {
  start <- length(patterns)-10-(10-event_id)
  pat <- patterns[start:(length(patterns)-(10-event_id))]
  pos <- c()
  neg <- c()
  log_odds <- c()
  for (id in length(pat)-1) {
    
    log_value <- log(grid_pos[pat[id],pat[id+1]] / grid_neg[pat[id],pat[id+1]])
    if (is.na(log_value) || (length(log_value)==0) || (is.nan(log(grid_pos[pat[id],pat[id+1]] / grid_neg[pat[id],pat[id+1]]))==TRUE)) {
      log_value <- 0.0
    } else if (log_value == -Inf) {
      log_value <- log(0.00001 / grid_neg[pat[id],pat[id+1]])
    } else if (log_value == Inf) {
      log_value <- log(grid_pos[pat[id],pat[id+1]] / 0.00001)
      
    }
    log_odds <- c(log_odds, log_value)
    
    pos <- c(pos, grid_pos[pat[id],pat[id+1]])
    neg <- c(neg, grid_neg[pat[id],pat[id+1]])
  }
  predicting <- c(predicting, sum(log_odds))
}
write.csv(predicting, file = 'zigzag_predicted.csv')

print(result)