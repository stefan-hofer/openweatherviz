import pandas as pd

# Data downloaded from https://klimaservicesenter.no/observations/

df = pd.read_csv('table.csv', delimiter=';', nrows=27760)

df['Date'] = pd.to_datetime(df['Tid(norsk normaltid)'], format='%d.%m.%Y')
df = df.sort_values(by='Date')

df = df.set_index('Date')


df = (df[['Homogenisert middeltemperatur (døgn)', 'Snødybde',
          'Minimumstemperatur (døgn)', 'Middeltemperatur (døgn)']]
      .replace(',', '.', regex=True).replace('-', np.NaN).astype(float))

(df['Snødybde'] > 0.0).resample('AS').sum().plot(alpha=0.5)
(df['Snødybde'] > 0.0).resample('AS').sum().plot.hist(alpha=0.5)
