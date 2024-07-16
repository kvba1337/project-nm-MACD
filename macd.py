import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Calculate Exponential Moving Average (EMA)
def calculate_ema(data, N):
    alpha = 2 / (N + 1)
    ema_values = [data[0]]

    denominator = 0
    for i in range(N):
        denominator += (1 - alpha) ** i

    for i in range(1, len(data)):
        numerator = 0
        for j in range(i, max(-1, i - N), -1):
            numerator += ((1 - alpha) ** (i - j)) * data[j]
        ema = numerator / denominator
        ema_values.append(ema)
    
    return ema_values

# Algorithm for MACD strategy
def macd_strategy(data):
    capital = 1000
    shares = 0
    portfolio_value = pd.Series(index=data.index, dtype='float64')
    
    for i in range(data.index[0], data.index[-1] + 1):
        if data['Buy_Signal'][i]:
            for j in range(i, data.index[-1] + 1):
                if data['Sell_Signal'][j]:
                    shares += capital / data['Zamkniecie'][i]
                    capital = 0
                    print(f"Kupno akcji w dniu: {data['Data'][i]}, kapital: {capital}, liczba akcji: {shares}")
                    break
                
        elif data['Sell_Signal'][i] and shares > 0:
            capital += shares * data['Zamkniecie'][i]
            shares = 0
            print(f"Sprzedaz akcji w dniu: {data['Data'][i]}, kapital: {capital}, liczba akcji: {shares}")

        portfolio_value[i] = capital + shares * data['Zamkniecie'][i]

    return capital, portfolio_value

# Algorithm for no MACD strategy
def no_macd_strategy(data):
    capital = 1000
    shares = 0
    portfolio_value = pd.Series(index=data.index, dtype='float64')

    shares = capital / data['Zamkniecie'][data.index[0]]

    for i in range(data.index[0], data.index[-1] + 1):
        portfolio_value[i] = shares * data['Zamkniecie'][i]

    return portfolio_value



data = pd.read_csv('tsla_us.csv')
data['Data'] = pd.to_datetime(data['Data'])

# Calculate 12-day and 26-day Exponential Moving Average (EMA)
short_ema = calculate_ema(data['Zamkniecie'], N=12)
long_ema = calculate_ema(data['Zamkniecie'], N=26)

# Calculate MACD line for 12-day and 26-day EMA
macd_line = np.array(short_ema) - np.array(long_ema)

# Calculate 9-day Exponential Moving Average (EMA) for MACD line
signal_line = calculate_ema(macd_line, N=9)

# Calculate difference between MACD line and signal line for histogram
histogram = macd_line - signal_line

# Add new columns to the data
data['MACD'] = macd_line
data['SIGNAL'] = signal_line

# Add detection of buy and sell signals to the data
data['Buy_Signal'] = (data['MACD'] > data['SIGNAL']) & (data['MACD'].shift(1) < data['SIGNAL'].shift(1))
data['Sell_Signal'] = (data['MACD'] < data['SIGNAL']) & (data['MACD'].shift(1) > data['SIGNAL'].shift(1))

# Plot of the closing price of Tesla Inc stock
plt.figure(figsize=(12, 12))
plt.subplot(2, 1, 1)
plt.plot(data['Data'], data['Zamkniecie'], label='Zamkniecie')
plt.title('Wykres ceny akcji Tesla Inc podczas Zamkniecia')
plt.xlabel('Data')
plt.ylabel('Wartosc zamkniecia ($)')
plt.legend()

# Plot of MACD and SIGNAL lines with buy and sell signals
plt.subplot(2, 1, 2)
plt.plot(data['Data'], macd_line, label='MACD', color='blue')
plt.plot(data['Data'], signal_line, label='SIGNAL', color='red')
#plt.bar(data['Data'], histogram, label='Histogram', color='gray')
plt.scatter(data['Data'][data['Buy_Signal']], data['MACD'][data['Buy_Signal']], label='Buy', marker='s', color='green', facecolors='none', linewidth=2)
plt.scatter(data['Data'][data['Sell_Signal']], data['MACD'][data['Sell_Signal']], label='Sell', marker='s', color='red', facecolors='none', linewidth=2)
plt.title('Wykres MACD i SIGNAL')
plt.legend()
plt.subplots_adjust(hspace=0.5)
plt.show()

# First period
start_date_1 = '2022-01-01'
end_date_1 = '2023-01-01'

# Second period
start_date_2 = '2023-01-01'
end_date_2 = '2024-01-01'

