from pandas import read_csv      
df = read_csv('Gift_Cards.csv', header= None, names= ['item','user','rating','timestamp'])
df.to_csv('Gift_Cards_2.csv', index= False)
