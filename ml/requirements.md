## Input
1. We will get the stock market data (OHLCV Daily)

## Expectation
1. How much high it can go in terms of percentage
2. How much low it can go in terms of percentage


## Steps
1. Acquire the data
2. Clean up data (missing data, remove noise, remove unncessary columns)
3. Make adjustments (like splits, dividends)

## Create features
Bollinger Bands
Moving Average - 7
Moving Average - 20
Moving Average - 50

## Define label (targets)
High% = (today high - Yesterdays closing price) / yesterday closing price
Low% = (today Low - Yesterdays closing price) / yesterday closing price

Ex. If ycp = 200, High=205, low 198. High%= (205-200)/200 = 2.5%, low%=(198-200)/200 = -1%

# Build the Model
## Training Data, Testing data (split)
## Train the model
## accuracy (parameter)
## How to improve?
## Regularization
## Release the model - for the production