# Data selection for the first period
data_period_1 = data[(data['Data'] >= start_date_1) & (data['Data'] <= end_date_1)]

# Data selection for the second period
data_period_2 = data[(data['Data'] >= start_date_2) & (data['Data'] <= end_date_2)]

# Results for the first period
portfolio_no_macd = no_macd_strategy(data_period_1)
result_period_1, portfolio_with_macd = macd_strategy(data_period_1)
print("Wynik koncowy (Okres 1):", result_period_1)

# First plot for the first period
plt.figure(figsize=(12, 18))
plt.subplot(3, 1, 1)
plt.plot(data_period_1['Data'], data_period_1['Zamkniecie'], label='Zamkniecie')
plt.title('Wykres ceny akcji Tesla Inc podczas Zamkniecia (Okres 1)')
plt.xlabel('Data')
plt.ylabel('Wartosc zamkniecia ($)')
plt.legend()

# Second plot for the first period
plt.subplot(3, 1, 2)
plt.plot(data_period_1['Data'], data_period_1['MACD'], label='MACD', color='blue')
plt.plot(data_period_1['Data'], data_period_1['SIGNAL'], label='SIGNAL', color='red')
plt.scatter(data_period_1['Data'][data_period_1['Buy_Signal']], data_period_1['MACD'][data_period_1['Buy_Signal']], label='Buy', marker='s', color='green', facecolors='none', linewidth=2)
plt.scatter(data_period_1['Data'][data_period_1['Sell_Signal']], data_period_1['MACD'][data_period_1['Sell_Signal']], label='Sell', marker='s', color='red', facecolors='none', linewidth=2)
plt.title('Wykres MACD i SIGNAL (Okres 1)')
plt.legend()

# Third plot for the first period
plt.subplot(3, 1, 3)
plt.plot(data_period_1['Data'], portfolio_no_macd, label='kup i zapomnij', color='black')
plt.plot(data_period_1['Data'], portfolio_with_macd, label='z MACD', color='purple')
plt.title('Stan portfela z i bez uzycia MACD (Okres 1)')
plt.xlabel('Data')
plt.ylabel('Wartosc portfela ($)')
plt.legend()
plt.text(0, -0.2, f'Wynik koncowy algorytmu (Okres 1): {round(result_period_1, 2)} $', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
plt.subplots_adjust(hspace=0.5)
plt.show()

# Results for the second period
portfolio_no_macd = no_macd_strategy(data_period_2)
result_period_2, portfolio_with_macd = macd_strategy(data_period_2)
print("Wynik koncowy (Okres 2):", result_period_2)

# First plot for the second period
plt.figure(figsize=(12, 18))
plt.subplot(3, 1, 1)
plt.plot(data_period_2['Data'], data_period_2['Zamkniecie'], label='Zamkniecie')
plt.title('Wykres ceny akcji Tesla Inc podczas Zamkniecia (Okres 2)')
plt.xlabel('Data')
plt.ylabel('Wartosc zamkniecia ($)')
plt.legend()

# Second plot for the second period
plt.subplot(3, 1, 2)
plt.plot(data_period_2['Data'], data_period_2['MACD'], label='MACD', color='blue')
plt.plot(data_period_2['Data'], data_period_2['SIGNAL'], label='SIGNAL', color='red')
plt.scatter(data_period_2['Data'][data_period_2['Buy_Signal']], data_period_2['MACD'][data_period_2['Buy_Signal']], label='Buy', marker='s', color='green', facecolors='none', linewidth=2)
plt.scatter(data_period_2['Data'][data_period_2['Sell_Signal']], data_period_2['MACD'][data_period_2['Sell_Signal']], label='Sell', marker='s', color='red', facecolors='none', linewidth=2)
plt.title('Wykres MACD i SIGNAL (Okres 2)')
plt.legend()

# Third plot for the second period
plt.subplot(3, 1, 3)
plt.plot(data_period_2['Data'], portfolio_no_macd, label='kup i zapomnij', color='black')
plt.plot(data_period_2['Data'], portfolio_with_macd, label='z MACD', color='purple')
plt.title('Stan portfela z i bez uzycia MACD (Okres 2)')
plt.xlabel('Data')
plt.ylabel('Wartosc portfela ($)')
plt.legend()
plt.text(0, -0.2, f'Wynik koncowy algorytmu (Okres 2): {round(result_period_2, 2)} $', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
plt.subplots_adjust(hspace=0.5)
plt.show()